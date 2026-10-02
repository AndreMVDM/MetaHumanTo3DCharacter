"""Inspect FBX 7400 hierarchy without importing or changing source files."""

from __future__ import annotations

import csv
import json
import struct
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent


def read_property(data: bytes, pos: int):
    kind = chr(data[pos]); pos += 1
    fixed = {"Y": "h", "C": "?", "I": "i", "F": "f", "D": "d", "L": "q"}
    if kind in fixed:
        fmt = "<" + fixed[kind]
        return struct.unpack_from(fmt, data, pos)[0], pos + struct.calcsize(fmt)
    if kind in "SR":
        length = struct.unpack_from("<I", data, pos)[0]; pos += 4
        raw = data[pos:pos + length]; pos += length
        return (raw.decode("utf-8", "replace") if kind == "S" else {"bytes": length}), pos
    if kind in "fdlibc":
        count, encoding, length = struct.unpack_from("<III", data, pos); pos += 12
        # Arrays are not needed for hierarchy inspection.
        return {"count": count, "encoding": encoding, "bytes": length}, pos + length
    raise ValueError(f"Unknown FBX property {kind!r} at {pos - 1}")


def read_nodes(data: bytes, pos: int, limit: int):
    nodes = []
    while pos + 13 <= limit:
        end, count, prop_len, name_len = struct.unpack_from("<IIIB", data, pos)
        if end == 0:
            break
        start = pos + 13
        name = data[start:start + name_len].decode("utf-8", "replace")
        cursor = start + name_len
        props = []
        for _ in range(count):
            value, cursor = read_property(data, cursor)
            props.append(value)
        children, _ = read_nodes(data, cursor, end - 13) if cursor < end - 13 else ([], cursor)
        nodes.append({"name": name, "props": props, "children": children})
        pos = end
    return nodes, pos


def child(node, name):
    return [item for item in node["children"] if item["name"] == name]


def inspect(data: bytes):
    assert data.startswith(b"Kaydara FBX Binary"), "Not a binary FBX"
    version = struct.unpack_from("<I", data, 23)[0]
    assert version < 7500, "This reader handles FBX 7400 node headers"
    nodes, _ = read_nodes(data, 27, len(data))
    root = {item["name"]: item for item in nodes}
    objects = root["Objects"]["children"]
    models = {}
    model_types = {}
    for item in objects:
        if item["name"] != "Model":
            continue
        ident, raw_name, kind = item["props"][:3]
        raw_name = str(raw_name).split("\x00", 1)[0]
        properties = {}
        for group in child(item, "Properties70"):
            for prop in child(group, "P"):
                if len(prop["props"]) >= 5:
                    properties[prop["props"][0]] = prop["props"][4:]
        models[ident] = {"id": ident, "name": raw_name.removeprefix("Model::"), "kind": kind,
                         "translation": properties.get("Lcl Translation"),
                         "rotation": properties.get("Lcl Rotation"),
                         "scaling": properties.get("Lcl Scaling"), "parent": None}
        model_types[kind] = model_types.get(kind, 0) + 1
    for connection in child(root["Connections"], "C"):
        props = connection["props"]
        if len(props) >= 3 and props[0] == "OO" and props[1] in models and props[2] in models:
            models[props[1]]["parent"] = props[2]
    for item in models.values():
        item["parent"] = models[item["parent"]]["name"] if item["parent"] in models else None
    bones = [item for item in models.values() if item["kind"] in ("LimbNode", "Root")]
    return {"fbx_version": version, "model_types": model_types,
            "bone_count": len(bones), "bones": bones,
            "animation_stacks": [item["props"][1] for item in objects if item["name"] == "AnimationStack"],
            "animation_curves": sum(item["name"] == "AnimationCurve" for item in objects),
            "materials": [str(item["props"][1]).split("\x00", 1)[0] for item in objects if item["name"] == "Material"],
            "textures": [str(item["props"][1]).split("\x00", 1)[0] for item in objects if item["name"] == "Texture"],
            "videos": [str(item["props"][1]).split("\x00", 1)[0] for item in objects if item["name"] == "Video"]}


def main():
    inventory = []
    reports = {}
    for label, zip_name in (("UE5", "Lara_Rigged_UE5.zip"), ("Mixamo", "Lara_Rigged_Mixamo.zip")):
        dest = WORK / label
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(ROOT / "Characters" / zip_name) as archive:
            for entry in archive.infolist():
                # These archives contain a single flat file. Reject unexpected paths.
                assert Path(entry.filename).name == entry.filename, entry.filename
                target = dest / entry.filename
                if not target.exists() or target.stat().st_size != entry.file_size:
                    target.write_bytes(archive.read(entry))
                inventory.append({"variant": label, "zip": zip_name, "entry": entry.filename,
                                  "size": entry.file_size, "compressed_size": entry.compress_size,
                                  "extracted_path": str(target)})
                if target.suffix.lower() == ".fbx":
                    reports[label] = inspect(target.read_bytes())
                    reports[label]["fbx_path"] = str(target)
    (WORK / "zip_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    (WORK / "fbx_analysis.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    with (WORK / "fbx_bones.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["variant", "name", "parent", "kind", "translation", "rotation"])
        writer.writeheader()
        for label, report in reports.items():
            for bone in report["bones"]:
                writer.writerow({"variant": label, **{key: bone[key] for key in ("name", "parent", "kind", "translation", "rotation")}})
    print(json.dumps({key: {k: v for k, v in value.items() if k != "bones"} for key, value in reports.items()}, indent=2))


if __name__ == "__main__":
    main()
