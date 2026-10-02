"""Small local Phase4D control panel. Anatomical judgement is always user input."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys,time,uuid,json,os
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
W=core.W
if (W/'Runtime/tcl8.6/init.tcl').exists():
    os.environ['TCL_LIBRARY']=str(W/'Runtime/tcl8.6')
    os.environ['TK_LIBRARY']=str(W/'Runtime/tk8.6')
class Panel:
    def __init__(self,layout_check=False):
        self.root=tk.Tk();self.root.title('Phase4D - Lara landmark correction');self.root.geometry('520x820');self.root.configure(bg='#f5f7fa');self.root.attributes('-topmost',True)
        style=ttk.Style();style.theme_use('clam');style.configure('TFrame',background='#f5f7fa');style.configure('TLabel',background='#f5f7fa',foreground='#172433');style.configure('TButton',padding=5)
        f=ttk.Frame(self.root,padding=12);f.pack(fill='both',expand=True)
        ttk.Label(f,text='Lara: guided landmark trial',font=('Segoe UI',15,'bold')).pack(anchor='w')
        ttk.Label(f,text='Green automatic | Amber review | Blue moved\nCyan reviewed | Purple generated / dependent').pack(anchor='w',pady=8)
        ttk.Label(f,text='Select a point, drag its UE gizmo, then Record placement.\nInspect front AND side before accepting anatomy.').pack(anchor='w')
        self.button(f,'Start / resume measured trial',{'action':'start'})
        row=ttk.Frame(f);row.pack(fill='x');self.body=tk.StringVar(value='Pelvis centre');self.lookup={label:n for n,label in core.LABELS.items()};ttk.Combobox(row,textvariable=self.body,values=list(self.lookup),state='readonly',width=36).pack(side='left');ttk.Button(row,text='Select in UE',command=lambda:self.send({'action':'select','role':self.lookup[self.body.get()]})).pack(side='left')
        row=ttk.Frame(f);row.pack(fill='x',pady=5)
        self.button(row,'Record placement',{'action':'record'},side='left');self.button(row,'Mirror pair',{'action':'mirror'},side='left');self.button(row,'Discard preview',{'action':'discard_preview'},side='left')
        self.view=tk.StringVar(value='front');row=ttk.Frame(f);row.pack(fill='x');ttk.Combobox(row,textvariable=self.view,values=['front','side','pelvis','arms','knees','feet','left hand','right hand'],state='readonly',width=28).pack(side='left');ttk.Button(row,text='View',command=lambda:self.send({'action':'view','view':self.view.get()})).pack(side='left')
        self.overlay=tk.BooleanVar();ttk.Checkbutton(f,text='Show original automatic overlay',variable=self.overlay,command=lambda:self.send({'action':'overlay','visible':self.overlay.get()})).pack(anchor='w')
        ttk.Separator(f).pack(fill='x',pady=8)
        ttk.Label(f,text='Anatomical review (explicit judgement)').pack(anchor='w')
        self.category=tk.StringVar(value='actual anatomical misplacement');ttk.Combobox(f,textvariable=self.category,values=['actual anatomical misplacement','skeleton pivot convention','reference-pose difference','target correspondence failure','geometry/clothing ambiguity','position acceptable after visual review'],state='readonly',width=48).pack(anchor='w')
        self.group=tk.StringVar(value='Selected body control');ttk.Combobox(f,textvariable=self.group,values=['Selected body control']+list(core.GROUPS),state='readonly',width=48).pack(anchor='w',pady=4)
        row=ttk.Frame(f);row.pack(fill='x');ttk.Button(row,text='Accept inspected point / group',command=lambda:self.review('accept')).pack(side='left');ttk.Button(row,text='Keep unresolved',command=lambda:self.review('unresolved')).pack(side='left')
        ttk.Separator(f).pack(fill='x',pady=8);ttk.Label(f,text='Finger correspondence (each hand independently)').pack(anchor='w')
        row=ttk.Frame(f);row.pack(fill='x');self.side=tk.StringVar(value='l');self.digit=tk.StringVar(value='thumb');self.track=tk.StringVar(value='1')
        for var,values,width in [(self.side,['l','r'],5),(self.digit,list(core.DIGITS),10),(self.track,list('12345'),5)]:ttk.Combobox(row,textvariable=var,values=values,state='readonly',width=width).pack(side='left',padx=3)
        ttk.Button(row,text='Identify track',command=lambda:self.send({'action':'assign','side':self.side.get(),'digit':self.digit.get(),'track_id':'digit_branch_'+self.track.get()+'_'+self.side.get()})).pack(side='left')
        ttk.Button(f,text='Highlight selected track in UE',command=lambda:self.send({'action':'preview_track','side':self.side.get(),'track_id':'digit_branch_'+self.track.get()+'_'+self.side.get()})).pack(anchor='w')
        ttk.Label(f,text='Pink lines = detected tracks (numbered in Outliner).\nChoose digit identity; generated joints follow the track.\nMove root/tip only if needed, then Record placement.').pack(anchor='w',pady=4)
        row=ttk.Frame(f);row.pack(fill='x')
        for end in ['root','tip']:ttk.Button(row,text='Select '+end,command=lambda e=end:self.send({'action':'select','role':self.digit.get()+'_'+self.side.get()+':'+e})).pack(side='left')
        ttk.Button(row,text='Accept inspected digit chain',command=lambda:self.send({'action':'review','roles':[self.digit.get()+'_'+self.side.get()],'judgement':'accept','category':self.category.get()})).pack(side='left')
        ttk.Separator(f).pack(fill='x',pady=8);row=ttk.Frame(f);row.pack(fill='x');self.button(row,'Save trial',{'action':'save'},side='left');self.button(row,'Finish measured trial',{'action':'finish'},side='left')
        self.message=tk.StringVar(value='Waiting for UE tool');ttk.Label(f,textvariable=self.message,wraplength=475).pack(anchor='w',pady=8);self.summary=tk.StringVar();ttk.Label(f,textvariable=self.summary,wraplength=475).pack(anchor='w');ttk.Label(f,text='No skeleton is built by this panel. Validation runs separately.\nClosing this panel retains the trial; reopen to continue.',wraplength=475).pack(anchor='w',pady=6)
        self.root.update_idletasks()
        # Size from the actual requested content so Finish/status remain visible.
        requested=self.root.winfo_reqheight();available=self.root.winfo_screenheight()-70
        self.root.geometry(f'580x{min(available,max(820,requested+24))}')
        self.root.update_idletasks()
        if layout_check:
            core.save(core.O/'panel_layout_validation.json',{'requested_content_height':requested,'window_height':self.root.winfo_height(),'screen_height':self.root.winfo_screenheight(),'content_fits':requested<=self.root.winfo_height(),'all_controls_constructed':True,'native_screenshot_verified':False,'synthetic_only':True})
            self.root.destroy();return
        self.refresh();self.root.mainloop()
    def button(self,parent,text,cmd,side='top'):
        ttk.Button(parent,text=text,command=lambda:self.send(cmd)).pack(side=side,pady=4)
    def send(self,cmd):
        try:
            status=core.read(W/'panel_status.json')
            if time.time()-status['heartbeat_epoch']>5:raise ValueError('UE tool is not responding. Reopen the correction map and run ue_tool.py.')
            path=W/'Inbox'/(str(time.time_ns())+'_'+uuid.uuid4().hex+'.json');core.save(path,dict(cmd,session_id=status['session_id']))
        except Exception as e:messagebox.showerror('Phase4D',str(e),parent=self.root)
    def review(self,judgement):
        roles=core.GROUPS.get(self.group.get())
        self.send({'action':'review','roles':roles,'judgement':judgement,'category':self.category.get()})
    def refresh(self):
        try:
            s=core.read(W/'panel_status.json');self.message.set(s['message']);m=s['metrics'];self.summary.set(f"Trial: {m['trial_status']}\nRecorded commands: {m['recorded_user_commands']} | Moved landmarks: {m['landmarks_actually_moved']}\nUnresolved body roles: {len(m['unresolved_body_roles'])} | Finger chains: {len(m['unresolved_finger_chains'])}\nPending unrecorded controls: {', '.join(s['pending_preview']) or 'none'}")
        except Exception:self.message.set('Waiting for UE tool')
        self.root.after(500,self.refresh)
if __name__=='__main__':Panel(layout_check='--layout-check' in sys.argv)
