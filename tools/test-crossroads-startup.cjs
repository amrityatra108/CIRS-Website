// Record compositor frames from navigation, rather than screenshots after load.
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.CIRS_BROWSER_DIR?path.join(process.env.CIRS_BROWSER_DIR,'node_modules/playwright-core'):'playwright-core');
const base=process.env.CIRS_PREVIEW_URL||'http://127.0.0.1:8878';
const output=process.env.CIRS_QA_DIR||'/tmp/cirs-startup-qa';
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[];
 for(const mobile of [false,true]){
  const name=mobile?'mobile':'desktop',dir=path.join(output,name);fs.mkdirSync(dir,{recursive:true});
  const context=await browser.newContext({viewport:mobile?{width:390,height:844}:{width:1440,height:900}});
  const page=await context.newPage();
  await page.addInitScript(()=>{window.startupSamples=[];function sample(){const i=document.querySelector('[data-crossroads-intro]'),c=i?.querySelector('.crossroads-intro__content'),v=i?.querySelector('video');if(c){const s=getComputedStyle(c);window.startupSamples.push({time:performance.now(),pending:i.hasAttribute('data-crossroads-intro-pending'),playing:i.hasAttribute('data-crossroads-intro-opening-playing'),visible:s.visibility!=='hidden'&&Number(s.opacity)>0,ready:v.readyState});}requestAnimationFrame(sample)}requestAnimationFrame(sample)});
  await page.route('**/crossroads-intro.js*',async r=>{await delay(1600);await r.continue()});
  await page.route('**/crossroads-opening*.mp4',async r=>{await delay(900);await r.continue()});
  const cdp=await context.newCDPSession(page);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
  await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:80,downloadThroughput:5000000,uploadThroughput:1000000});
  let count=0;const frames=[];
  cdp.on('Page.screencastFrame',async e=>{const file=`frame-${String(count++).padStart(3,'0')}.png`;fs.writeFileSync(path.join(dir,file),Buffer.from(e.data,'base64'));frames.push({file,timestamp:e.metadata.timestamp});await cdp.send('Page.screencastFrameAck',{sessionId:e.sessionId}).catch(()=>{})});
  await cdp.send('Page.startScreencast',{format:'png',everyNthFrame:1});
  await page.goto(base+'/crossroads.html',{waitUntil:'commit'});
  await page.waitForFunction(()=>document.querySelector('[data-crossroads-intro-opening]')?.currentTime>.15,null,{timeout:15000});
  await cdp.send('Page.stopScreencast');
  const samples=await page.evaluate(()=>window.startupSamples);
  const pending=samples.filter(s=>s.pending&&!s.playing);assert.ok(pending.length>10);assert.equal(pending.filter(s=>s.visible).length,0,'No visible page lockup before playback');
  fs.writeFileSync(path.join(dir,'frames.json'),JSON.stringify(frames,null,2));
  results.push({test:name+' cold cache/throttled first paint',pendingSamples:pending.length,exposedSamples:0,compositorFrames:count});
  await page.reload({waitUntil:'commit'});
  await page.waitForFunction(()=>document.querySelector('[data-crossroads-intro-opening]')?.currentTime>.15,null,{timeout:15000});
  assert.equal(await page.evaluate(()=>window.startupSamples.some(s=>s.pending&&!s.playing&&s.visible)),false);
  results.push({test:name+' reload',passed:true});
  await page.locator('[data-crossroads-intro-skip]').click();
  await page.goto(base+'/index.html');await page.goBack({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('[data-crossroads-intro]')?.hasAttribute('data-crossroads-intro-settled'));
  assert.equal(await page.locator('[data-crossroads-intro-opening]').evaluate(v=>v.paused),true);
  assert.equal(await page.evaluate(()=>document.documentElement.classList.contains('crossroads-intro-scroll-locked')),false);
  results.push({test:name+' history return',passed:true});await context.close();
 }
 // Real streamed HTML: the head reaches the browser, then the body is held
 // until after the fallback deadline. The external controller is unavailable.
 {
  const http=require('node:http');
  const html=fs.readFileSync(path.join(__dirname,'../crossroads.html'),'utf8').replace('<head>','<head><base href="'+base+'/">');
  const cut=html.indexOf('</head>')+7;
  const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html'});res.write(html.slice(0,cut));setTimeout(()=>res.end(html.slice(cut)),6600)});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const context=await browser.newContext();const page=await context.newPage();
  await page.route('**/crossroads-intro.js*',r=>r.abort());
  await page.goto('http://127.0.0.1:'+server.address().port+'/',{waitUntil:'commit'});
  await page.locator('.crossroads-intro__content').waitFor({state:'visible',timeout:10000});
  assert.equal(await page.evaluate(()=>window.__crossroadsStartupExpired),true);
  assert.equal(await page.locator('[data-crossroads-intro]').evaluate(i=>i.hasAttribute('data-crossroads-intro-pending')),false);
  assert.equal(await page.evaluate(()=>document.documentElement.classList.contains('crossroads-intro-scroll-locked')),false);
  results.push({test:'streamed body after six-second deadline with blocked controller',passed:true});
  await context.close();await new Promise(resolve=>server.close(resolve));
 }
 for(const mode of ['script-failure','late-script','media-failure','no-js','reduced-motion']){
  const context=await browser.newContext({javaScriptEnabled:mode!=='no-js',reducedMotion:mode==='reduced-motion'?'reduce':'no-preference'});const page=await context.newPage();
  if(mode==='script-failure')await page.route('**/crossroads-intro.js*',r=>r.abort());
  if(mode==='late-script')await page.route('**/crossroads-intro.js*',async r=>{await delay(7200);await r.continue()});
  if(mode==='media-failure')await page.route('**/crossroads-opening*.mp4',r=>r.abort());
  await page.goto(base+'/crossroads.html',{waitUntil:'commit'});
  await page.locator('.crossroads-intro__content').waitFor({state:'visible',timeout:10000});
  if(mode==='late-script')await page.waitForFunction(()=>window.__crossroadsIntroReady===true);
  assert.equal(await page.evaluate(()=>document.documentElement.classList.contains('crossroads-intro-scroll-locked')),false);
  assert.equal(await page.locator('[data-crossroads-intro-opening]').evaluate(v=>v.paused),true);
  await page.locator('[data-crossroads-intro-enter]').click();
  // Node-side polling also works when page JavaScript (including rAF) is disabled.
  let reached=false;for(let attempt=0;attempt<40;attempt++){reached=await page.evaluate(()=>Math.abs(document.getElementById('crossroads-main').getBoundingClientRect().top)<150);if(reached)break;await delay(100)}assert.ok(reached,mode+' Enter reaches archive');
  results.push({test:mode+' bounded visible fallback and Enter',passed:true});console.log('PASS '+mode);await context.close();
 }
 fs.writeFileSync(path.join(output,'startup-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
