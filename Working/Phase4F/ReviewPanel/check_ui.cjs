// Isolated UI behaviour checks. Fake DOM and fake transport; no real commands.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, 'panel.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let current = JSON.parse(fs.readFileSync(path.join(__dirname,
  '../../../Documentation/Phase4F/ReviewPanel/panel_status_at_attachment.json'), 'utf8'));
const sessionPath = path.join(__dirname, '../John/session.json');
const originalSession = fs.readFileSync(sessionPath, 'utf8');
current.connected = true;
const elements = new Map();
function element(id) {
  const classes = new Set();
  const e = {id, value:'', textContent:'', hidden:false, disabled:false, dataset:{},
    classList:{toggle:(name,on)=>on?classes.add(name):classes.delete(name)},
    replaceChildren(...children){this.children=children;this.value=children[0]?.value||''}};
  elements.set(id, e);
  return e;
}
for (const match of html.matchAll(/id="([^"]+)"/g)) element(match[1]);
const buttons = [...html.matchAll(/<button([^>]*)>/g)].map((m,i)=> {
  const id = /id="([^"]+)"/.exec(m[1])?.[1];
  const e = id ? elements.get(id) : element('button'+i);
  for(const data of m[1].matchAll(/data-([a-z]+)="([^"]+)"/g))e.dataset[data[1]]=data[2];
  return e;
});
elements.get('side').value='l';elements.get('endpoint').value='root';
const commands=[],storage=new Map();let result={ok:true};
const context = vm.createContext({console,Date,JSON,Number,Object,String,RegExp,Error,
  document:{documentElement:{dataset:{}},getElementById:id=>elements.get(id),
    createElement:()=>({value:'',textContent:''}),querySelectorAll:q=>q==='button'?buttons:
      q==='select'?[...elements.values()].filter(x=>['step','role','group','side','track','digit','endpoint'].includes(x.id)):
      buttons.filter(x=>x.dataset.action)},
  localStorage:{getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)},
  setInterval:()=>0,setTimeout:fn=>{fn();return 0},
  fetch:async (url,options)=>{
    if(url==='/api/status')return {json:async()=>structuredClone(current)};
    if(url.startsWith('/api/result/'))return {status:200,json:async()=>result};
    const data=JSON.parse(options.body);commands.push(data);result={ok:true};
    if(data.action==='accept'){
      current.metrics.review_commands++;
      current.metrics.currently_accepted_human_roles.push(data.args.role);
      current.metrics.unresolved_body_roles=current.metrics.unresolved_body_roles.filter(n=>n!==data.args.role);
      current.metrics.unresolved_finger_chains=current.metrics.unresolved_finger_chains.filter(n=>n!==data.args.role);
    }
    if(data.action==='step')current.selected_step=data.args.role;
    if(data.action==='identify')current.fingers[data.args.digit+'_'+data.args.side]={track_id:'digit_branch_'+data.args.number+'_'+data.args.side};
    return {ok:true,json:async()=>({id:'isolated-ui-check'})};
  }
});
async function invoke(code){
  const value = await vm.runInContext(code,context);
  // Browser onclick handlers need not return their asynchronous transport promise.
  await new Promise(resolve=>setImmediate(resolve));
  return value;
}
(async()=>{
  for(const script of scripts)vm.runInContext(script,context);
  await invoke('refresh()');
  assert.equal(elements.get('start').disabled,true);
  assert.equal(elements.get('reviews').textContent,1);
  assert.match(elements.get('unchanged').textContent,/Pelvis/);
  assert.equal(commands.length,0);
  await invoke("$('accept').onclick()");
  assert.deepEqual(commands.map(x=>x.action),['accept','step']);
  assert.equal(commands[0].args.role,'neck_01');
  assert.equal(commands[1].args.role,'head');
  assert.equal(elements.get('stepTitle').textContent,'Head pivot');
  assert.equal(elements.get('reviews').textContent,2);
  await invoke("$('adjust').onclick()");
  assert.equal(elements.get('adjustHelp').hidden,false);
  await invoke('refresh()');
  assert.equal(elements.get('adjustHelp').hidden,false);
  const before=commands.length;
  await invoke("navigate(state.steps.findIndex(s=>s.kind==='summary'))");
  await invoke('refresh()');
  assert.equal(elements.get('stepTitle').textContent,'Review summary');
  assert.equal(elements.get('accept').disabled,true);
  assert.equal(commands.length,before);
  await invoke("navigate(state.steps.findIndex(s=>s.role==='thumb_l'))");
  assert.equal(elements.get('digit').value,'');
  assert.equal(elements.get('track').value,'');
  assert.equal(elements.get('adjust').disabled,true);
  const beforeIdentity=commands.length;
  await invoke("$('identify').onclick()");
  assert.equal(commands.length,beforeIdentity);
  elements.get('track').value='4';elements.get('digit').value='thumb';
  await invoke("$('identify').onclick()");
  assert.deepEqual(commands.at(-1).args,{side:'l',number:4,digit:'thumb'});
  assert.equal(elements.get('selectEndpoint').disabled,false);
  await invoke("$('theme').onclick()");
  assert.equal(context.document.documentElement.dataset.theme,'dark');
  vm.runInContext(scripts[0],context);
  assert.equal(context.document.documentElement.dataset.theme,'dark');
  current.connected=false;await invoke('refresh()');
  assert.equal(elements.get('accept').disabled,true);
  assert.equal(elements.get('step').disabled,true);
  assert.equal(fs.readFileSync(sessionPath,'utf8'), originalSession);
  console.log('UI checks passed: passive resume, accept/advance, refresh counts, adjust help, summary stability, explicit identity, theme persistence, disconnect guards. No real command submitted.');
})().catch(error=>{console.error(error);process.exitCode=1});
