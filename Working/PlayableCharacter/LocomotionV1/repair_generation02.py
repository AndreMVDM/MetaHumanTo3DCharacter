from pathlib import Path
import json
p=Path('Working/PlayableCharacter/LocomotionV1/generator.py');s=p.read_text();a=s.index('    # Preserve continuous VSizeXY');b=s.index('    for graph,name,value',a)
s=s[:a]+'''    # Keep legacy Speed telemetry intact; precise configurable boundaries use
    # continuous horizontal speed directly from the existing VSizeXY calculation.
    require(ae.add_member_variable('HorizontalSpeed',real,'0'),'horizontal speed variable')
    old_speed_set=next(n for n in ae.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Speed' in pins(n))
    outgoing=pin(old_speed_set,'then').list_connected_pins()[0];trunc=source(old_speed_set,'Speed');require(str(trunc.get_node_title())=='Truncate','expected historical speed conversion');length_pin=pin(trunc,'A').list_connected_pins()[0]
    speed_set=ae.add_set_member_variable_node('HorizontalSpeed');pin(old_speed_set,'then').break_pin_links();wire(old_speed_set,'then',speed_set,'execute');require(pin(speed_set,'then').try_create_connection(outgoing),'speed continuation');require(length_pin.try_create_connection(pin(speed_set,'HorizontalSpeed')),'continuous horizontal speed')
''' +s[b:]
s=s.replace("ag.add_get_member_variable_node('Speed'),'Speed',greater", "ag.add_get_member_variable_node('HorizontalSpeed'),'HorizontalSpeed',greater")
s=s.replace("ae.add_get_member_variable_node('Speed'),'Speed',less", "ae.add_get_member_variable_node('HorizontalSpeed'),'HorizontalSpeed',less")
p.write_text(s)
f=p.parent/'fresh_profile.json';c=json.loads(f.read_text());(f.parent/'fresh_profile_attempt02.json').write_text(f.read_text());c['output_namespace']=c['output_namespace'].removesuffix('02')+'03';f.write_text(json.dumps(c,indent=2)+'\n')
