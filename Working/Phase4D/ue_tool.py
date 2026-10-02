"""Execute in the existing UE Python console. Only Phase4D assets are saved.

Native viewport gizmos + an external lightweight button panel, no skeletal
authoring. Select, position, record, review; never accepts anatomy on movement.
"""
import sys, json, traceback, time, math, builtins, importlib
from pathlib import Path
import unreal
sys.dont_write_bytecode=True
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4D';O=P/'Documentation/Phase4D'
sys.path.insert(0,str(W))
import core
importlib.reload(core)
B='/Game/MetaHumanTo3DCharacter/Phase4D';MAP=B+'/Maps/L_GuidedCorrection'
def start_tool():
    global phase4d_tool
    if hasattr(builtins,'phase4d_tool'):
        try: unreal.unregister_slate_post_tick_callback(builtins.phase4d_tool.handle)
        except Exception: pass
    phase4d_tool=Phase4DTool()
    builtins.phase4d_tool=phase4d_tool
    return phase4d_tool
class Phase4DTool:
    def __init__(self):
        self.A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);self.U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);self.L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);self.T=unreal.AssetToolsHelpers.get_asset_tools()
        self.state=core.rebuild(core.read(W/'session.json') if (W/'session.json').exists() else core.fresh_state());core.export(self.state)
        self.controls={};self.edges={};self.generated=[];self.track_actors=[];self.materials={};self.last_poll=0;self.last_preview='';self.errors=[]
        try:
            self.build();self.handle=unreal.register_slate_post_tick_callback(self.tick);self.publish('Ready. Start trial before recording edits or anatomical reviews.')
        except Exception:
            core.save(O/'ue_tool_error.json',{'traceback':traceback.format_exc()});raise
    def material(self,name,colour,opacity=None):
        m=unreal.load_asset(B+'/Materials/'+name)
        if not m:
            m=self.T.create_asset(name,B+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);m.set_editor_property('two_sided',True);ML=unreal.MaterialEditingLibrary
            node=ML.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,0,0);node.set_editor_property('constant',unreal.LinearColor(*colour,1));ML.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
            if opacity is not None:
                m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);node=ML.create_material_expression(m,unreal.MaterialExpressionConstant,0,150);node.set_editor_property('r',opacity);ML.connect_material_property(node,'',unreal.MaterialProperty.MP_OPACITY)
            ML.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
        return m
    def duplicate(self,source,target):
        a=unreal.load_asset(target)
        if not a: a=unreal.EditorAssetLibrary.duplicate_asset(source,target)
        if not a:raise RuntimeError('duplicate failed '+target)
        return a
    def actor(self,label,asset,pos,scale,mat,folder):
        a=self.A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator());a.set_actor_label(label);a.set_folder_path(folder);a.static_mesh_component.set_static_mesh(asset);a.static_mesh_component.set_material(0,mat);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_enable_collision(False);return a
    def line(self,label,a,b,mat,folder='Phase4D/Generated'):
        delta=core.sub(b,a);length=core.norm(delta);actor=self.actor(label,self.cylinder,core.mul(core.add(a,b),.5),[.003,.003,max(.001,length/100)],mat,folder);actor.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(unreal.Vector(*delta)),False);return actor
    def build(self):
        # Current prior map is fully saved; new_level does not save that map.
        if unreal.EditorAssetLibrary.does_asset_exist(MAP): assert self.L.load_level(MAP)
        else: assert self.L.new_level(MAP)
        assert self.U.get_editor_world().get_path_name().startswith(MAP)
        for actor in self.A.get_all_level_actors():self.A.destroy_actor(actor)
        self.sphere=unreal.load_asset('/Engine/BasicShapes/Sphere');self.cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder')
        self.materials={key:self.material('M_'+key,col,opacity) for key,col,opacity in [('Automatic',(.03,.65,.18),None),('Review',(.95,.48,.03),None),('Moved',(.05,.38,1),None),('Dependent',(.64,.18,.94),None),('Reviewed',(.1,.75,.8),None),('Baseline',(.3,.45,.55),None),('Ghost',(.65,.72,.8),.20),('Track',(.86,.12,.35),None)]}
        self.mesh=self.duplicate('/Game/MetaHumanTo3DCharacter/Phase4C/Geometry/SM_Lara180',B+'/Geometry/SM_Lara180')
        tex=self.duplicate('/Game/MetaHumanTo3DCharacter/Phase4B/Materials/T_LaraOriginal',B+'/Materials/T_LaraOriginal')
        original=self.duplicate('/Game/MetaHumanTo3DCharacter/Phase4B/Materials/M_LaraOriginal',B+'/Materials/M_LaraOriginal')
        for expression in unreal.MaterialEditingLibrary.get_material_expressions(original):
            if isinstance(expression,unreal.MaterialExpressionTextureSample):expression.set_editor_property('texture',tex)
        unreal.MaterialEditingLibrary.recompile_material(original);assert unreal.EditorAssetLibrary.save_loaded_asset(original,only_if_is_dirty=False)
        for i in range(len(self.mesh.static_materials)):self.mesh.set_material(i,original)
        assert unreal.EditorAssetLibrary.save_loaded_asset(self.mesh,only_if_is_dirty=False);assert unreal.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
        self.reference=self.actor('Lara original surface - 180cm reference',self.mesh,[-100,0,0],[1,1,1],original,'Phase4D/Surface')
        self.surface=self.actor('Lara correction surface - original geometry',self.mesh,[0,0,0],[1,1,1],self.materials['Ghost'],'Phase4D/Surface')
        for r in self.state['joints']:
            n=r['role'];a=self.actor('D4 '+core.LABELS.get(n,n),self.sphere,r['position_cm'],[.014]*3,self.materials['Automatic' if r['status']=='automatically_accepted' else 'Review'],'Phase4D/BodyControls');self.controls[n]=a
            if n=='root':a.set_is_temporarily_hidden_in_editor(True)
        # Immutable automatic proposal for reference overlay; hidden until requested.
        for r in core.read(O/'automatic_starting_proposal.json')['joints']:
            a=self.actor('D4 original '+r['role'],self.sphere,r['position_cm'],[.009]*3,self.materials['Baseline'],'Phase4D/AutomaticOverlay');a.set_is_temporarily_hidden_in_editor(True)
        for side,tracks in self.state['tracks'].items():
            for t in tracks:
                points=core.track_points(t)
                for i,(a,b) in enumerate(zip(points,points[1:])):
                    actor=self.line('D4 '+t['candidate_id']+' segment '+str(i),a,b,self.materials['Track'],'Phase4D/DigitTracks');actor.set_is_temporarily_hidden_in_editor(True);self.track_actors.append((side,t['candidate_id'],actor))
        self.redraw();assert self.L.save_current_level();self.view('front')
        dm=unreal.DynamicMesh();opt=unreal.GeometryScriptCopyMeshFromAssetOptions();opt.set_editor_property('apply_build_settings',False);unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(self.mesh,dm,opt,unreal.GeometryScriptMeshReadLOD())
        vertices=[];Q=unreal.GeometryScript_MeshQueries
        for i in range(Q.get_num_vertex_i_ds(dm)):
            p,ok=Q.get_vertex_position(dm,i)
            if ok:vertices.append([p.x,p.y,p.z])
        core.save(W/'ue_vertices.json',vertices)
        assets=[]
        for path in unreal.EditorAssetLibrary.list_assets(B,recursive=True):
            asset=unreal.load_asset(path);assets.append({'path':path,'class':asset.get_class().get_name()})
        core.save(O/'ue_scene.json',{'map':MAP,'height_cm':2*self.mesh.get_bounds().box_extent.z,'triangles':dm.get_triangle_count(),'vertex_count':len(vertices),'uv_sets':Q.get_num_uv_sets(dm),'assets':assets,'skeletal_asset_count':sum(r['class'] in ['Skeleton','SkeletalMesh','AnimSequence','IKRigDefinition','IKRetargeter'] for r in assets),'display_scale':[1,1,1],'controls':list(self.controls),'panel':'Working/Phase4D/panel.py','anatomical_approvals_created':0})
    def redraw(self,preview=None):
        state=preview or self.state;joints={r['role']:r for r in state['joints']}
        for n,r in joints.items():
            self.controls[n].set_actor_location(unreal.Vector(*r['position_cm']),False,False)
            colour='Moved' if r['status']=='manually_corrected' else ('Dependent' if r['status']=='dependency_recomputed' else ('Automatic' if r['status']=='automatically_accepted' else 'Review'))
            if n in state['approvals'] and colour not in ['Moved','Dependent']:colour='Reviewed'
            self.controls[n].static_mesh_component.set_material(0,self.materials[colour])
            if r['parent_role']:
                parent=joints[r['parent_role']]['position_cm'];point=r['position_cm'];delta=core.sub(point,parent)
                if n not in self.edges:self.edges[n]=self.line('D4 generated edge '+n,parent,point,self.materials['Dependent'])
                edge=self.edges[n];edge.set_actor_location(unreal.Vector(*core.mul(core.add(parent,point),.5)),False,False);edge.set_actor_scale3d(unreal.Vector(.003,.003,core.norm(delta)/100));edge.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(unreal.Vector(*delta)),False)
        for key,f in state['fingers'].items():
            for end in ['root','tip']:
                n=key+':'+end
                if n not in self.controls:self.controls[n]=self.actor('D4 '+key+' '+end,self.sphere,f[end+'_cm'],[.01]*3,self.materials['Review'],'Phase4D/FingerControls')
                self.controls[n].set_actor_location(unreal.Vector(*f[end+'_cm']),False,False)
        for a in self.generated:self.A.destroy_actor(a)
        self.generated=[]
        for key,f in state['fingers'].items():
            pts=[joints['hand_'+f['side']]['position_cm']]+f['phalanges_cm']+[f['tip_cm']]
            for i,(a,b) in enumerate(zip(pts,pts[1:])):self.generated.append(self.line('D4 generated '+key+' '+str(i),a,b,self.materials['Dependent']))
    def positions(self):
        result={}
        for n,a in self.controls.items():
            p=a.get_actor_location();q=[p.x,p.y,p.z]
            if n=='root':continue
            original=self.state['fingers'][n.rsplit(':',1)[0]][n.rsplit(':',1)[1]+'_cm'] if ':' in n else next(r['position_cm'] for r in self.state['joints'] if r['role']==n)
            if core.norm(core.sub(q,original))>.001:result[n]=q
        return result
    def selected(self):
        selected=list(self.A.get_selected_level_actors());return [n for n,a in self.controls.items() if a in selected]
    def view(self,name):
        views={'front':([-50,335,92],[0,-90,0]),'side':([300,0,92],[0,180,0]),'pelvis':([0,145,105],[0,-90,0]),'arms':([0,170,130],[0,-90,0]),'knees':([0,135,55],[0,-90,0]),'feet':([110,5,15],[0,180,0]),'left hand':([68,8.5,93],[0,180,0]),'right hand':([-68,8.5,93],[0,0,0])}
        pos,rot=views[name];self.reference.set_is_temporarily_hidden_in_editor(name!='front');self.U.set_level_viewport_camera_info(unreal.Vector(*pos),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
        for side,tid,a in self.track_actors:a.set_is_temporarily_hidden_in_editor(not (name=='left hand' and side=='l' or name=='right hand' and side=='r'))
    def publish(self,message):
        core.save(W/'panel_status.json',{'message':message,'heartbeat_epoch':time.time(),'session_id':self.state['session_id'],'metrics':core.metrics(self.state),'body_controls':list(core.LABELS),'fingers':list(self.state['fingers']),'selected':self.selected(),'pending_preview':list(self.positions()),'errors':self.errors[-3:]})
    def process(self,cmd):
        action=cmd['action']
        if action=='select':
            self.A.set_selected_level_actors([self.controls[cmd['role']]])
        elif action=='view':self.view(cmd['view'])
        elif action=='overlay':
            for a in self.A.get_all_level_actors():
                if a.get_actor_label().startswith('D4 original '):a.set_is_temporarily_hidden_in_editor(not cmd['visible'])
        elif action=='preview_track':
            self.view('left hand' if cmd['side']=='l' else 'right hand')
            self.A.set_selected_level_actors([a for side,tid,a in self.track_actors if side==cmd['side'] and tid==cmd['track_id']])
        elif action=='record':
            selected=self.selected(); positions=self.positions()
            if not positions:raise ValueError('No changed positions to record')
            # Preview-generated dependents are not user moves. Record only directly selected controls.
            direct={n:p for n,p in positions.items() if n in selected}
            if not direct:raise ValueError('Select the control you moved, then record it')
            self.state=core.command(self.state,{'action':'move','positions':direct});self.redraw();core.export(self.state)
        elif action=='mirror':
            selected=self.selected()
            if len(selected)!=1 or ':' in selected[0] or not selected[0].endswith(('_l','_r')):raise ValueError('Select one paired body landmark')
            n=selected[0];p=self.controls[n].get_actor_location();other=n[:-1]+('r' if n[-1]=='l' else 'l');self.state=core.command(self.state,{'action':'move','positions':{n:[p.x,p.y,p.z],other:[-p.x,p.y,p.z]},'group':'explicit mirror placement'});self.redraw();core.export(self.state)
        elif action=='review':
            if self.positions():raise ValueError('Record or discard pending positions before review')
            roles=cmd.get('roles') or [n for n in self.selected() if ':' not in n]
            if not roles:raise ValueError('Choose a body control, group or assigned digit to review')
            self.state=core.command(self.state,dict(cmd,roles=roles));core.export(self.state);self.redraw()
        elif action in ['start','assign','finish']:
            if self.positions():raise ValueError('Record or discard pending positions first')
            self.state=core.command(self.state,cmd);core.export(self.state);self.redraw()
        elif action=='discard_preview':self.redraw()
        elif action=='save':
            if self.positions():raise ValueError('Record pending positions first')
            core.export(self.state);assert self.L.save_current_level()
        else:raise ValueError('unknown UI command')
        if action in ['select','view','overlay','preview_track','discard_preview','save'] and cmd.get('provenance')!='agent_ui_test':
            core.append_event(self.state,action,cmd);core.export(self.state)
        self.publish('Completed: '+action)
    def tick(self,dt):
        if time.monotonic()-self.last_poll<.25:return
        self.last_poll=time.monotonic()
        if not self.U.get_editor_world().get_path_name().startswith(MAP):
            unreal.unregister_slate_post_tick_callback(self.handle);self.publish('Stopped: correction map is not active');return
        for path in sorted((W/'Inbox').glob('*.json')):
            try:
                cmd=core.read(path)
                if cmd.get('session_id')!=self.state['session_id']:raise ValueError('stale panel session')
                self.process(cmd)
            except Exception as e:
                self.errors.append(str(e));self.publish('ERROR: '+str(e))
            finally:
                dest=W/'Processed'/path.name;dest.parent.mkdir(exist_ok=True);path.replace(dest)
        # Live preview propagates from selected controls without approval or interaction ledger edits.
        try:
            pending=self.positions();direct={n:p for n,p in pending.items() if n in self.selected()};sig=core.digest(direct)
            if direct and sig!=self.last_preview:
                preview=json.loads(json.dumps(self.state))
                for n,p in direct.items():
                    if ':' in n:key,end=n.rsplit(':',1);preview['fingers'][key][end+'_cm']=p
                    else:preview['body_overrides'][n]=p
                core.rebuild(preview);self.redraw(preview);self.last_preview=sig
            self.publish(core.read(W/'panel_status.json')['message'])
        except Exception as e:self.publish('Preview error: '+str(e))
start_tool()
