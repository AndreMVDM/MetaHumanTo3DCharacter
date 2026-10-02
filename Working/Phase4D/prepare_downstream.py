from pathlib import Path
P=Path(__file__).resolve().parents[2]
a=(P/'Working/Phase4A/ue_common.py').read_text().replace("W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'","W=P/'Working/Phase4D';O=P/'Documentation/Phase4D'").replace("sys.dont_write_bytecode=True;sys.path.insert(0,str(P/'Working/Phase3B'));import common","sys.dont_write_bytecode=True")
b=(P/'Working/Phase3B/common.py').read_text();b=b[b.index('def v('):]
(P/'Working/Phase4D/ue_common_d.py').write_text('import re\n'+a+'\n'+b,encoding='utf-8')
