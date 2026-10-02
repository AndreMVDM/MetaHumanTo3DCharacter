from pathlib import Path
import json,subprocess,os
W=Path(__file__).resolve().parent;d=json.loads((W/'native_actions.json').read_text());env=os.environ.copy();env.update(d['Environment'])
generated_rsp=W/'NativeHost/Plugins/Phase4ATools/Intermediate/Build/Win64/x64/UnrealEditor/Development/Phase4ATools/Module.Phase4ATools.cpp.obj.rsp'
compiler=next(a for a in d['Actions'] if a['Type']=='Compile')
# UHT was run separately after changing a reflected declaration. Compile the existing
# UBT-authored generated-module response file before the exported link action.
result=subprocess.run('"'+compiler['CommandPath']+'" @"'+str(generated_rsp)+'"',cwd=compiler['WorkingDirectory'],env=env)
if result.returncode:raise SystemExit(result.returncode)
for a in d['Actions']:
    if 'SharedPCH.' in a['CommandArguments'] and all(Path(p).exists() for p in a['ProducedItems']):continue
    print('ACTION',a['Id'],a['Type'],flush=True)
    # Execute the exact compiler/linker actions exported by UBT, without shell interpretation.
    result=subprocess.run('"'+a['CommandPath']+'" '+a['CommandArguments'],cwd=a['WorkingDirectory'],env=env)
    if result.returncode:raise SystemExit(result.returncode)
