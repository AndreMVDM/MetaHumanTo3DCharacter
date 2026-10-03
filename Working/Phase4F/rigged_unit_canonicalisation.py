"""Derived-only uniform root-unit canonicalisation for the scale-free UE IK retarget path.

For positive isotropic root scale s: root scale -> 1; every non-root local
translation -> s*t. Root translation, rotations, descendant scales, topology,
geometry and weights are preserved. Component-space bind positions are invariant.
No vendor, subject, bone-name or stature constant is used.
"""
import math

VERSION='phase4f.rigged-unit-canonicalisation/1.0.0'

def plan(bones, relative_tolerance=32*2**-23):
    roots=[n for n,b in bones.items() if b['parent'] is None]
    if len(roots)!=1:raise ValueError('requires exactly one connected root')
    root=roots[0];s=bones[root]['local']['scale'];factor=sum(x/3 for x in s)
    if not all(math.isfinite(x) and x>0 for x in s):raise ValueError('nonpositive or invalid root scale')
    if not math.isfinite(factor) or factor<=0:raise ValueError('invalid uniform factor')
    if max(abs(x-factor) for x in s)>relative_tolerance*factor:raise ValueError('nonuniform root scale requires a different certified conversion')
    for n,b in bones.items():
        seen=set();p=n
        while p is not None:
            if p not in bones or p in seen:raise ValueError('invalid hierarchy')
            seen.add(p);p=bones[p]['parent']
        if root not in seen:raise ValueError('disconnected hierarchy')
        for k in ['translation','rotation_xyzw','scale']:
            if not all(math.isfinite(x) for x in b['local'][k]):raise ValueError('non-finite bind')
    transforms={}
    for n,b in bones.items():
        t=b['local'];transforms[n]=dict(translation=t['translation'][:] if n==root else [factor*x for x in t['translation']],rotation_xyzw=t['rotation_xyzw'][:],scale=[1.,1.,1.] if n==root else t['scale'][:])
        if not all(math.isfinite(x) for x in transforms[n]['translation']):raise ValueError('unit conversion translation overflow')
    return dict(version=VERSION,root=root,factor=factor,needs_canonicalisation=abs(factor-1)>relative_tolerance,transforms=transforms,model='Uniform root factor distributed to ALL non-root local translations; root translation is already component centimetres and is not multiplied')

def derive(unreal, source_mesh, folder, mesh_name, skeleton_name, bones):
    p=plan(bones)
    if not p['needs_canonicalisation']:return source_mesh,p
    T=unreal.AssetToolsHelpers.get_asset_tools()
    for name in [mesh_name,skeleton_name]:
        if unreal.EditorAssetLibrary.does_asset_exist(folder+'/'+name):raise ValueError('refuse to overwrite derived assets')
    # An isolated associated skeleton prevents any mesh post-edit path touching the original.
    mesh=T.duplicate_asset(mesh_name,folder,source_mesh)
    isolated=unreal.RiggedUnitBridgeLibrary.attach_isolated_skeleton(mesh,folder+'/'+skeleton_name,folder+'/')
    if isolated is None or mesh.skeleton!=isolated:raise ValueError('native factory isolation failed')
    modifier=unreal.SkeletonModifier()
    if not modifier.set_skeletal_mesh(mesh):raise ValueError('native modifier cannot load duplicate')
    ns=list(bones);transforms=[]
    for n in ns:
        v=p['transforms'][n];t=unreal.Transform();t.set_editor_properties(dict(translation=unreal.Vector(*v['translation']),rotation=unreal.Quat(*v['rotation_xyzw']),scale3d=unreal.Vector(*v['scale'])));transforms.append(t)
    if not modifier.set_bones_transforms(ns,transforms,True):raise ValueError('native reference conversion failed')
    if not modifier.commit_skeleton_to_skeletal_mesh():raise ValueError('native derived bind commit failed')
    # The bridge exposes native reference synchronisation missing from Python.
    # Same cloned hierarchy/metadata; no new names, parents, weights or anatomy.
    if not unreal.RiggedUnitBridgeLibrary.sync_derived_reference(mesh,folder+'/'):raise ValueError('canonical skeleton reference synchronisation failed')
    sk=mesh.skeleton
    for asset in [sk,mesh]:
        if not unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False):raise ValueError('derived native save failed')
    p.update(source_mesh=source_mesh.get_path_name(),source_skeleton=source_mesh.skeleton.get_path_name(),derived_mesh=mesh.get_path_name(),derived_skeleton=sk.get_path_name())
    return mesh,p
