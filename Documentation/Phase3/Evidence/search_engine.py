"""Record broad source searches without writing to the engine."""
from collect_evidence import ENGINE, OUT, save
from pathlib import Path
import subprocess, json, hashlib
GROUPS={
 'resize':r'auto.?resiz|character.?resiz|body.?resiz|mesh.?resiz|metahuman.?resiz|resiz',
 'fit':r'conform|fit.?body|body.?fit|mesh.?fit|fit.?mesh|template.?fit|wrap|morph.?fit',
 'proportions_scale':r'body.?proportion|character.?proportion|skeleton.?proportion|skeletal.?mesh.?scale|mesh.?scale|importuniformscale',
 'identity':r'auto.?rig|characterization|metahuman.?identity|metahuman.?creator|mesh.?to.?metahuman|metahuman.?animator|body.?dna|template.?mesh|body.?template|mesh.?correspondence|landmark|neutral.?pose|identity.?solve|\bDNA\b'}
def main():
    manifest=[]
    for name,pattern in GROUPS.items():
        args=['rg','-n','-i','--no-heading','-g','*.h','-g','*.cpp','-g','*.py','-g','*.json','-g','*.ini','-g','!**/Intermediate/**','-g','!**/Binaries/**',pattern,str(ENGINE/'Source'),str(ENGINE/'Plugins')]
        p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/(name+'_search.txt')).write_text(p.stdout,encoding='utf-8')
        manifest.append({'group':name,'pattern':pattern,'roots':[str(ENGINE/'Source'),str(ENGINE/'Plugins')],'exit_code':p.returncode,'matching_lines':len(p.stdout.splitlines()),'stderr':p.stderr})
    save('search_manifest.json',manifest)
    files=[]
    for root in [ENGINE/'Plugins/MetaHuman',ENGINE/'Plugins/Animation/IKRig',ENGINE/'Plugins/Animation/PBIK',ENGINE/'Plugins/Experimental/Animation']:
        for p in root.rglob('*'):
            if p.is_file() and ('Source' in p.parts or p.suffix in ('.uplugin','.py')) and 'Intermediate' not in p.parts and 'Binaries' not in p.parts:
                files.append({'path':str(p.relative_to(ENGINE)),'bytes':p.stat().st_size})
    save('relevant_file_inventory.json',files)
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
