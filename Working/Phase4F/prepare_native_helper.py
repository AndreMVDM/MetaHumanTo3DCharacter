"""Reuse proven DNA reader implementation in a Phase4F-only helper binary."""
import sys, shutil, json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F'
src=P/'Working/Phase4C/NativeHost/Plugins/Phase4CTools';dst=W/'NativeHost/Plugins/Phase4CTools'
shutil.copytree(src,dst,dirs_exist_ok=True)
old=src.as_posix();new=dst.as_posix()
for p in dst.rglob('*'):
    if p.suffix in ['.h','.cpp','.rsp','.cs','.json','.uplugin']:
        text=p.read_text(encoding='utf-8-sig').replace(old,new).replace(str(src),str(dst))
        if p.name=='Phase4CLibrary.cpp':
            text=text.replace('Working/Phase4C/Donor/','Working/Phase4F/').replace('outside Phase4C donor scope','outside Phase4F donor scope')
        if p.name=='UnrealEditor-Phase4CTools.dll.rsp':text='\n'.join(l for l in text.splitlines() if not l.endswith('.res"'))
        p.write_text(text,encoding='utf-8')
print('Prepared isolated helper; PCH and Engine include/library inputs remain read-only prior build inputs.')
