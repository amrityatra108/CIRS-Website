// Math-only regression: source-backed archive, native grade navigation and motion fallbacks.
// CIRS_BROWSER_DIR must contain playwright-core and @axe-core/playwright.
const path = require('node:path'), fs = require('node:fs'), assert = require('node:assert/strict');
const modules = process.env.CIRS_BROWSER_DIR || '/tmp/cirs-browser';
const { chromium } = require(path.join(modules, 'node_modules/playwright-core'));
const AxeBuilder = require(path.join(modules, 'node_modules/@axe-core/playwright')).default;
const base = process.env.CIRS_PREVIEW_URL || 'http://127.0.0.1:8013';
const output = process.env.CIRS_QA_DIR || '/tmp/math-only-qa';
fs.mkdirSync(output, {recursive:true});
(async()=>{
 const browser = await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results = [], errors = [];
 function pass(s) { results.push(s); console.log('PASS '+s); }
 async function land(p,selector,offset=110){await p.locator(selector).evaluate((el,y)=>scrollTo({top:el.getBoundingClientRect().top+scrollY-y,behavior:'instant'}),offset);await p.waitForTimeout(250);}
 for(const [name,viewport,reducedMotion] of [ ['desktop',{width:1440,height:900},'no-preference'],['mobile',{width:390,height:844},'no-preference'],['reduced',{width:1440,height:900},'reduce'] ]){
  const context=await browser.newContext({viewport,reducedMotion});const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base+'/math-challenge.html');await p.waitForFunction(()=>window.__mcBooted);await p.waitForTimeout(600);
  await p.screenshot({path:output+'/math-'+name+'-hero.png'});
  assert.equal(await p.locator('.mc-doc').count(),25);
  assert.equal(await p.locator('.mc-month').count(),7);
  assert.equal(await p.locator('.mc-grade').count(),4);
  const expected=[7,7,6,5], keys=['5-6','7-8','9-10','11-12'];
  for(let i=0;i<keys.length;i++){
   const g=keys[i];assert.equal(await p.locator('#grade-'+g+' .mc-grade__papers a').count(),expected[i]);
   await land(p,'#grade-'+g);
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   if(name==='desktop'){
    const op=await p.locator('.mc-stack__block').evaluateAll(els=>els.map(el=>+getComputedStyle(el).opacity));
    assert(op.slice(0,i+1).every(v=>v===1));assert(op.slice(i+1).every(v=>v===0));
   }else assert.equal(await p.locator('.mc-stack').evaluate(el=>getComputedStyle(el).display),'none');
   if(i===1)await p.screenshot({path:output+'/math-'+name+'-grades.png'});
  }
  // Reverse scrolling removes the later layers as naturally as they build.
  await land(p,'#grade-5-6');
  if(name==='desktop')assert.deepEqual(await p.locator('.mc-stack__block').evaluateAll(els=>els.map(el=>+getComputedStyle(el).opacity)),[1,0,0,0]);
  pass(name+': all four grade mappings, forward/back scroll, no overflow');
  await land(p,'#zones');
  await p.locator('.mc-grade-nav a').nth(2).focus();await p.keyboard.press('Enter');await p.waitForTimeout(1200);
  assert.equal(new URL(p.url()).hash,'#grade-9-10');
  assert(await p.locator('#grade-9-10').evaluate(el=>el.getBoundingClientRect().top>=0&&el.getBoundingClientRect().top<innerHeight/2));
  await p.goBack();await p.goForward();await p.waitForTimeout(500);
  assert.equal(new URL(p.url()).hash,'#grade-9-10');
  await p.reload();await p.waitForTimeout(600);assert(await p.locator('#grade-9-10').isVisible());
  await p.locator('#grade-9-10 .mc-zone__link').focus();await p.keyboard.press('Enter');await p.waitForTimeout(1100);
  assert.equal(await p.locator('.mc-filter[aria-pressed="true"]').getAttribute('data-grade'),'9-10');
  assert.equal(await p.locator('.mc-doc:visible').count(),6);
  await p.locator('#mcSearch').fill('February');await p.waitForTimeout(500);
  assert.equal(await p.locator('.mc-doc:visible').count(),0);assert(await p.locator('#mcNone').isVisible());
  await p.locator('[data-reset]').click();assert.equal(await p.locator('.mc-doc:visible').count(),25);
  await p.locator('#mcSearch').fill('April');await p.waitForTimeout(500);assert.equal(await p.locator('.mc-doc:visible').count(),4);
  await p.locator('#mcSearch').press('Escape');assert.equal(await p.locator('.mc-doc:visible').count(),25);
  await land(p,'#archive');await p.screenshot({path:output+'/math-'+name+'-archive.png'});
  pass(name+': keyboard grade links, hash/reload/history, archive filters, no-result and reset');
  const audit=await new AxeBuilder({page:p}).include('#main').withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  fs.writeFileSync(output+'/axe-'+name+'.json',JSON.stringify(audit.violations,null,2));
  assert.deepEqual(audit.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),[]);
  pass(name+': main-content axe WCAG A/AA');
  if(name==='desktop'){
   await land(p,'#grade-11-12');await p.setViewportSize({width:390,height:844});await p.waitForTimeout(400);
   assert.equal(await p.locator('.mc-stack').evaluate(el=>getComputedStyle(el).display),'none');
   await p.setViewportSize(viewport);await land(p,'#grade-7-8');
   await p.emulateMedia({reducedMotion:'reduce'});await p.waitForTimeout(250);
   assert.equal(await p.locator('.mc-stack').evaluate(el=>getComputedStyle(el).display),'none');
   await p.emulateMedia({reducedMotion:'no-preference'});await land(p,'#grade-7-8');
   assert.deepEqual(await p.locator('.mc-stack__block').evaluateAll(els=>els.map(el=>+getComputedStyle(el).opacity)),[1,1,0,0]);
   pass('desktop: responsive resize and live reduced-motion switch');
  }
  await context.close();
 }
 const plain=await browser.newPage({javaScriptEnabled:false,viewport:{width:390,height:844}});
 await plain.goto(base+'/math-challenge.html#grade-11-12');assert.equal(await plain.locator('.mc-doc:visible').count(),25);
 assert(await plain.locator('#math-solution').isVisible());assert.equal(await plain.locator('.mc-grade:visible').count(),4);
 await plain.screenshot({path:output+'/math-no-js.png'});pass('no JavaScript: four grade sections, 25 documents and worked solution readable');await plain.close();
 assert.deepEqual(errors,[]);pass('no page JavaScript errors');
 fs.writeFileSync(output+'/results.json',JSON.stringify(results,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
