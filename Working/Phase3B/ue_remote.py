"""Project-scoped loopback remote Python client; never selects another project."""
import sys, time, json
from pathlib import Path
sys.path.insert(0, r'D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')
import remote_execution as remote
session = remote.RemoteExecution()
try:
    session.start()
    time.sleep(2)
    nodes = session.remote_nodes
    if len(sys.argv) == 1:
        print(json.dumps(nodes, indent=2))
    else:
        node = next(n for n in nodes if n.get('project_name') == 'MHTo3DCharacter')
        session.open_command_connection(node['node_id'])
        command = Path(sys.argv[1]).resolve().as_posix()
        result = session.run_command(command, raise_on_failure=False)
        print(json.dumps(result, indent=2))
        if not result['success']: sys.exit(1)
finally:
    session.stop()
