const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.CIRS_BROWSER_DIR?path.join(process.env.CIRS_BROWSER_DIR,'node_modules/playwright-core'):'playwright-core');
const base=process.env.CIRS_PREVIEW_URL||'http://127.0.0.1:8878',out=process.env.CIRS_QA_DIR||'/tmp/cirs-crossroads-page';fs.mkdirSync(out,{recursive:true});
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[];
 for(const [name,viewport,reduced] of [['desktop',{width:1440,height:900},false],['mobile',{width:390,height:844},false],['reduced',{width:390,height:844},true]]){
  const p=await b.newPage({viewport,reducedMotion:reduced?'reduce':'no-preference'});const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base+'/crossroads.html');
  if(!reduced)await p.locator('[data-crossroads-intro-skip]').click();
  await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-settled'));
  await p.waitForTimeout(600);
  for(const selector of ['.crossroads-intro','.crossroads-intro__base'])assert.equal(await p.locator(selector).evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(0, 0, 0)');
  await p.screenshot({path:path.join(out,name+'-archive-after-skip.png')});
  await p.locator('[data-crossroads-intro-enter]').focus();await p.keyboard.press('Enter');
  await p.waitForFunction(()=>Math.abs(document.getElementById('crossroads-main').getBoundingClientRect().top)<150);
  // Exercise the section controller with real keyboard and wheel input.
  await p.evaluate(()=>{document.activeElement.blur();scrollTo({top:0,behavior:'instant'})});await p.waitForTimeout(1300);
  await p.keyboard.press('PageDown');await p.waitForFunction(()=>scrollY>innerHeight*.5);await p.waitForTimeout(1200);
  await p.mouse.wheel(0,-900);await p.waitForFunction(()=>scrollY<10);await p.waitForTimeout(1200);
  await p.locator('[data-crossroads-intro-enter]').focus();await p.keyboard.press('Enter');
  await p.waitForFunction(()=>Math.abs(document.getElementById('crossroads-main').getBoundingClientRect().top)<150);
  await p.locator('.crossroads-archive-hero__primary').click();await p.waitForFunction(()=>location.hash==='#archive');
  await p.waitForFunction(()=>document.activeElement.id==='archive');
  const pdfs=await p.locator('a[href$=".pdf"]').evaluateAll(es=>[...new Set(es.map(e=>e.href))]);assert.ok(pdfs.length>20);
  for(const url of pdfs){const response=await p.request.get(url);assert.equal(response.status(),200,url);const data=await response.body();assert.equal(data.subarray(0,4).toString(),'%PDF',url)}
  // Crawl every content section and the footer, letting lazy images and
  // entrance animations settle at their real scroll positions.
  for(const selector of ['#top','#inside-the-issue','#statement','#about','#archive','.footer-wrap']){
   await p.locator(selector).scrollIntoViewIfNeeded();await p.waitForTimeout(700);
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,selector+' horizontal overflow');
   await p.screenshot({path:path.join(out,name+'-'+selector.replace(/[^a-z-]/g,'')+'.png')});
  }
  const broken=await p.locator('img').evaluateAll(es=>es.filter(e=>e.complete&&e.naturalWidth===0).map(e=>e.src));assert.deepEqual(broken,[]);
  assert.deepEqual(errors,[]);
  // Return to the opening and navigate the browser history after archive use.
  await p.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await p.waitForTimeout(400);
  assert.equal(await p.locator('[data-crossroads-intro-opening]').evaluate(v=>v.paused),true);
  await p.goBack();await p.goForward();await p.waitForTimeout(400);
  assert.equal(await p.evaluate(()=>document.documentElement.classList.contains('crossroads-intro-scroll-locked')),false);
  results.push({test:name+' keyboard entry, archive, PDF links, full-section crawl, footer and history',pdfs:pdfs.length,passed:true});await p.close();
 }
 // Reproduce autoplay rejection: clicking Play must not bubble into the
 // intro's generic click-to-skip handler.
 {
  const p=await b.newPage();await p.addInitScript(()=>{const original=HTMLMediaElement.prototype.play;let refused=false;HTMLMediaElement.prototype.play=function(){if(this.hasAttribute('data-crossroads-intro-opening')&&!refused){refused=true;return Promise.reject(new DOMException('Autoplay blocked','NotAllowedError'))}return original.call(this)}});
  await p.goto(base+'/crossroads.html');await p.locator('[data-crossroads-intro-play]').waitFor({state:'visible'});
  await p.locator('[data-crossroads-intro-play]').click();await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro-opening]').currentTime>.2);
  assert.equal(await p.locator('[data-crossroads-intro]').evaluate(i=>i.hasAttribute('data-crossroads-intro-settled')),false);
  results.push({test:'blocked autoplay Play control starts the intro without skipping',passed:true});await p.close();
 }
 fs.writeFileSync(path.join(out,'page-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
