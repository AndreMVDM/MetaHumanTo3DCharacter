import json
from pathlib import Path
W=Path('Working/PlayableCharacter/LocomotionV1');O=Path('Documentation/PlayableCharacter/LocomotionV1');g=json.loads((O/'generation.json').read_text());profiles={'Fresh':dict(assets=g['assets'],speed_variable='HorizontalSpeed',settings=g['settings'],expected_version=g['version'])}
for subject,name in [('Female','FemaleBody'),('Aegis','Aegis')]:
 B='/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/'+subject;profiles[subject]=dict(assets=dict(level=B+'/L_'+name+'MovementReview',character=B+'/BP_'+name+'MovementReviewCharacter',anim_blueprint=B+'/ABP_'+name+'MovementReview',game_mode=B+'/BP_'+name+'MovementReviewGameMode'),speed_variable='Speed',settings=g['settings'])
(W/'regression_profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
s=Path('Working/ReviewFixes/RunJumpLand/native_measure.py').read_text();a=s.index("R=Path(");b=s.index('E=unreal.get_editor_subsystem',a)
s=s[:a]+'''W=Path(__file__).parent;O=Path(json.loads((W/'fresh_profile.json').read_text())['evidence_directory'])
cmd=unreal.SystemLibrary.get_command_line();subject=re.search(r'-LocomotionCase=(\\w+)',cmd).group(1);mode='after';handoff=False
C=json.loads((W/'regression_profiles.json').read_text())[subject];MAP=C['assets']['level'].split('.')[0];ABP=C['assets']['anim_blueprint'].split('.')[0];BP=C['assets']['character'].split('.')[0];settings_config=C['settings'];idle_threshold=settings_config['IdleSpeedThreshold'];run_threshold=(settings_config['WalkSpeed']+settings_config['RunSpeed'])/2
''' +s[b:]
s=s.replace("x['anim_speed']>450", "x['anim_speed']>run_threshold").replace("x['anim_speed']>5", "x['anim_speed']>idle_threshold")
s=s.replace("anim.get_editor_property('Speed')", "anim.get_editor_property(C['speed_variable'])")
s=s.replace(">(500 if 'Shift' in case['name'] else 250)", ">(.9*settings_config['RunSpeed'] if 'Shift' in case['name'] else .9*settings_config['WalkSpeed'])")
s=s.replace("distance<=650*dt+3", "distance<=(settings_config['RunSpeed']+50)*dt+3")
s=s.replace("events.append(dict(touchdown=rows[i]", "events.append(dict(touchdown_horizontal_speed=rows[i]['horizontal_speed'],first_grounded_state=rows[i]['state'],touchdown=rows[i]")
s=s.replace("for event in events:require(event['delay_s']<.25 and event['distance_cm']<150,'moving landing delay/skid '+case['name'])", "for event in events:\n                require(event['delay_s']<.1 and event['distance_cm']<settings_config['RunSpeed']*.1,'moving landing delay/skid '+case['name'])\n                require(event['first_grounded_state'] in ['Walk','Run'],'incorrect first grounded state '+case['name'])\n                if 'release_at' not in case:require(event['touchdown_horizontal_speed']>=.95*(settings_config['RunSpeed'] if 'LeftShift' in case['keys'] else settings_config['WalkSpeed']),'forced velocity stop '+case['name'])")
s=s.replace("D['possession']='PASS';", "D['possession']='PASS';D['authoring_bridge_loaded']=hasattr(unreal,'RiggedUnitBridgeLibrary');require(not D['authoring_bridge_loaded'],'authoring bridge loaded');\n            if C.get('expected_version'):require(str(anim.get_editor_property('LocomotionTemplateVersion'))==C['expected_version'],'wrong generated version')\n            ")
(W/'native_regression.py').write_text(s)
