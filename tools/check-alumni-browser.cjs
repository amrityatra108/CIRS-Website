// Run against `python3 -m http.server 8000` with Playwright installed outside
// the repo: CIRS_BROWSER_DIR=/path/to/node_modules node tools/check-alumni-browser.cjs
const path = require('node:path');
const {chromium}=require(process.env.CIRS_BROWSER_DIR ? path.join(process.env.CIRS_BROWSER_DIR, 'playwright') : 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const out = process.env.CIRS_ALUMNI_REVIEW_DIR || '/tmp/cirs-alumni-review';
fs.mkdirSync(out, {recursive:true});
const url = process.env.CIRS_ALUMNI_URL || 'http://localhost:8000/alumni.html';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const errors=[], report=[];
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url); await page.waitForTimeout(1600);
 assert.equal(await page.locator('.ajc__land').count(),240);
 assert.equal(await page.locator('.ajc__pt').count(),19);
 const browse=page.locator('[data-filter="all"]');
 for(let i=0;i<3;i++){
  await browse.click();
  assert.equal(await page.locator('[data-panel-results] li').count(),166);
  const y=await page.evaluate(()=>scrollY);
  await page.mouse.wheel(0,700); await page.waitForTimeout(150);
  assert.equal(await page.evaluate(()=>scrollY),y);
  await page.locator('#ajc-search').fill('impossible institution xyz');
  assert.equal(await page.locator('[data-panel-results] li').count(),0);
  assert(await page.locator('[data-panel-empty]').isVisible());
  await page.locator('#ajc-search').fill('singapore');
  assert.equal(await page.locator('[data-panel-results] li').count(),7);
  await page.locator('[data-panel-close]').focus(); await page.keyboard.press('Shift+Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.hasAttribute('data-panel-all')),true);
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.hasAttribute('data-panel-close')),true);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#ajc-panel').evaluate(e=>e.open),false);
  assert.equal(await page.evaluate(()=>document.activeElement.dataset.filter),'all');
  assert(Math.abs(await page.evaluate(()=>scrollY)-y)<2);
 }
 report.push('Repeated open/search/empty/reset/Escape; Tab loop; focus and scroll restoration: passed');
 await page.locator('#ajc-country').selectOption('Brazil'); await page.locator('[data-country-open]').click();
 assert.equal(await page.locator('[data-panel-results] li').count(),0);
 assert((await page.locator('[data-panel-empty]').textContent()).includes('does not imply'));
 await page.locator('[data-panel-all]').click(); assert.equal(await page.locator('[data-panel-results] li').count(),166);
 await page.locator('[data-panel-close]').click();
 await page.locator('[data-filter="middle-east"]').click(); assert.equal(await page.locator('[data-panel-results] li').count(),3);
 await page.keyboard.press('Escape');
 const uk=page.locator('.ajc__land[data-country="United Kingdom"]');
 await uk.focus(); assert((await page.locator('[data-map-hint]').textContent()).includes('17 institutions'));
 await page.keyboard.press('Enter'); assert.equal(await page.locator('[data-panel-results] li').count(),17);
 await page.keyboard.press('Escape'); assert.equal(await page.evaluate(()=>document.activeElement.dataset.country),'United Kingdom');
 await page.keyboard.press('ArrowRight'); assert.equal(await page.evaluate(()=>document.activeElement.dataset.country),'United States');
 // Click inside Brazil's actual polygon, using a projected inland location.
 await page.locator('.ajc__map').scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
 const target=await page.evaluate(()=>{ const svg=document.querySelector('.ajc__map'); const p=svg.createSVGPoint(); p.x=72.10; p.y=64.0; const screen=p.matrixTransform(svg.getScreenCTM()); return {x:screen.x,y:screen.y,country:document.elementFromPoint(screen.x,screen.y)?.dataset.country}; });
 assert.equal(target.country,'Brazil'); await page.mouse.click(target.x,target.y); assert.equal(await page.locator('#ajc-panel-name').textContent(),'Brazil'); await page.keyboard.press('Escape');
 report.push('Geographic pointer hit, keyboard country traversal, country/region counts and honest empty country: passed');
 // A pinned scene is selected through the single existing scroll owner.
 await page.evaluate(()=>{const t=ScrollTrigger.getAll().find(t=>t.trigger?.matches('[data-pathways]')); window.scrollTo(0,t.start+3); ScrollTrigger.update();});
 await page.waitForTimeout(700);
 const colors=[];
 for(const n of [0,1,2,3,4,2,0]){
  await page.locator('[data-goto="'+n+'"]').click(); await page.waitForTimeout(1250);
  assert.equal(await page.locator('.ajw.is-on').getAttribute('data-pathway'),['abroad','national','design','science','sport'][n]);
  assert.equal(await page.locator('.ajw__dot[aria-current="step"]').getAttribute('data-goto'),String(n));
  colors[n]=await page.locator('#pathways').evaluate(el=>getComputedStyle(el).backgroundColor);
  if(n===4||n===0)await page.screenshot({path:out + '/pathway-'+n+'.png'});
 }
 assert.equal(new Set(colors).size,5);
 for(const progress of [.8,.55,.2,0]){
  await page.evaluate(p=>{const t=ScrollTrigger.getAll().find(t=>t.trigger?.matches('[data-pathways]')); window.scrollTo(0,t.start+(t.end-t.start)*p); ScrollTrigger.update();},progress); await page.waitForTimeout(350);
  assert.equal(await page.locator('.ajw__dot[aria-current]').getAttribute('data-goto'),String(Math.round(progress*4)));
 }
 await page.setViewportSize({width:768,height:1024}); await page.waitForTimeout(700);
 assert.equal(await page.locator('.ajw-track.is-live').count(),0); assert.equal(await page.locator('.ajw[inert]').count(),0);
 assert.equal(await page.locator('.ajw[aria-hidden]').count(),0);
 for(const s of ['#constellation','#aj-voices','#aj-return']){ await page.locator(s).scrollIntoViewIfNeeded(); await page.waitForTimeout(500); await page.locator(s).screenshot({path:out + '/tablet-'+s.slice(1)+'.png'}); }
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.setViewportSize({width:1440,height:650}); await page.waitForTimeout(500); assert.equal(await page.locator('.ajw-track.is-live').count(),0);
 await page.setViewportSize({width:1440,height:1000}); await page.waitForTimeout(500); assert.equal(await page.locator('.ajw-track.is-live').count(),1);
 report.push('Five distinct pathway grounds, forward/direct/reverse selection, active nav, resize teardown/rebuild, short desktop stack: passed');
 await page.locator('#aj-return').scrollIntoViewIfNeeded(); await page.waitForTimeout(800); await page.locator('#aj-return').screenshot({path:out + '/return-final.png'});
 // Mobile, including actual touch events in emulation.
 const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
 mobile.on('pageerror',e=>errors.push(e.message)); await mobile.goto(url); await mobile.waitForTimeout(1200);
 await mobile.locator('[data-filter="india"]').tap(); assert.equal(await mobile.locator('[data-panel-results] li').count(),97);
 assert.equal(Math.round((await mobile.locator('#ajc-panel').boundingBox()).height),844);
 await mobile.locator('#ajc-search').fill('IIT'); await mobile.screenshot({path:out + '/mobile-sheet.png'});
 await mobile.locator('[data-panel-close]').tap(); assert.equal(await mobile.locator('#ajc-panel').evaluate(e=>e.open),false);
 for(const s of ['#constellation','#aj-voices','#pathways','#aj-return']){await mobile.locator(s).scrollIntoViewIfNeeded(); await mobile.waitForTimeout(600); await mobile.locator(s).screenshot({path:out + '/mobile-'+s.slice(1)+'.png'});}
 assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await mobile.setViewportSize({width:320,height:640}); await mobile.waitForTimeout(500); assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 report.push('390px touch modal/search/close, full-height sheet; 320px and tablet no horizontal overflow: passed');
 for(const mode of ['reduced','no-js']){
  const p=await browser.newPage({viewport:{width:1280,height:900},javaScriptEnabled:mode!=='no-js',reducedMotion:mode==='reduced'?'reduce':'no-preference'});
  await p.goto(url + '#pathways'); await p.waitForTimeout(500);
  assert.equal(await p.locator('.ajw-track.is-live').count(),0); assert.equal(await p.locator('.ajw').count(),5);
  assert.equal(await p.locator('.ajv').count(),3); assert.equal(await p.locator('.ajd__row').count(),166);
  for(const q of await p.locator('.ajv').all()) assert(await q.isVisible());
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await p.screenshot({path:out + '/'+mode+'.png'});
  if(mode==='reduced'){await p.locator('[data-filter="all"]').click();assert.equal(await p.locator('[data-panel-results] li').count(),166);}
  await p.close();
 }
 report.push('Reduced motion and JavaScript disabled: all quotes, pathways, 166 directory entries and #pathways anchor remain available');
 assert.deepEqual(errors,[]); report.push('No browser runtime errors');
 fs.writeFileSync(out + '/browser-results.json',JSON.stringify({report,colors,errors},null,2));
 console.log(report.join('\n')); await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
