"""Technical native review utility. Human commands are never run by scene preparation.

Load this module in UE's Python console, then rigreview.open('Bill'|'Jill').
Movement is a proposal edit; only explicit accept() records human judgement.
No external Tk panel, final plugin/UI, native skeleton or skin is built here.
"""
import sys, json, math, importlib, builtins
from pathlib import Path
import unreal
sys.dont_write_bytecode=True
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4F';O=P/'Documentation/Phase4F';B='/Game/MetaHumanTo3DCharacter/Phase4F'
sys.path.insert(0,str(W))
import apose_review_core as core
importlib.reload(core)
class Review:
    def __init__(self):
        self.A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);self.L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);self.U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);self.T=unreal.AssetToolsHelpers.get_asset_tools()
        self.character=None;self.controls={};self.handle=None
    def configure(self,character):
        core.configure(character);self.character=character;self.base=B+'/'+character;self.map=self.base+'/Maps/L_'+character+'Review'
        self.state=core.rebuild(core.read(core.W/'session.json'))
    def material(self,name,colour,opacity=None):
        path=B+'/APoseReviewMaterials/M_'+name;m=unreal.load_asset(path)
        if m:return m
        m=self.T.create_asset('M_'+name,B+'/APoseReviewMaterials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_properties({'shading_model':unreal.MaterialShadingModel.MSM_UNLIT,'two_sided':True})
        ml=unreal.MaterialEditingLibrary;n=ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,0,0);n.set_editor_property('constant',unreal.LinearColor(*colour,1));ml.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        if opacity is not None:
            m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);n=ml.create_material_expression(m,unreal.MaterialExpressionConstant,0,150);n.set_editor_property('r',opacity);ml.connect_material_property(n,'',unreal.MaterialProperty.MP_OPACITY)
        ml.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m);return m
    def actor(self,label,mesh,position,scale,material=None,folder='Review'):
        a=self.A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*position),unreal.Rotator());a.set_actor_label(label);a.set_folder_path(folder);a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(*scale));a.set_actor_enable_collision(False)
        if material:a.static_mesh_component.set_material(0,material)
        return a
    def line(self,label,a,b,material,folder='Generated'):
        d=core.sub(b,a);length=core.norm(d)
        o=self.actor(label,self.cylinder,core.mul(core.add(a,b),.5),[.0025,.0025,max(.0001,length/100)],material,folder);o.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(unreal.Vector(*d)),False);return o
    def setup(self):
        self.sphere=unreal.load_asset('/Engine/BasicShapes/Sphere');self.cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder')
        self.mats={n:self.material(n,col,opacity) for n,col,opacity in [('Automatic',(.03,.7,.2),None),('Ambiguous',(.95,.45,.03),None),('Reviewed',(.05,.65,.8),None),('Moved',(.03,.3,1),None),('Generated',(.65,.12,.85),None),('Track',(.85,.04,.2),None),('Ghost',(.6,.7,.8),.22)]}
    def build(self,character):
        self.configure(character)
        if unreal.EditorAssetLibrary.does_asset_exist(self.map):
            assert not (core.O/'native_review_scene.json').exists() and not self.state['events'],'Do not replace a completed scene or recorded human review'
            assert self.L.load_level(self.map)
            for a in self.A.get_all_level_actors():self.A.destroy_actor(a)
        else:assert self.L.new_level(self.map)
        self.setup();assert self.U.get_editor_world().get_path_name().startswith(self.map)
        suffix='_FrameVerified' if character=='Bill' else ''
        mesh=unreal.load_asset(self.base+'/Geometry/SM_'+character+'180'+suffix);assert isinstance(mesh,unreal.StaticMesh)
        self.actor('F4 '+character+' original source - no anatomy accepted',mesh,[-235,0,0],[1,1,1],folder='Source')
        self.actor('F4 '+character+' review surface - canonical 180cm',mesh,[0,0,0],[1,1,1],self.mats['Ghost'],'ReviewSurface')
        for r in self.state['joints']:
            if r['role']=='root':continue
            self.actor('F4 CONTROL '+r['role'],self.sphere,r['position_cm'],[.013]*3,self.mats['Automatic' if r['status']=='automatically_accepted' else 'Ambiguous'],'Controls')
        for side,tracks in self.state['tracks'].items():
            for t in tracks:
                for i,(a,b) in enumerate(zip(core.track_points(t),core.track_points(t)[1:])):
                    o=self.line('F4 TRACK '+t['candidate_id']+' '+str(i),a,b,self.mats['Track'],'DigitTracks');o.set_is_temporarily_hidden_in_editor(True)
        light=self.A.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,220),unreal.Rotator(pitch=-40,yaw=-30,roll=0))
        light.set_actor_label('Phase4F review light');light.light_component.set_editor_property('intensity',3.0)
        self.bind_controls();self.redraw();self.view('front',record=False);assert self.L.save_current_level()
        core.save(core.O/'native_review_scene.json',{'map':self.map,'controls':list(self.controls),'source_mesh':mesh.get_path_name(),'no_anatomy_approved':not self.state['approvals'],'native_skeleton_built':False,'native_gizmo_review':True})
    def bind_controls(self):
        self.controls={a.get_actor_label()[11:]:a for a in self.A.get_all_level_actors() if a.get_actor_label().startswith('F4 CONTROL ')}
    def open(self,character):
        if self.handle is not None:unreal.unregister_slate_post_tick_callback(self.handle);self.handle=None
        if self.character and self.pending():raise ValueError('Record or discard current pending gizmo positions before switching character')
        self.configure(character);assert self.L.load_level(self.map);self.setup();self.bind_controls();self.redraw();self.view('front',record=False)
        self.handle=unreal.register_slate_post_tick_callback(self.tick)
        self.status();return self
    def active(self):
        if not self.character or not self.U.get_editor_world().get_path_name().startswith(self.map):raise ValueError('Open the correct Phase4F review map first')
    def pending(self):
        result={}
        for n,a in self.controls.items():
            p=a.get_actor_location();p=[p.x,p.y,p.z]
            old=self.state['fingers'][n.split(':')[0]][n.split(':')[1]+'_cm'] if ':' in n else next(r['position_cm'] for r in self.state['joints'] if r['role']==n)
            if core.norm(core.sub(p,old))>.001:result[n]=p
        return result
    def event(self,kind,details):
        if self.state['trial_started_at'] is not None and self.state['trial_finished_at'] is None:
            core.append_event(self.state,kind,details);core.export(self.state)
    def select(self,role):
        self.active();self.A.set_selected_level_actors([self.controls[role]]);self.event('select',{'role':role})
    def start(self):
        self.active();self.state=core.command(self.state,{'action':'start'});core.export(self.state);self.status()
    def record(self):
        self.active();selected=list(self.A.get_selected_level_actors());changes={n:p for n,p in self.pending().items() if self.controls[n] in selected}
        if not changes:raise ValueError('Select the directly moved control and move its gizmo before recording')
        self.state=core.command(self.state,{'action':'move','positions':changes});core.export(self.state);self.redraw();self.status()
    def accept(self,roles,category='anatomical_front_side_review'):
        self.active()
        if self.pending():raise ValueError('Record or discard pending gizmo placements before acceptance')
        if isinstance(roles,str):roles=core.GROUPS.get(roles,[roles])
        self.state=core.command(self.state,{'action':'review','roles':roles,'judgement':'accept','category':category});core.export(self.state);self.redraw();self.status()
    def unresolved(self,roles,category='anatomically_ambiguous'):
        self.active()
        if isinstance(roles,str):roles=core.GROUPS.get(roles,[roles])
        self.state=core.command(self.state,{'action':'review','roles':roles,'judgement':'unresolved','category':category});core.export(self.state);self.redraw()
    def identify(self,side,digit,number):
        self.active()
        if self.pending():raise ValueError('Record or discard pending positions first')
        tid='digit_branch_'+str(number)+'_'+side
        self.state=core.command(self.state,{'action':'assign','side':side,'digit':digit,'track_id':tid});core.export(self.state);self.redraw();self.status()
    def track(self,side,number):
        self.active();tid='digit_branch_'+str(number)+'_'+side
        selected=[]
        for a in self.A.get_all_level_actors():
            if a.get_actor_label().startswith('F4 TRACK '):
                match=a.get_actor_label().startswith('F4 TRACK '+tid+' ');a.set_is_temporarily_hidden_in_editor(not match)
                if match:selected.append(a)
        if not selected:raise ValueError('Unknown digit track')
        self.A.set_selected_level_actors(selected);self.view('hand_'+side+'_top');self.event('preview_track',{'side':side,'track_id':tid})
    def discard(self):self.active();self.redraw()
    def finish(self):
        self.active()
        if self.pending():raise ValueError('Record or discard pending positions before finishing')
        self.state=core.command(self.state,{'action':'finish'});core.export(self.state);assert self.L.save_current_level();self.status()
    def save(self):
        self.active()
        if self.pending():raise ValueError('Record pending changes before saving')
        core.export(self.state);assert self.L.save_current_level()
    def status(self):print(json.dumps(core.metrics(self.state),indent=2))
    def redraw(self):
        for n,a in self.controls.items():
            if ':' in n:p=self.state['fingers'][n.split(':')[0]][n.split(':')[1]+'_cm'];mat=self.mats['Ambiguous']
            else:
                r=next(r for r in self.state['joints'] if r['role']==n);p=r['position_cm'];mat=self.mats['Moved' if r['status']=='manually_corrected' else 'Automatic' if r['status']=='automatically_accepted' else 'Ambiguous']
                if n in self.state['approvals']:mat=self.mats['Reviewed']
            a.set_actor_location(unreal.Vector(*p),False,False);a.static_mesh_component.set_material(0,mat)
        for a in self.A.get_all_level_actors():
            if a.get_actor_label().startswith('F4 GENERATED '):self.A.destroy_actor(a)
        rows={r['role']:r for r in self.state['joints']}
        for n,r in rows.items():
            if r['parent_role']:self.line('F4 GENERATED '+n,rows[r['parent_role']]['position_cm'],r['position_cm'],self.mats['Generated'])
        for key,f in self.state['fingers'].items():
            for end in ['root','tip']:
                n=key+':'+end
                if n not in self.controls:self.controls[n]=self.actor('F4 CONTROL '+n,self.sphere,f[end+'_cm'],[.009]*3,self.mats['Ambiguous'],'FingerControls')
            pts=[rows['hand_'+f['side']]['position_cm']]+f['phalanges_cm']+[f['tip_cm']]
            for i,(a,b) in enumerate(zip(pts,pts[1:])):self.line('F4 GENERATED '+key+' '+str(i),a,b,self.mats['Generated'])
    def view(self,name='front',record=True):
        self.active();views={'front':([0,380,100],[0,-90,0]),'side':([320,0,100],[0,180,0]),'pelvis':([0,145,100],[0,-90,0]),'arms':([0,295,140],[0,-90,0]),'feet':([120,2,17],[0,180,0])}
        if name.startswith('hand_'):
            side=name.split('_')[1];ts=self.state['tracks'][side];pts=[p for t in ts for p in core.track_points(t)];centre=[sum(p[i] for p in pts)/len(pts) for i in range(3)]
            pos=[centre[0],centre[1],centre[2]+48] if name.endswith('top') else [centre[0],centre[1]+48,centre[2]];rot=[-90,-90,0] if name.endswith('top') else [0,-90,0]
        else:pos,rot=views[name]
        self.U.set_level_viewport_camera_info(unreal.Vector(*pos),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
        if record:self.event('view',{'view':name})
    def tick(self,dt):
        # Diagnostic heartbeat only. No automatic movement or human approval.
        if not self.U.get_editor_world().get_path_name().startswith(self.map):return
        req=W/'apose_review_agent_request.json'
        if req.exists():
            data=json.loads(req.read_text())
            if data.get('token')!=getattr(self,'last_agent_token',None):
                self.last_agent_token=data['token'];action=data['action']
                # Agent operations deliberately cannot call accept/identify/start/record/finish.
                if action=='view':self.view(data['view'],record=False)
                elif action=='open':self.open(data['character'])
                elif action=='snapshot':pass
                else:raise ValueError('Agent review harness is read-only except view/map selection')
                core.save(W/'apose_review_agent_response.json',{'token':data['token'],'character':self.character,'pending':self.pending(),'metrics':core.metrics(self.state),'map':self.map})
rigreview=Review()
builtins.phase4f_review=rigreview
if __name__=='__main__':
    for character in ['John','Jane']:rigreview.build(character)
    print('PHASE4F_REVIEW_SCENES_READY')
