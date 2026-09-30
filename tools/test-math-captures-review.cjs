// Focused browser regressions for the PR139/140 review findings.
const path = require('node:path'), fs = require('node:fs'), assert = require('node:assert/strict');
const { chromium } = require(path.join(process.env.CIRS_BROWSER_DIR || '/tmp/cirs-browser','node_modules/playwright-core'));
const base = process.env.CIRS_PREVIEW_URL || 'http://127.0.0.1:8044';
const output = process.env.CIRS_QA_DIR || '/tmp/math-captures-review-qa';
fs.mkdirSync(output,{recursive:true});
function luminance(s){const c=s.match(/[\d.]+/g).slice(0,3).map(v=>{v=+v/255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});return .2126*c[0]+.7152*c[1]+.0722*c[2]}
function contrast(a,b){a=luminance(a);b=luminance(b);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const report={math:[],captures:[]};
 for(const legacy of [false,true]){
  const p=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(legacy)await p.addInitScript(()=>{
   const native=window.matchMedia;
   window.__legacyMathQueries=[];
   window.matchMedia=q=>{
    const m=native(q);
    // Only the Maths controller is under test; unrelated shared scripts retain
    // their normal browser APIs. Each Maths MQL exposes the old Safari API.
    if(new Error().stack.includes('matharena.js')){
     const add=m.addListener.bind(m);
     Object.defineProperty(m,'addEventListener',{value:undefined});
     Object.defineProperty(m,'addListener',{value:fn=>{window.__legacyMathQueries.push(q);add(fn)}});
    }
    return m;
   };
  });
  await p.goto(base+'/math-challenge.html');
  await p.waitForFunction(()=>document.querySelector('#mcArt').classList.contains('is-live'));
  await p.locator('#zones').evaluate(el=>scrollTo({top:el.offsetTop,behavior:'instant'}));
  await p.waitForFunction(()=>document.querySelector('#mc-zones-title').classList.contains('is-in'));
  await p.locator('#grade-7-8').evaluate(el=>scrollTo({top:el.getBoundingClientRect().top+scrollY-110,behavior:'instant'}));await p.waitForTimeout(250);
  assert.deepEqual(await p.locator('.mc-stack__block').evaluateAll(els=>els.map(el=>+el.style.opacity)),[1,1,0,0]);
  await p.emulateMedia({reducedMotion:'reduce'});await p.waitForTimeout(200);
  assert.equal(await p.locator('html').evaluate(el=>el.classList.contains('mc-kinetic')),false);
  assert.deepEqual(await p.locator('.mc-stack__block').evaluateAll(els=>els.map(el=>+el.style.opacity)),[1,1,1,1]);
  await p.emulateMedia({reducedMotion:'no-preference'});await p.waitForTimeout(250);
  assert.equal(await p.locator('html').evaluate(el=>el.classList.contains('mc-kinetic')),true);
  if(legacy)assert.equal((await p.evaluate(()=>window.__legacyMathQueries)).length,2);
  assert.deepEqual(errors,[]);report.math.push({legacy,headingsRevealed:true,sculptureStarted:true,motionChangesWork:true,errors});await p.close();
 }
 for(const width of [1440,390]){
  const p=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  await p.goto(base+'/captures.html#last-frame');
  const primary=p.locator('.cg-end__onward .btn--primary'),outline=p.locator('.cg-end__onward .btn--outline');
  await primary.scrollIntoViewIfNeeded();
  const cdp=await p.context().newCDPSession(p);await cdp.send('DOM.enable');await cdp.send('CSS.enable');
  const doc=await cdp.send('DOM.getDocument');const {nodeId}=await cdp.send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'.cg-end__onward .btn--primary'});
  for(const hover of [false,true]){
   await cdp.send('CSS.forcePseudoState',{nodeId,forcedPseudoClasses:hover?['hover']:[]});
   const colors=await primary.evaluate(el=>{const s=getComputedStyle(el);return {color:s.color,background:s.backgroundColor,onGold:getComputedStyle(document.body).getPropertyValue('--on-gold').trim()}});
   const ratio=contrast(colors.color,colors.background);assert(ratio>=4.5,JSON.stringify({width,hover,...colors,ratio}));
   assert.equal(colors.color,'rgb(30, 22, 38)');report.captures.push({width,hover,...colors,ratio});
  }
  assert.equal(await outline.evaluate(el=>getComputedStyle(el).color),'rgb(250, 249, 243)');
  await cdp.send('CSS.forcePseudoState',{nodeId,forcedPseudoClasses:[]});
  await p.locator('.cg-end__onward').screenshot({path:output+'/captures-buttons-'+width+'.png'});await p.close();
 }
 fs.writeFileSync(output+'/review-regressions.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
