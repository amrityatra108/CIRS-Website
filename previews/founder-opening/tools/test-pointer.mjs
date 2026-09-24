import {spawn} from "node:child_process";
import {mkdirSync,writeFileSync} from "node:fs";
import {join} from "node:path";
import {tmpdir} from "node:os";

const chrome="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const port=9300+Math.floor(Math.random()*500);
const profile=join(tmpdir(),`codex-founder-test-${Date.now()}`);
const output=process.argv[2]||join(process.cwd(),"captures");
mkdirSync(output,{recursive:true});

const browser=spawn(chrome,["--headless=new","--no-first-run","--disable-extensions","--use-angle=swiftshader","--enable-webgl","--ignore-gpu-blocklist",`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,"--window-size=1440,900","about:blank"],{stdio:"ignore",windowsHide:true});
const wait=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));

async function endpoint(path){
  for(let attempt=0;attempt<80;attempt++){
    try{const response=await fetch(`http://127.0.0.1:${port}${path}`);if(response.ok)return response.json();}catch{}
    await wait(100);
  }
  throw new Error("Chrome DevTools endpoint did not start");
}

try{
  await endpoint("/json/version");
  const tabResponse=await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent("http://127.0.0.1:4173/previews/founder-opening/")}`,{method:"PUT"});
  const tab=await tabResponse.json();
  const socket=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.addEventListener("open",resolve,{once:true});socket.addEventListener("error",reject,{once:true});});
  let id=0;
  const pending=new Map();
  socket.addEventListener("message",event=>{
    const message=JSON.parse(event.data);
    if(message.id&&pending.has(message.id)){const {resolve,reject}=pending.get(message.id);pending.delete(message.id);message.error?reject(message.error):resolve(message.result);}
  });
  const send=(method,params={})=>new Promise((resolve,reject)=>{const callId=++id;pending.set(callId,{resolve,reject});socket.send(JSON.stringify({id:callId,method,params}));});
  const evaluate=async(expression)=>(await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true})).result.value;
  const screenshot=async(name)=>{const {data}=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});writeFileSync(join(output,name),Buffer.from(data,"base64"));};

  await send("Page.enable");
  await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride",{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await wait(3500);

  await screenshot("01-initial.png");
  await evaluate("scrollTo(0,180)");
  await wait(350);
  await screenshot("02-scroll-only.png");
  await evaluate("scrollTo(0,0)");
  await wait(250);

  const rect=await evaluate("(()=>{const r=document.querySelector('[data-portrait]').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,ready:document.querySelector('[data-portrait]').classList.contains('is-ready')}})()");
  await evaluate(`(()=>{const node=document.querySelector('[data-portrait]');node.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:${rect.x+rect.width*.49},clientY:${rect.y+rect.height*.27}}));})()`);
  await wait(160);
  await screenshot("03-mouse-fallback.png");
  await wait(650);
  await screenshot("03b-wave-later.png");
  await wait(550);
  const points=[[.48,.25],[.5,.3],[.47,.37],[.53,.43],[.48,.49]];
  await send("Input.dispatchMouseEvent",{type:"mouseMoved",x:rect.x+rect.width*points[0][0],y:rect.y+rect.height*points[0][1],button:"none",pointerType:"mouse"});
  await wait(120);
  await screenshot("03-forehead-only.png");
  for(const [px,py] of points.slice(1)){await send("Input.dispatchMouseEvent",{type:"mouseMoved",x:rect.x+rect.width*px,y:rect.y+rect.height*py,button:"none",pointerType:"mouse"});await wait(70);}
  await screenshot("04-pointer-trail.png");

  await wait(1300);
  await screenshot("05-stopped-inside.png");
  await send("Input.dispatchMouseEvent",{type:"mouseMoved",x:rect.x+rect.width*.35,y:rect.y+rect.height*.68,button:"none",pointerType:"mouse"});
  await wait(140);
  await screenshot("06-shoulder-robe.png");
  await send("Input.dispatchMouseEvent",{type:"mouseMoved",x:rect.x+rect.width*.5,y:rect.y+rect.height*.36,button:"none",pointerType:"mouse"});
  await wait(90);

  await send("Input.dispatchMouseEvent",{type:"mouseMoved",x:20,y:860,button:"none",pointerType:"mouse"});
  await wait(1500);
  await screenshot("07-after-leave.png");
  await evaluate("scrollTo(0,220)");
  await wait(350);
  await screenshot("08-scroll-after-leave.png");

  await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await send("Page.reload",{ignoreCache:true});
  await wait(3500);
  const mobileRect=await evaluate("(()=>{const r=document.querySelector('[data-portrait]').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()");
  const touchPoint=(px,py)=>({x:mobileRect.x+mobileRect.width*px,y:mobileRect.y+mobileRect.height*py,radiusX:4,radiusY:4,force:1,id:1});
  await send("Input.dispatchTouchEvent",{type:"touchStart",touchPoints:[touchPoint(.48,.28)]});
  for(const point of [[.5,.33],[.47,.4],[.52,.47]]){await send("Input.dispatchTouchEvent",{type:"touchMove",touchPoints:[touchPoint(...point)]});await wait(80);}
  await screenshot("09-mobile-touch.png");
  await send("Input.dispatchTouchEvent",{type:"touchEnd",touchPoints:[]});
  await wait(1500);
  await screenshot("10-mobile-release.png");
  console.log(JSON.stringify({ready:rect.ready,output},null,2));
  socket.close();
}finally{
  browser.kill();
}
