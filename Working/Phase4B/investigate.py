"""Read-only installation investigation and protected-file baseline. No fitter imports."""
import hashlib,json,subprocess,sys,zipfile,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[2]; W=P/'Working/Phase4B'; O=P/'Documentation/Phase4B'; E=Path('D:/Epic Games/UE_5.8/Engine')
O.mkdir(parents=True,exist_ok=True); (W/'Search').mkdir(exist_ok=True)
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,x): (O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
if not (O/'protected_before.json').exists():
    files=[]
    for root in ['Characters','Content','Config','Reference','Documentation','Working/Phase4A']:
        for p in (P/root).rglob('*'):
            if p.is_file() and 'Phase4B' not in p.parts and not any(t in p.parts for t in ['DDC','Intermediate','Saved','Binaries','__pycache__']): files.append(p)
    files.append(P/'MHTo3DCharacter.uproject')
    save('protected_before.json',{'scope':'All source archives, existing Content/Config/Reference/docs, Phase4A authored working files; excludes execution caches; engine evidence hashes separately','files':{str(p.relative_to(P)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in files}})
archive=P/'Characters/Lara_UnRigged_Textured.zip'
with zipfile.ZipFile(archive) as z:
    inventory={'archive':str(archive),'archive_sha256':digest(archive),'bytes':archive.stat().st_size,'entries':[{'name':i.filename,'bytes':i.file_size,'sha256':hashlib.sha256(z.read(i)).hexdigest()} for i in z.infolist() if not i.is_dir()]}
save('input_inventory.json',inventory)
reports=['RetargetingInvestigation/InvestigationReport.md','RetargetingInvestigation/SupplementalIKConfiguration.md','Phase2/Phase2RetargetingReport.md','Phase3/MetaHumanResizeConformInvestigation.md','Phase3B/Phase3BHeightNormalisationRetargeting.md','Phase4A/Phase4AAutoRigInvestigation.md']
save('existing_evidence_index.json',[{'path':str(P/'Documentation'/r),'sha256':digest(P/'Documentation'/r),'headings':[l for l in (P/'Documentation'/r).read_text(encoding='utf-8-sig').splitlines() if l.startswith('#')]} for r in reports])
groups={
 'semantic':r'humanoid.{0,30}landmark|body.{0,30}landmark|anatomic.{0,30}landmark|skelet(al|on).{0,30}fit|joint.{0,20}fit|bone.{0,20}place|body.{0,20}keypoint|human.{0,20}pose.{0,20}estimat|semantic.{0,20}skelet|pose.estimation',
 'geometry':r'symmetry.detect|bilateral.symmetry|mesh.segment|body.segment|skeleton.template|template.rig|auto.?rig|automatic.rig|medial.{0,30}semantic|mesh.correspond',
 'templates':r'characteri[sz]ation|AutoFBIK|AutoRetarget|SkeletonViaSampling|SkeletonFromMesh|SkeletonFitting|FitSkeleton|InferJoints',
 'metahuman':r'BodyIdentity|ConformTarget|Estimate.*Joint|Predict.*Joint|Predict.*Keypoint|Keypoints|body_region|region_landmarks|PipelineFitToArbitraryTarget',
 'ml':r'landmark.*model|model.*landmark|pose.*network|network.*pose|body.*network|network.*body|human.*keypoint|skelet.*neural|joint.*neural',
}
manifest={'engine_root':str(E.parent),'engine_version':json.loads((E/'Build/Build.version').read_text()),'scope':['Engine/Source','Engine/Plugins incl Content text/manifests/descriptors'],'excluded':['Intermediate','Binaries','ThirdParty (broad vendor noise; MetaHuman internal algorithm source still included)'],'queries':[]}
for name,pattern in groups.items():
    args=['rg','-n','-i','--no-heading','--max-columns','1600','--max-columns-preview',pattern,str(E/'Source'),str(E/'Plugins'),'-g','*.h','-g','*.cpp','-g','*.inl','-g','*.cs','-g','*.py','-g','*.json','-g','*.ini','-g','*.uplugin','-g','*.usf','-g','!**/Intermediate/**','-g','!**/Binaries/**','-g','!**/ThirdParty/**']
    out=subprocess.run(args,capture_output=True); dest=W/'Search'/f'{name}.txt';dest.write_bytes(out.stdout)
    manifest['queries'].append({'name':name,'pattern':pattern,'command':args,'return_code':out.returncode,'matches':len(out.stdout.splitlines()),'output':str(dest),'stderr':out.stderr.decode(errors='replace')})
    print(name,len(out.stdout.splitlines()),flush=True)
allfiles=subprocess.run(['rg','--files',str(E/'Plugins'),str(E/'Source'),'-g','!**/Intermediate/**','-g','!**/Binaries/**'],capture_output=True)
files=allfiles.stdout.decode(errors='replace').splitlines()
resources=[p for p in files if any(t in p.lower() for t in ['landmark','keypoint','poseestimat','bodyidentity','body_joint','region_land','identitytemplate','skeletonization']) and Path(p).suffix.lower() in ['.json','.binary','.bin','.dna','.onnx','.uasset','.h','.cpp','.py']]
save('installed_resources.json',[{'path':p,'bytes':Path(p).stat().st_size} for p in resources])
manifest['enumerated_files']=len(files);manifest['resource_candidates']=len(resources);save('search_manifest.json',manifest)
print('BASELINE',len(json.loads((O/'protected_before.json').read_text())['files']),flush=True)
