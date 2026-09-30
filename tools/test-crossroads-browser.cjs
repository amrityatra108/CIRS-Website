const path = require('node:path');
const {chromium} = require(process.env.CIRS_BROWSER_DIR ? path.join(process.env.CIRS_BROWSER_DIR, 'node_modules/playwright-core') : 'playwright-core');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const base = (process.env.CIRS_PREVIEW_URL || 'http://127.0.0.1:8878') + '/crossroads.html';
const output = process.env.CIRS_QA_DIR || '/tmp/cirs-crossroads-qa';
fs.mkdirSync(output,{recursive:true});
(async () => {
  const browser = await chromium.launch({executablePath:process.env.CIRS_CHROMIUM || '/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
  const results=[];
  async function state(page) {
    return page.evaluate(() => {
      const v=document.querySelector('[data-crossroads-intro-opening]');
      const i=document.querySelector('[data-crossroads-intro]');
      return {locked:document.documentElement.classList.contains('crossroads-intro-scroll-locked'),settled:i.hasAttribute('data-crossroads-intro-settled'),handoff:i.hasAttribute('data-crossroads-intro-handoff'),paused:v.paused,time:v.currentTime,duration:v.duration,src:v.getAttribute('src'),overflow:document.documentElement.scrollWidth>innerWidth};
    });
  }
  for (const [name,viewport] of [['desktop',{width:1440,height:900}],['mobile',{width:390,height:844}]]) {
    const p=await browser.newPage({viewport});
    await p.addInitScript(() => {
      addEventListener('DOMContentLoaded', () => {
        const film=document.querySelector('[data-crossroads-intro-opening]');
        film.addEventListener('ended', () => {
          window.handoffFrames=[];
          function sample() {
            const intro=document.querySelector('[data-crossroads-intro]');
            const f=getComputedStyle(film),pen=getComputedStyle(document.querySelector('.crossroads-intro__pen'));
            const title=getComputedStyle(document.querySelector('.crossroads-intro-title-art'));
            const mark=getComputedStyle(document.querySelector('.crossroads-intro__mark'));
            const matrix=new DOMMatrix(pen.transform);
            window.handoffFrames.push({film:f.display!=='none'&&f.visibility!=='hidden'?Number(f.opacity):0,pen:Number(pen.opacity)*Number(mark.opacity),title:Number(title.opacity)*Number(mark.opacity),scaleX:matrix.a,scaleY:matrix.d});
            if(intro.hasAttribute('data-crossroads-intro-handoff'))requestAnimationFrame(sample);
          }
          requestAnimationFrame(sample);
        });
      });
    });
    await p.goto(base);
    await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro-opening]').ended,{},{timeout:12000});
    const ended=await state(p);
    assert.equal(ended.time,ended.duration);
    assert.equal(ended.handoff,true);
    assert.equal(ended.locked,false);
    await p.screenshot({path:`${output}/crossroads-${name}-final-frame.png`});
    await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-dissolve'));
    await p.waitForTimeout(100);
    await p.screenshot({path:`${output}/crossroads-${name}-film-exit.png`});
    await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-logo-reveal'));
    await p.waitForTimeout(280);
    await p.screenshot({path:`${output}/crossroads-${name}-logo-reveal.png`});
    await p.waitForFunction(()=>!document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-handoff'));
    const settled=await state(p);
    assert.equal(settled.src,null);
    assert.equal(settled.overflow,false);
    await p.screenshot({path:`${output}/crossroads-${name}-settled.png`});
    const frames=await p.evaluate(()=>window.handoffFrames);
    assert.ok(frames.length>20,'Sampled the handoff on rendered frames');
    assert.equal(frames.filter(f=>f.film>0&&(f.pen>0||f.title>0)).length,0,'Film and SVG contours never overlap');
    assert.ok(frames.every(f=>Math.abs(f.scaleX-f.scaleY)<.0001),'Approved artwork keeps its proportions');
    results.push({test:`${name}: natural end, no contour overlap, uniform scaling, no overflow`,ended,settled,sampledFrames:frames.length,overlapFrames:0});
    await p.close();
  }
  for(const keyboard of [false,true]) {
    const p=await browser.newPage(); await p.goto(base);
    const skip=p.locator('[data-crossroads-intro-skip]');
    if(keyboard){await skip.focus();await p.keyboard.press('Enter');}else await skip.click();
    await p.waitForTimeout(650);
    const s=await state(p); assert.equal(s.locked,false); assert.equal(s.settled,true); assert.equal(s.paused,true); assert.equal(s.handoff,false);
    results.push({test:keyboard?'keyboard Skip':'pointer Skip',state:s});await p.close();
  }
  {
    const p=await browser.newPage({reducedMotion:'reduce'});await p.goto(base);const s=await state(p);
    assert.equal(s.locked,false);assert.equal(s.src,null);assert.equal(s.settled,true);
    results.push({test:'reduced motion skips film and lock',state:s});await p.close();
  }
  {
    const p=await browser.newPage();await p.route('**/crossroads-opening*.mp4',async route=>{await new Promise(r=>setTimeout(r,8000));await route.continue().catch(()=>{});});
    await p.goto(base,{waitUntil:'domcontentloaded'});
    await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-settled'),{},{timeout:7000});
    const s=await state(p);assert.equal(s.locked,false);assert.equal(s.paused,true);
    results.push({test:'slow media releases at original deadline',state:s});await p.close();
  }
  {
    const p=await browser.newPage();await p.goto(base);
    await p.waitForFunction(()=>performance.now()>6200);
    await p.evaluate(()=>document.querySelector('[data-crossroads-intro-opening]').pause());
    await p.waitForFunction(()=>document.querySelector('[data-crossroads-intro]').hasAttribute('data-crossroads-intro-settled'),{},{timeout:4500});
    const s=await state(p);assert.equal(s.locked,false);assert.equal(s.paused,true);
    results.push({test:'stall after deadline has bounded fallback',state:s});await p.close();
  }
  fs.writeFileSync(path.join(output,'crossroads-results.json'),JSON.stringify(results,null,2));
  console.log(JSON.stringify(results,null,2));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
