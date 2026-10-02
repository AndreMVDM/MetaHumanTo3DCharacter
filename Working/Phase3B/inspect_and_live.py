import runpy
from pathlib import Path
for name in ['inspect_final.py','live_start.py']:
    exec((Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')/name).read_text(),globals())
