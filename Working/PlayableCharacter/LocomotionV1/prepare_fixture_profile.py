import json
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=R/'Working/PlayableCharacter/LocomotionV1';O=R/'Documentation/PlayableCharacter/LocomotionV1';B='/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2'
M=json.loads((R/'Documentation/FinalAcceptance/FemaleBodyRigged/animation_library_manifest.json').read_text());animations={}
for role,name in [('Idle','MM_Idle'),('Walk','MF_Walk_Fwd'),('Run','MM_Run_Fwd'),('Jump','MM_Jump'),('Fall','MM_Fall_Loop'),('Land','MM_Land')]:
 rows=[x for x in M['entries'] if x['name']==name and x.get('bake_result')=='PASS' and ('/InPlace/' in x['source_path'] if role in ['Idle','Walk','Run'] else '/Anims/Unarmed/' in x['source_path'])];assert len(rows)==1;animations[role]=rows[0]['destination_path']
C=dict(output_namespace='/Game/MetaHumanTo3DCharacter/PlayableCharacter/LocomotionV1Regression/FreshGenerated',destination_mesh=M['destination_mesh'],animations=animations,scaffold=dict(character=B+'/BP_AegisMovementReviewCharacter',anim_blueprint=B+'/ABP_AegisMovementReview',game_mode=B+'/BP_AegisMovementReviewGameMode',level=B+'/L_AegisMovementReview'),evidence_directory=str(O),locomotion=dict(IdleSpeedThreshold=5,WalkSpeed=300,RunSpeed=600,LandingBlendDuration=.1))
(W/'fresh_profile.json').write_text(json.dumps(C,indent=2)+'\n')
