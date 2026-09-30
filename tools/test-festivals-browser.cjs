// Run tools/serve-preview.py first. Exercises the real video and fallbacks.
const path=require("node:path");
const {chromium}=require(process.env.CIRS_BROWSER_DIR ? path.join(process.env.CIRS_BROWSER_DIR,'node_modules/playwright-core') : 'playwright-core');
const fs=require('fs'),assert=require('node:assert/strict');
const out=process.env.CIRS_QA_DIR || '/tmp/cirs-festivals-qa';fs.mkdirSync(out,{recursive:true});
const report={url:(process.env.CIRS_PREVIEW_URL || 'http://127.0.0.1:8878')+'/festivals.html',viewports:[],fallbacks:[],checks:[]};
async function state(p){return p.evaluate(()=>{const v=document.querySelector('[data-fx-hero-video]'),h=document.querySelector('[data-fx-hero]'),c=document.querySelector('.fx-hero__copy');return {time:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,pending:document.documentElement.classList.contains('fx-intro-pending'),ready:h.classList.contains('is-video-ready'),opacity:getComputedStyle(c).opacity,visibility:getComputedStyle(c).visibility,overflow:document.documentElement.scrollWidth>innerWidth,control:document.querySelector('[data-fx-intro-control]').textContent}})}
(async()=>{const b=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox']});
for(const [label,width,height] of [['desktop',1440,900],['tablet',768,1024],['mobile',390,844],['zoom',720,450]]){
 const p=await b.newPage({viewport:{width,height}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(()=>{window.fxFrames=[];window.addEventListener('DOMContentLoaded',()=>{const v=document.querySelector('[data-fx-hero-video]');v.addEventListener('timeupdate',()=>fxFrames.push({t:v.currentTime,pending:document.documentElement.classList.contains('fx-intro-pending')}));});});
 await p.goto(report.url,{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>document.querySelector('video').currentTime>.15);
 const early=await state(p);assert(early.pending && early.visibility==='hidden','early film must have no hero copy');assert(early.ready);assert(!early.overflow);
 await p.screenshot({path:out+'/'+label+'-early.jpg',type:'jpeg',quality:78});
 await p.waitForFunction(()=>document.querySelector('[data-fx-hero-video]').ended,null,{timeout:12000});await p.waitForTimeout(700);
 const end=await state(p);assert(end.ended && end.ready && !end.pending && end.opacity==='1');assert(end.time>=end.duration-.06);assert.equal(end.control,'Replay intro');assert(!end.overflow);
 const frames=await p.evaluate(()=>fxFrames);const firstReveal=frames.find(f=>!f.pending);assert(firstReveal.t>=end.duration-1.3,'no early reveal');
 await p.screenshot({path:out+'/'+label+'-final.jpg',type:'jpeg',quality:78});
 await p.locator('[data-fx-intro-control]').click();await p.waitForFunction(()=>document.querySelector('video').currentTime>.1 && document.querySelector('video').currentTime<2);
 assert((await state(p)).pending);await p.locator('[data-fx-intro-control]').focus();await p.keyboard.press('Enter');await p.waitForTimeout(650);const skip=await state(p);assert(skip.paused&&!skip.pending&&!skip.ready);assert.equal(skip.control,'Replay intro');assert.equal(await p.locator('[data-fx-intro-control]').evaluate(e=>document.activeElement===e),true);
 await p.locator('.fx-hero__scroll').click();await p.waitForTimeout(1500);await p.evaluate(()=>window.scrollBy({top:180,behavior:'instant'}));await p.waitForTimeout(400);assert.equal(await p.locator('.nv-header').getAttribute('data-header-mode'),'content');assert(await p.locator('[data-fx-intro-control]').isHidden());
 await p.screenshot({path:out+'/'+label+'-year.jpg',type:'jpeg',quality:78});
 assert(!await p.locator('#together').count());assert.equal(await p.locator('[data-fx-chapter]').count(),7);assert.equal(await p.locator('.fx-tile').count(),22);
 // Archive viewer: keyboard, focus return and filter still work after caption cleanup.
 await p.locator('.fx-tile__link').first().scrollIntoViewIfNeeded();await p.locator('.fx-tile__link').first().click();assert(await p.locator('[data-fx-viewer]').evaluate(e=>e.open));await p.keyboard.press('ArrowRight');await p.keyboard.press('Escape');assert(await p.locator('.fx-tile__link').first().evaluate(e=>document.activeElement===e));
 await p.locator('[data-fx-filter="festival"][data-value="raksha-bandhan"]').click();assert(await p.locator('.fx-tile:not([hidden])').count()>0);assert.equal(await p.locator('.fx-tile:not([hidden])').evaluateAll(es=>es.every(e=>e.dataset.festival==='raksha-bandhan')),true);
 await p.locator('[data-fx-filter="festival"][data-value="all"]').click();
 const backgrounds=await p.locator('.fx-open,.fx-night,.fx-ch--dussehra').evaluateAll(es=>es.map(e=>({class:e.className,color:getComputedStyle(e).color,background:getComputedStyle(e).backgroundColor})));
 assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth));assert.deepEqual(errors,[]);
 report.viewports.push({label,width,height,early,end,firstReveal,backgrounds,errors});await p.close();
}
for(const type of ['reduced','no-js','blocked-media','blocked-script','autoplay-rejected']){
 const p=await b.newPage({viewport:{width:390,height:844},reducedMotion:type==='reduced'?'reduce':'no-preference',javaScriptEnabled:type!=='no-js'});
 if(type==='blocked-media')await p.route('**/assets/video/festivals-opening.*',r=>r.abort());
 if(type==='blocked-script')await p.route('**/assets/js/festivals.js*',r=>r.abort());
 if(type==='autoplay-rejected')await p.addInitScript(()=>HTMLMediaElement.prototype.play=function(){return Promise.reject(new DOMException('blocked','NotAllowedError'))});
 await p.goto(report.url);if(type==='blocked-script')await p.waitForTimeout(8500);else await p.waitForTimeout(750);
 await p.waitForFunction(()=>!document.documentElement.classList.contains('fx-intro-pending') && getComputedStyle(document.querySelector('.fx-hero__copy')).opacity==='1',null,{timeout:10000});
 const s=await state(p);assert(!s.pending && s.opacity==='1' && s.visibility==='visible');assert(!s.overflow);assert(!s.ready);if(type==='reduced'||type==='no-js')assert(s.paused);
 assert.equal(await p.locator('.fx-tile__link').count(),22);await p.screenshot({path:out+'/fallback-'+type+'.jpg',type:'jpeg',quality:78});report.fallbacks.push({type,state:s});
 if(type==='blocked-media'){await p.unroute('**/assets/video/festivals-opening.*');await p.locator('[data-fx-intro-control]').click();await p.waitForFunction(()=>document.querySelector('video').currentTime>.1);assert((await state(p)).pending);await p.locator('[data-fx-intro-control]').click();report.checks.push('Replay recovers when failed media becomes available');}
 await p.close();
}
const p=await b.newPage();await p.goto(report.url);await p.waitForFunction(()=>document.querySelector('video').currentTime>.15);await p.emulateMedia({reducedMotion:'reduce'});await p.waitForTimeout(100);assert((await state(p)).paused);assert(!(await state(p)).pending);report.checks.push('live reduced-motion preference pauses film and reveals static hero');await p.close();
await b.close();fs.writeFileSync(out+'/browser.json',JSON.stringify(report,null,2));console.log(JSON.stringify({passed:true,viewports:report.viewports.length,fallbacks:report.fallbacks.length,out}));
})().catch(e=>{fs.writeFileSync(out+'/failure.txt',e.stack);console.error(e);process.exit(1)});
