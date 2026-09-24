import {spawn} from "node:child_process";
import {mkdirSync,writeFileSync} from "node:fs";
import {pathToFileURL} from "node:url";
import {tmpdir} from "node:os";
import {join} from "node:path";

const source=process.argv[2];
const output=process.argv[3]||join(process.cwd(),"reference-frames");
if(!source)throw new Error("Pass the reference video path");
mkdirSync(output,{recursive:true});
const chrome="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const port=9500+Math.floor(Math.random()*300);
const profile=join(tmpdir(),`codex-video-inspect-${Date.now()}`);
const browser=spawn(chrome,["--headless=new","--no-first-run","--disable-extensions",`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,"--window-size=1600,1000","about:blank"],{stdio:"ignore",windowsHide:true});
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function endpoint(path){
  for(let attempt=0;attempt<80;attempt++){
    try{const response=await fetch(`http://127.0.0.1:${port}${path}`);if(response.ok)return response.json();}catch{}
    await wait(100);
  }
  throw new Error("Chrome DevTools endpoint did not start");
}

try{
  await endpoint("/json/version");
  const page=await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(pathToFileURL(source).href)}`,{method:"PUT"})).json();
  const socket=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.addEventListener("open",resolve,{once:true});socket.addEventListener("error",reject,{once:true});});
  let id=0;const pending=new Map();
  socket.addEventListener("message",event=>{const message=JSON.parse(event.data);if(message.id&&pending.has(message.id)){const item=pending.get(message.id);pending.delete(message.id);message.error?item.reject(message.error):item.resolve(message.result);}});
  const send=(method,params={})=>new Promise((resolve,reject)=>{const callId=++id;pending.set(callId,{resolve,reject});socket.send(JSON.stringify({id:callId,method,params}));});
  const evaluate=async expression=>(await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true})).result.value;
  await send("Page.enable");await send("Runtime.enable");await wait(1500);
  const meta=await evaluate(`(async()=>{const v=document.querySelector('video');if(!v)return null;if(v.readyState<1)await new Promise(r=>v.addEventListener('loadedmetadata',r,{once:true}));v.pause();return {duration:v.duration,width:v.videoWidth,height:v.videoHeight};})()`);
  if(!meta)throw new Error("Chrome did not create a video element");
  const times=Array.from({length:9},(_,index)=>meta.duration*index/8);
  for(let index=0;index<times.length;index++){
    const time=Math.min(times[index],Math.max(0,meta.duration-.04));
    await evaluate(`(async()=>{const v=document.querySelector('video');v.currentTime=${time};await new Promise(r=>v.addEventListener('seeked',r,{once:true}));})()`);
    await wait(80);
    const {data}=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    writeFileSync(join(output,`${String(index+1).padStart(2,"0")}-${time.toFixed(2)}s.png`),Buffer.from(data,"base64"));
  }
  console.log(JSON.stringify({meta,output},null,2));socket.close();
}finally{browser.kill();}
