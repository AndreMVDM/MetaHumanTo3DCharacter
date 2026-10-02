from pathlib import Path
import json, zipfile, hashlib, importlib.util, sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'
def save(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[P/'MHTo3DCharacter.uproject']
for folder in ['Characters','Config','Content','Reference','Documentation/Phase2','Documentation/Phase3','Documentation/Phase3B']:
    protected.extend(p for p in (P/folder).rglob('*') if p.is_file() and 'Phase4A' not in p.parts)
save('protected_before.json',{str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(protected)})
spec=importlib.util.spec_from_file_location('readonly_parser',P/'Documentation/Phase3/Evidence/collect_evidence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
inv=[];fbxs=[]
for case,name in [('MixamoRecovered','Lara_Rigged_Mixamo.zip'),('Unrigged','Lara_UnRigged_Textured.zip')]:
    src=P/'Characters'/name;dest=W/'Inputs'/case;dest.mkdir(parents=True,exist_ok=True)
    row={'case':case,'archive':str(src),'bytes':src.stat().st_size,'sha256':digest(src),'entries':[]};inv.append(row)
    with zipfile.ZipFile(src) as z:
        for member in z.infolist():
            target=(dest/member.filename).resolve();assert target.is_relative_to(dest.resolve())
            row['entries'].append({'name':member.filename,'bytes':member.file_size,'compressed_bytes':member.compress_size,'crc32':member.CRC})
            if not member.is_dir():
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(member));row['entries'][-1]['sha256']=digest(target)
                if target.suffix.lower()=='.fbx':fbxs.append(m.fbx(target))
save('zip_inventory.json',inv);save('fbx_inspection.json',fbxs)
print(json.dumps(inv,indent=2));print(json.dumps(fbxs,indent=2))
