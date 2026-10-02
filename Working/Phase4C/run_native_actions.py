"""Execute UBT-exported compiler/linker actions, bypassing failed UBA executor."""
from pathlib import Path
import json,subprocess,os
W=Path(__file__).resolve().parent;d=json.loads((W/'native_actions.json').read_text());env=os.environ.copy();env.update(d['Environment'])
for a in d['Actions']:
    for p in a['ProducedItems']:
        assert Path(p).resolve().is_relative_to(W.resolve()),p
        Path(p).parent.mkdir(parents=True,exist_ok=True)
    print('ACTION',a['Id'],a['Type'],flush=True)
    result=subprocess.run('"'+a['CommandPath']+'" '+a['CommandArguments'],cwd=a['WorkingDirectory'],env=env)
    if result.returncode: raise SystemExit(result.returncode)
