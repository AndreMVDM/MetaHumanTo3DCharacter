"""Close exact-term and ThirdParty text-search gaps; inspect model/resource filename inventory."""
import json,subprocess,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';E=Path('D:/Epic Games/UE_5.8/Engine');rows=[]
queries={
 'exact_concepts':r'humanoid.?landmark|body.?landmark|anatomical.?landmark|skeletal.?fit|skeleton.?fit|joint.?fit|bone.?placement|body.?keypoint|pose.?estimation|semantic.?skeleton|humanoid.?characteri[sz]|symmetry.?detect|mesh.?segment|body.?segment|skeleton.?template|template.?rig|auto.?rig|medial.{0,30}semantic|control.?rig.{0,30}template|ik.?rig.{0,30}template|fbik.{0,30}template|body.?identity|body.?region|mesh.?correspond|skeleton.?tool|skeletal.?tool',
 'predictors_including_vendor':r'(predict|infer|estimate).{0,40}(joint|keypoint|body.pose)|humanoid.{0,40}(fit|model)|joint.{0,30}(predict|network|model)|body.{0,20}segment',
}
for n,q in queries.items():
    args=['rg','-n','-i','--max-columns','1200','--max-columns-preview',q,str(E/'Source'),str(E/'Plugins'),'-g','*.h','-g','*.hpp','-g','*.cpp','-g','*.inl','-g','*.py','-g','*.json','-g','*.ini','-g','*.uplugin','-g','*.xml','-g','*.yaml','-g','!**/Intermediate/**','-g','!**/Binaries/**']
    out=subprocess.run(args,capture_output=True);dest=W/'Search'/(n+'.txt');dest.write_bytes(out.stdout);rows.append({'name':n,'command':args,'matches':len(out.stdout.splitlines()),'return_code':out.returncode,'stderr':out.stderr.decode(errors='replace'),'output_sha256':hashlib.sha256(out.stdout).hexdigest()});print(n,rows[-1]['matches'],flush=True)
files=subprocess.run(['rg','--files',str(E/'Plugins'),'-g','!**/Intermediate/**','-g','!**/Binaries/**'],capture_output=True).stdout.decode(errors='replace').splitlines()
models=[p for p in files if Path(p).suffix.lower() in ['.onnx','.pt','.pth','.tflite','.dna','.npy','.npz'] or any(t in Path(p).name.lower() for t in ['joint_mapping','region_landmark','body_model','body_rig','body_joint','pipeline_presets','modelmanifest'])]
(O/'supplemental_search.json').write_text(json.dumps({'queries':rows,'thirdparty_text_included':True,'resource_candidates':models,'limit':'Models and uasset binaries enumerated by names/manifests; no assertion of exhaustive semantics in opaque binary payloads.'},indent=2))
