"""Fresh saved review-map verification; not native skeletal runtime acceptance."""
import unreal,sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4F';B='/Game/MetaHumanTo3DCharacter/Phase4F'
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
results=[]
for ch in ['John','Jane']:
    co=O/ch;scene=json.loads((co/'native_review_scene.json').read_text());fit=json.loads((co/'current_proposal.json').read_text());expected={r['role']:r['position_cm'] for r in fit['joints'] if r['role']!='root'}
    assert L.load_level(scene['map']);controls={a.get_actor_label()[11:]:a for a in A.get_all_level_actors() if a.get_actor_label().startswith('F4 CONTROL ')}
    assert set(controls)==set(expected)
    error=max(math.sqrt(sum((a-b)**2 for a,b in zip([actor.get_actor_location().x,actor.get_actor_location().y,actor.get_actor_location().z],expected[n]))) for n,actor in controls.items())
    assert error<1e-5
    source=unreal.load_asset(scene['source_mesh']);assert isinstance(source,unreal.StaticMesh)
    actors=[a for a in A.get_all_level_actors() if a.get_actor_label().startswith('F4 '+ch)]
    assert len(actors)==2
    assert all(abs(a.get_actor_scale3d().x-1)+abs(a.get_actor_scale3d().y-1)+abs(a.get_actor_scale3d().z-1)==0 for a in actors)
    materials=[]
    for slot in source.static_materials:
        mat=slot.material_interface;assert mat and mat.get_path_name().startswith(B)
        textures=[]
        for e in unreal.MaterialEditingLibrary.get_material_expressions(mat):
            if isinstance(e,unreal.MaterialExpressionTextureSample):
                tex=e.get_editor_property('texture');textures.append(tex.get_path_name() if tex else None)
        assert textures and all(t and t.startswith(B) for t in textures)
        materials.append({'material':mat.get_path_name(),'textures':textures})
    r={'character':ch,'status':'passed','fresh_process_map_loaded':True,'controls':len(controls),'control_max_error_cm':error,'source_height_cm':2*source.get_bounds().box_extent.z,'source_actor_scales_unit':True,'source_materials':materials,'human_review_created':False,'runtime_playback_test':False}
    results.append(r)
(O/'APoseContinuation/native_review_fresh_readback.json').write_text(json.dumps({'status':'passed','results':results,'scope':'Saved static anatomical authoring maps only. Not skeletal/native-runtime or clean-project playback.'},indent=2))
print('PHASE4F_REVIEW_READBACK_PASSED',results)
