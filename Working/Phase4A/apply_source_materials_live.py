import unreal,json
from pathlib import Path
B='/Game/MetaHumanTo3DCharacter/Phase4A';rows=[]
for case in ['Unrigged','MixamoRecovered']:
    mat_path=B+'/Unrigged/PreservedSource/f9dcb69f_c978_4517_86d5_c509f2f721f9' if case=='Unrigged' else B+'/MixamoRecovered/PreservedSource/tripo_mat_c86468c2'
    m=unreal.load_asset(mat_path);assert m,mat_path
    for folder in ['Assisted180','Assisted180BallForward','Medial64','Medial128']:
        for name in ['SK_Lara','SK_Lara_Authoring'] if folder.startswith('Assisted') else ['SK_Lara']:
            mesh=unreal.load_asset(B+'/'+case+'/'+folder+'/'+name);slots=mesh.materials
            for i in range(len(slots)):
                slot=slots[i];slot.set_editor_property('material_interface',m);slots[i]=slot
            mesh.set_editor_property('materials',slots);assert all(s.material_interface==m for s in mesh.materials),'Material assignment did not apply'
            assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);rows.append({'mesh':mesh.get_path_name(),'material':m.get_path_name(),'readback':[s.material_interface.get_path_name() if s.material_interface else None for s in mesh.materials]})
(Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase4A')/'material_assignment_final.json').write_text(json.dumps(rows,indent=2));print('OWN_MATERIAL_ASSIGNMENT_DONE')
