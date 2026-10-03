"""UE commandlet entry: -PlayableProfile=<absolute JSON profile>."""
import unreal,json,sys,traceback,re,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).parent));from generator import generate,VERSION
match=re.search(r'-PlayableProfile="?([^"\r\n]+?)(?:"|\s+-|$)',unreal.SystemLibrary.get_command_line());assert match,'PlayableProfile argument required';P=Path(match.group(1).strip());C=json.loads(P.read_text());O=Path(C['evidence_directory']);O.mkdir(parents=True,exist_ok=True)
try:D=generate(C);D['generator_sha256']=hashlib.sha256((Path(__file__).parent/'generator.py').read_bytes()).hexdigest();D['profile_sha256']=hashlib.sha256(P.read_bytes()).hexdigest()
except Exception:D=dict(status='FAIL',version=VERSION,error=traceback.format_exc())
(O/'generation.json').write_text(json.dumps(D,indent=2)+'\n');print('PLAYABLE_GENERATION',D['status'],D.get('error',''))
