"""Bind accepted R2/R4 execution to the user-confirmed Female input only."""
import json,hashlib,zipfile,collections
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=Path(__file__).parent;O=R/'Documentation/FinalAcceptance/FemaleBodyRigged';O.mkdir(parents=True,exist_ok=True);(O/'R2').mkdir(exist_ok=True);(W/'R2').mkdir(exist_ok=True)
B='/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance'
old=R/'Working/Phase4F/BenchmarkRuns/02_AegisNX7/R3';accepted=R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2'
c=json.loads((accepted/'config.json').read_text());c['output_namespace']=B+'/R2_EndToEnd';(W/'R2/config.json').write_text(json.dumps(c,indent=2)+'\n')
runner=(old/'execute_r2.py').read_text().replace("Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3/Initial","Documentation/FinalAcceptance/FemaleBodyRigged/R2");(W/'R2/execute_r2.py').write_text(runner)
manifest=R/'Documentation/R4/AegisNX7/animation_library_manifest.json';m=json.loads(manifest.read_text());assert m['status']=='PASS' and m['totals']['default']==89
inventory=dict(status='PASS',version='phase4f.animation-library/1.0.0',source='Authoritative accepted R4 source set reused without discovery or reclassification',accepted_manifest=str(manifest),accepted_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),assets=m['entries']);(O/'source_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
profile=json.loads((R/'Working/R4/AegisNX7/profile.json').read_text());profile.update(evidence_directory='Documentation/FinalAcceptance/FemaleBodyRigged',output_namespace=B,destination_mesh=B+'/R2_EndToEnd/Character/SK_Destination',destination_skeleton=B+'/R2_EndToEnd/Character/SKEL_Destination',accepted_retargeter=B+'/R2_EndToEnd/Retarget/RTG_MannyToDestination');(W/'profile.json').write_text(json.dumps(profile,indent=2)+'\n')
for n in ['bake.py','validate_saved.py','native_library.py']:(W/n).write_bytes((R/'Working/R4/AegisNX7'/n).read_bytes())
archive=R/'Characters/Female_Body_Rigged.zip';source=R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/Input/tripo_convert_cacfc500-a133-4b70-abe0-51d9c097585a.fbx';matches=[]
with zipfile.ZipFile(archive) as z:
    for n in z.namelist():
        if n.lower().endswith('.fbx'):matches.append(dict(member=n,sha256=hashlib.sha256(z.read(n)).hexdigest(),bytes=z.getinfo(n).file_size))
assert len(matches)==1 and matches[0]['sha256']==hashlib.sha256(source.read_bytes()).hexdigest(),'Existing imported source does not match confirmed archive'
(O/'input_selection.json').write_text(json.dumps(dict(status='PASS',user_correction='Use Female_Body_Rigged.zip instead of rigged Jane',archive=str(archive),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),fbx=str(source),archive_fbx=matches[0],original_mesh=c['input_mesh'],reuse_existing_import=True,no_reimport=True,historical_jane_excluded=True,source_definition_reused=True),indent=2)+'\n');print('CONFIRMED_INPUT_AND_R4_SOURCE_SET',B)
