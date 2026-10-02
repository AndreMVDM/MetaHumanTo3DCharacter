from pathlib import Path
import shutil,hashlib,json
P=Path(__file__).resolve().parents[2];R=Path(r'E:/Repo/UE/Projects/AnimationRetargeting/Content');D=P/'Content/MetaHumanTo3DCharacter/Phase3B/SourceAnimations';D.mkdir(parents=True,exist_ok=True)
files=['Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset','Characters/Mannequins/Animations/Quinn/MF_Walk_Fwd.uasset','ExampleContent/ControlRig/Animations/JumpingJacks.uasset','Characters/Mannequins/Rigs/Poses/Manny/Manny_upperarm_r_anim.uasset','Characters/Mannequins/Animations/Manny/MM_Death_Front_01.uasset']
rows=[]
for f in files:
    s=R/f;d=D/s.name
    assert s.is_file(),s
    before=hashlib.sha256(s.read_bytes()).hexdigest()
    if not d.exists():shutil.copyfile(s,d)
    assert hashlib.sha256(s.read_bytes()).hexdigest()==before
    rows.append({'source':str(s),'candidate_copy':str(d),'sha256':before,'source_unchanged':True})
(P/'Documentation/Phase3B/source_animation_inventory.json').write_text(json.dumps(rows,indent=2))
