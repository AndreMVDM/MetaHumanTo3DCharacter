from pathlib import Path
import json
p=Path('Working/PlayableCharacter/LocomotionV1/generator.py');s=p.read_text();anchor="    return dict(graph=ag,players=players,moving=moving,running=running,land=land,final=final)"
s=s.replace(anchor,"""    eg=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');setter=next(n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Landing' in pins(n));predicate=source(setter,'Landing')
    require('A' in pins(predicate) and 'B' in pins(predicate),'legacy landing predicate')
    timer=source(predicate,'A');not_air=source(predicate,'B')
    require(' > ' in str(timer.get_node_title()) and 'LandTime' in pins(source(timer,'A')) and float(pin(timer,'B').get_pin_value())==0,'unmodified legacy timer guard required')
    require('Airborne' in pins(source(not_air,'A')),'unmodified legacy grounded guard required; corrected/generated scaffolds cannot be re-promoted')
"""+anchor)
s=s.replace("    for n in nodes:\n        if 'bPickA'", "    rebound={'Jump':0,'Land':0}\n    for n in nodes:\n        if 'bPickA'")
s=s.replace("if any('LandTime' in pins(p.get_owning_node()) for p in outputs):require(pin(n,'A').set_pin_value(str(clips['Land'].get_play_length())),'Land duration')", "if any('LandTime' in pins(p.get_owning_node()) for p in outputs):\n                require(pin(n,'A').set_pin_value(str(clips['Land'].get_play_length())),'Land duration');rebound['Land']+=1")
s=s.replace("if ' < ' in str(n.get_node_title()) and 'A' in pins(n) and 'AirTime' in pins(source(n,'A')):require(pin(n,'B').set_pin_value(str(clips['Jump'].get_play_length())),'Jump duration')", "if ' < ' in str(n.get_node_title()) and 'A' in pins(n) and 'AirTime' in pins(source(n,'A')):\n            require(pin(n,'B').set_pin_value(str(clips['Jump'].get_play_length())),'Jump duration');rebound['Jump']+=1\n    require(rebound=={'Jump':1,'Land':1},'unique destination timing guards required')")
p.write_text(s)
f=p.parent/'fresh_profile.json';c=json.loads(f.read_text());(f.parent/'fresh_profile_generated03.json').write_text(f.read_text());c['output_namespace']=c['output_namespace'].removesuffix('03')+'04';f.write_text(json.dumps(c,indent=2)+'\n')
