// Run the repository preview server first. Install playwright-core locally or
// set CIRS_BROWSER_DIR to a directory containing node_modules/playwright-core.
const path = require('node:path');
const { chromium } = require(process.env.CIRS_BROWSER_DIR ? path.join(process.env.CIRS_BROWSER_DIR, 'node_modules/playwright-core') : 'playwright-core');
const assert = require('node:assert/strict'), fs = require('node:fs');
const base=process.env.CIRS_PREVIEW_URL || 'http://127.0.0.1:8878';
const output=process.env.CIRS_QA_DIR || '/tmp/cirs-interactions-qa';
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[],errors=[];
 async function run(name,fn){if(process.env.CIRS_TEST_FILTER&&!name.includes(process.env.CIRS_TEST_FILTER))return;await fn();results.push(name);console.log('PASS '+name);fs.writeFileSync(path.join(output,'interactions-results.json'),JSON.stringify(results,null,2));}
 async function page(options={}){const p=await browser.newPage(options);p.on('pageerror',e=>errors.push(e.message));return p;}
 for(const [name,viewport] of [['desktop',{width:1440,height:900}],['mobile',{width:390,height:844}]]){
 await run('Maths '+name+': inputs, feedback, hints, duplicate pair, solve, replay, keyboard',async()=>{
  const p=await page({viewport});await p.goto(base+'/math-challenge.html#cube-lab');
  const a=p.getByLabel('First edge'),b=p.getByLabel('Second edge'),status=p.locator('[data-lab-feedback]');
  await a.fill('2');await b.fill('3');await b.press('Enter');assert.match(await status.textContent(),/below/);
  for(let i=0;i<3;i++)await p.getByRole('button',{name:'Give me a hint'}).click();assert.match(await status.textContent(),/1 and 12/);
  await a.fill('12');await b.fill('1');await b.press('Enter');assert.match(await status.textContent(),/One pair found/);
  await a.fill('1');await b.fill('12');await b.press('Enter');assert.match(await status.textContent(),/already/);
  await a.fill('9');await b.fill('10');await b.press('Enter');assert.match(await status.textContent(),/Solved/);
  assert.match(await p.locator('[data-lab-found]').textContent(),/1³ \+ 12³ = 1729.*9³ \+ 10³ = 1729/);
  assert.equal(await p.getByRole('button',{name:'Give me a hint'}).isDisabled(),true);
  await p.locator('#cube-lab').screenshot({path:output+'/math-'+name+'-solved.png'});
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await p.getByRole('button',{name:'Play again'}).click();assert.equal(await a.inputValue(),'2');assert.equal(await a.evaluate(el=>el===document.activeElement),true);
  await a.fill('1.5');await b.press('Enter');assert.equal(await a.evaluate(el=>el.validity.stepMismatch),true);assert.match(await p.locator('[data-lab-progress]').textContent(),/0 of 2/);
  await p.close();
 });
 await run('Art '+name+': native default, seek/end, optional scroll forward/back, rewind and mode switch',async()=>{
  const p=await page({viewport});await p.goto(base+'/art-attack.html');await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').readyState>=2);
  assert.equal(await p.locator('video').first().evaluate(v=>v.controls),true);
  await p.locator('[data-aa-opening-video]').evaluate(v=>{v.pause();v.currentTime=Math.max(0,v.duration-.3);v.play();});
  await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').ended);
  await p.locator('[data-art-rewind]').click();await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').currentTime<.1);
  await p.locator('[data-art-mode]').click();assert.equal(await p.locator('[data-aa-opening-video]').evaluate(v=>v.controls),false);
  for(const progress of [.7,.2,1]){
   await p.evaluate(p=>{const h=document.querySelector('[data-aa-video-hero]');scrollTo({top:h.offsetTop+(h.offsetHeight-h.querySelector('.aa-video-hero__frame').offsetHeight)*p,behavior:'instant'});},progress);
   await p.waitForFunction(p=>{const v=document.querySelector('[data-aa-opening-video]');return !v.seeking&&Math.abs(v.currentTime-Math.min(v.duration-.03,v.duration*p))<.2;},progress,{timeout:10000});
  }
  await p.screenshot({path:output+'/art-'+name+'-scroll-end.png'});
  await p.locator('[data-art-rewind]').click();await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').currentTime<.1);
  await p.locator('[data-art-mode]').click();assert.equal(await p.locator('[data-aa-opening-video]').evaluate(v=>v.controls&&v.paused),true);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await p.screenshot({path:output+'/art-'+name+'-native.png'});await p.close();
 });
 }
 await run('Reduced motion: puzzle works without celebration motion; Art native controls only',async()=>{
  const p=await page({reducedMotion:'reduce'});await p.goto(base+'/math-challenge.html#cube-lab');
  for(const [a,b] of [['1','12'],['9','10']]){await p.getByLabel('First edge').fill(a);await p.getByLabel('Second edge').fill(b);await p.getByRole('button',{name:'Check pair'}).click();}
  assert.equal(await p.locator('.math-lab__model').evaluate(e=>getComputedStyle(e).animationName),'none');
  await p.goto(base+'/art-attack.html');assert.equal(await p.locator('[data-art-mode]').isDisabled(),true);assert.equal(await p.locator('[data-aa-opening-video]').evaluate(v=>v.paused&&v.controls),true);await p.close();
 });
 await run('Shared decorative video: offscreen pause/resume respects manual pause',async()=>{
  const p=await page();await p.goto(base+'/admissions.html');await p.waitForFunction(()=>{const v=document.querySelector('.pagehero__video');return v&&!v.paused;});
  await p.evaluate(()=>scrollTo({top:1800,behavior:'instant'}));await p.waitForFunction(()=>document.querySelector('.pagehero__video').paused);
  await p.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await p.waitForFunction(()=>!document.querySelector('.pagehero__video').paused);
  await p.locator('.pagehero__video').evaluate(v=>v.pause());await p.waitForTimeout(100);await p.evaluate(()=>scrollTo({top:1800,behavior:'instant'}));await p.waitForTimeout(200);await p.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await p.waitForTimeout(300);assert.equal(await p.locator('.pagehero__video').evaluate(v=>v.paused),true);await p.close();
 });
 await run('Scrubbed film: real forward/reverse/final-frame seeks with missing animation libraries',async()=>{
  const p=await page();await p.route('**/assets/vendor/**',r=>r.abort());await p.goto(base+'/captures.html');await p.waitForFunction(()=>document.querySelector('[data-film-video]').readyState>=2);
  for(const progress of [.5,.15,.95]){
   await p.evaluate(p=>{const s=document.querySelector('[data-film]');scrollTo({top:s.offsetTop+(s.offsetHeight-s.querySelector('.film__stage').offsetHeight)*p,behavior:'instant'});},progress);
   await p.waitForFunction(p=>{const s=document.querySelector('[data-film]'),v=s.querySelector('video'),end=Number(s.dataset.filmPhases.split(' ')[0]);const target=Math.min(v.duration-.03,p/end*v.duration);return !v.seeking&&Math.abs(v.currentTime-target)<.2;},progress,{timeout:10000});
  }
  await p.screenshot({path:path.join(output,'captures-final-frame.png')});await p.close();
 });
 await run('Slow-loading scrubbed film recovers after its still fallback',async()=>{
  const p=await page();await p.route('**/assets/video/**',async r=>{await new Promise(resolve=>setTimeout(resolve,6500));await r.continue().catch(()=>{});});
  await p.goto(base+'/captures.html',{waitUntil:'domcontentloaded'});
  await p.waitForFunction(()=>document.querySelector('[data-film]').hasAttribute('data-film-still'),{},{timeout:6500});
  await p.waitForFunction(()=>{const s=document.querySelector('[data-film]');return !s.hasAttribute('data-film-still')&&s.querySelector('video').readyState>=2;},{},{timeout:15000});await p.close();
 });
 await run('Art delayed media: early rewind, rapid mode switch and changed motion preference',async()=>{
  const p=await page();await p.route('**/assets/video/**',async r=>{await new Promise(resolve=>setTimeout(resolve,1800));await r.continue().catch(()=>{});});
  await p.goto(base+'/art-attack.html',{waitUntil:'domcontentloaded'});await p.locator('[data-art-rewind]').click();
  await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').readyState>=2);
  await p.locator('[data-aa-opening-video]').evaluate(v=>v.play());
  await p.waitForFunction(()=>document.querySelector('[data-aa-opening-video]').currentTime>1);
  await p.locator('[data-art-rewind]').click();await p.locator('[data-art-mode]').click();
  await p.evaluate(()=>{const h=document.querySelector('[data-aa-video-hero]');scrollTo({top:h.offsetTop+(h.offsetHeight-h.querySelector('.aa-video-hero__frame').offsetHeight)*.5,behavior:'instant'});});
  await p.waitForFunction(()=>{const v=document.querySelector('[data-aa-opening-video]');return !v.seeking&&Math.abs(v.currentTime-v.duration*.5)<.2;});
  await p.emulateMedia({reducedMotion:'reduce'});
  await p.waitForFunction(()=>document.querySelector('[data-art-mode]').disabled);
  assert.equal(await p.locator('[data-art-mode]').isDisabled(),true);
  assert.equal(await p.locator('[data-aa-opening-video]').evaluate(v=>v.paused&&v.controls),true);await p.close();
 });
 assert.deepEqual(errors,[], 'No page JavaScript errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
