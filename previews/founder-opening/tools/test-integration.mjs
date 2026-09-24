import {spawn} from 'node:child_process';
import {mkdtempSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const profile=mkdtempSync(join(tmpdir(),'founder-integrated-'));
const port=9873;
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--no-first-run','--use-angle=swiftshader','--enable-webgl',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`],{stdio:'ignore',windowsHide:true});
const wait=ms=>new Promise(r=>setTimeout(r,ms));
try{
 let tab;
 for(let i=0;i<60;i++){try{tab=await(await fetch(`http://127.0.0.1:${port}/json/new?http://127.0.0.1:4173/founder.html`,{method:'PUT'})).json();break;}catch{await wait(100);}}
 const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));
 let id=0;const pending=new Map();const errors=[];
 ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m.result);pending.delete(m.id);}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);});
 const send=(method,params={})=>new Promise(r=>{pending.set(++id,r);ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true})).result.value;
 await send('Runtime.enable');await send('Page.enable');
 for(const width of [1440,390]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});await wait(4000);
  console.log(JSON.stringify(await evaluate(`(()=>{const f=document.querySelector('iframe');return {width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,openingHeight:f.getBoundingClientRect().height,ready:f.contentDocument.querySelector('[data-portrait]').classList.contains('is-ready'),touch:getComputedStyle(f.contentDocument.querySelector('.portrait-stage')).touchAction,story:!!document.querySelector('#founder-story')}})()`)));
  if(width===1440){const shot=await send('Page.captureScreenshot',{format:'png'});writeFileSync(join(profile,'desktop.png'),Buffer.from(shot.data,'base64'));console.log(join(profile,'desktop.png'));}
  await evaluate("document.querySelector('.founder-opening__continue').click()");await wait(1000);console.log('scroll',await evaluate('scrollY'));await evaluate('scrollTo(0,0)');
 }
 console.log('errors',JSON.stringify(errors));ws.close();
}finally{browser.kill();}
