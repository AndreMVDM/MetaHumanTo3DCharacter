"""Read-only source/FBX investigation; writes only this new Evidence directory."""
from pathlib import Path
import hashlib, json, struct, zlib, subprocess, collections
from PIL import Image, ImageDraw
PROJECT = Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter')
ENGINE = Path(r'D:\Epic Games\UE_5.8\Engine')
OUT = Path(__file__).resolve().parent
def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')
def protected():
    paths = [PROJECT/'MHTo3DCharacter.uproject']
    for folder in ['Config', 'Content/MetaHumanTo3DCharacter/Phase2', 'Working/Phase2', 'Documentation/Phase2', 'Reference/MetaHuman_Conform_Topology']:
        paths += [p for p in (PROJECT/folder).rglob('*') if p.is_file()]
    return {str(p.relative_to(PROJECT)): {'bytes':p.stat().st_size, 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}
def prop(data, pos):
    kind=chr(data[pos]); pos+=1
    fixed={'Y':'h','C':'?','I':'i','F':'f','D':'d','L':'q'}
    if kind in fixed:
        fmt='<'+fixed[kind]; return struct.unpack_from(fmt,data,pos)[0],pos+struct.calcsize(fmt)
    if kind in 'SR':
        length=struct.unpack_from('<I',data,pos)[0];pos+=4;raw=data[pos:pos+length]
        return raw.decode('utf-8','replace') if kind=='S' else {'raw_bytes':length},pos+length
    if kind in 'fdlibc':
        count,encoding,length=struct.unpack_from('<III',data,pos);pos+=12;raw=data[pos:pos+length]
        if encoding:raw=zlib.decompress(raw)
        fmt={'f':'f','d':'d','l':'q','i':'i','b':'b','c':'?'}[kind]
        return list(struct.unpack('<'+str(count)+fmt,raw)),pos+length
    raise ValueError(kind)
def nodes(data,pos,limit,wide):
    out=[];size=25 if wide else 13
    while pos+size<=limit:
        end,count,plen,nlen=struct.unpack_from('<QQQB' if wide else '<IIIB',data,pos)
        if end==0:break
        cursor=pos+size;name=data[cursor:cursor+nlen].decode();cursor+=nlen;props=[]
        for _ in range(count):v,cursor=prop(data,cursor);props.append(v)
        children,_=nodes(data,cursor,end-size,wide) if cursor<end-size else ([],cursor)
        out.append({'name':name,'props':props,'children':children});pos=end
    return out,pos
def child(n,name):return [c for c in n['children'] if c['name']==name]
def properties(n):return {p['props'][0]:p['props'][4:] for g in child(n,'Properties70') for p in child(g,'P')}
def fbx(path):
    data=path.read_bytes();assert data.startswith(b'Kaydara FBX Binary')
    version=struct.unpack_from('<I',data,23)[0];ns,_=nodes(data,27,len(data),version>=7500);root={n['name']:n for n in ns}
    objects=root['Objects']['children'];types=collections.Counter(n['name'] for n in objects)
    summary={'path':str(path),'version':version,'global_settings':properties(root['GlobalSettings']),'object_counts':dict(types),'models':[], 'geometries':[], 'deformers':[], 'materials':[], 'textures':[]}
    for n in objects:
        name=n['name'];p=n['props'];base={'id':p[0],'name':str(p[1]).split('\x00')[0], 'kind':p[2] if len(p)>2 else None}
        if name=='Model':summary['models'].append({**base,'properties':properties(n)})
        if name=='Geometry':
            vs=child(n,'Vertices')[0]['props'][0];inds=child(n,'PolygonVertexIndex')[0]['props'][0];axes=[vs[i::3] for i in range(3)]
            base.update({'control_points':len(vs)//3,'polygon_count':sum(i<0 for i in inds),'polygon_vertices':len(inds),'raw_local_bounds':{'min':[min(a) for a in axes],'max':[max(a) for a in axes]},'layers':[c['name'] for c in n['children'] if c['name'].startswith('LayerElement')]})
            base['uv_layers']=[{'name':c['name'],'uv_pairs':len(child(c,'UV')[0]['props'][0])//2 if child(c,'UV') else 0} for c in n['children'] if c['name']=='LayerElementUV']
            summary['geometries'].append(base)
        if name=='Deformer':
            base['arrays']={c['name']:len(c['props'][0]) for c in n['children'] if c['props'] and isinstance(c['props'][0],list)};summary['deformers'].append(base)
        if name in ('Material','Texture'):summary['materials' if name=='Material' else 'textures'].append({**base,'properties':properties(n),'fields':{c['name']:c['props'] for c in n['children'] if c['name'] in ('FileName','RelativeFilename')}})
    summary['connections']=[c['props'] for c in child(root['Connections'],'C')]
    return summary
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if not (OUT/'protected_before.json').exists():save('protected_before.json',protected())
    ref=PROJECT/'Reference/MetaHuman_Conform_Topology';inv=[];thumbs=[]
    for p in sorted(ref.rglob('*')):
        if not p.is_file():continue
        row={'path':str(p.relative_to(ref)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        if p.suffix.lower()=='.png':
            im=Image.open(p);row.update({'format':im.format,'dimensions':list(im.size),'mode':im.mode});im.thumbnail((540,420));thumbs.append((p.name,im.copy()))
        inv.append(row)
    save('reference_inventory.json',inv)
    sheet=Image.new('RGB',(1100,460*4),'white');draw=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate(thumbs):
        x=(i%2)*550;y=(i//2)*460;sheet.paste(im,(x,y+30));draw.text((x+8,y+8),label,fill='black')
    sheet.save(OUT/'reference_texture_contact_sheet.jpg')
    inputs=[ref/'body.fbx',ref/'head.fbx']+list((PROJECT/'Working/Phase2/UE5').glob('*.fbx'))+list((PROJECT/'Working/Phase2/Mixamo').glob('*.fbx'))
    save('fbx_inspection.json',[fbx(p) for p in inputs])
    print('Reference inventory, FBX geometry/transforms and protection baseline captured.')
if __name__=='__main__':main()
