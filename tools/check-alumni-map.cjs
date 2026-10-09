// Run against a local server with Playwright installed outside the repository.
const path=require('node:path'), fs=require('node:fs'), assert=require('node:assert/strict');
const {chromium}=require(process.env.CIRS_BROWSER_DIR?path.join(process.env.CIRS_BROWSER_DIR,'node_modules/playwright-core'):'playwright-core');
const out=process.env.CIRS_ALUMNI_REVIEW_DIR||'/tmp/cirs-alumni-review';
const url=process.env.CIRS_ALUMNI_URL||'http://localhost:8000/alumni.html';
fs.mkdirSync(out,{recursive:true});
const records=JSON.parse(fs.readFileSync(path.join(__dirname,'alumni-destinations.json')));
const coverage=[...new Set(records.map(r=>r.country))].sort().map(country=>({country,total:records.filter(r=>r.country===country).length,mapped:records.filter(r=>r.country===country&&r.lat!==null&&r.lon!==null).length}));
for(const c of coverage)assert(c.mapped>=Math.min(3,c.total),JSON.stringify(c));
assert.equal(coverage.length,14);assert.equal(coverage.reduce((n,c)=>n+c.mapped,0),37);
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox']});
 const errors=[],report=[],limitations=['Physical-device pinch and pan remain unverified; headless synthetic gestures do not establish them.'];
 for(const width of [1440,1024,768,390,320]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce',isMobile:width<900,hasTouch:width<900});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(500);
  const field=page.locator('.ajc__field');await field.scrollIntoViewIfNeeded();
  for(const name of ['China','Australia']){
   const country=page.locator('.ajc__land[data-country="'+name+'"]');await country.focus();
   const style=await country.evaluate(e=>{const s=getComputedStyle(e);return {outline:s.outlineStyle,stroke:s.strokeWidth,vector:s.vectorEffect};});
   assert.equal(style.outline,'none');assert.equal(style.stroke,'2.5px');assert.equal(style.vector,'non-scaling-stroke');
   await field.screenshot({path:out+'/map-'+width+'-'+name.toLowerCase()+'-focus.png'});
   await page.keyboard.press('Enter');assert.equal(await page.locator('#ajc-panel-name').textContent(),name);
   assert.equal(await page.locator('[data-panel-results] > li').count(),name==='China'?0:6);
   await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.dataset.country),name);
  }
  assert.equal(await page.locator('.ajc__mapMarkers circle').count(),37);
  if(width>=900){
   assert.equal(await page.locator('.ajc__label').first().evaluate(e=>getComputedStyle(e).backgroundColor),'rgba(0, 0, 0, 0)');
   const alignment=await page.evaluate(()=>{
    const svg=document.querySelector('.ajc__map');return [...document.querySelectorAll('.ajc__mapMarkers circle')].map((c,i)=>{
     const p=svg.createSVGPoint();p.x=c.cx.baseVal.value;p.y=c.cy.baseVal.value;const a=p.matrixTransform(svg.getScreenCTM());
     const b=document.querySelectorAll('.ajc__pt')[i].getBoundingClientRect();return Math.hypot(a.x-b.x-b.width/2,a.y-b.y-b.height/2);
    });
   });assert(Math.max(...alignment)<1.5,'Marker alignment: '+Math.max(...alignment));
  }else{
   assert(await page.locator('.ajc__mapMarkers').isVisible());
   assert.equal(await page.locator('.ajc__mapMarkers circle').first().evaluate(e=>getComputedStyle(e).fill),'rgb(73, 55, 25)');
   const australia=page.locator('.ajc__land[data-country="Australia"]');await australia.tap();
   assert.equal(await page.locator('#ajc-panel-name').textContent(),'Australia');
   await page.locator('[data-panel-close]').tap();
   // Browser-native magnification and touch panning need no extra map controller.
   const cdp=await page.context().newCDPSession(page);
   await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:2});
   const scale=await page.evaluate(()=>visualViewport.scale);assert(scale>1.5,'Native page scale: '+scale);
   await page.screenshot({path:out+'/map-'+width+'-native-zoom.png'});
   await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:1});
  }
  await page.setViewportSize({width:width===320?390:width-40,height:780});await page.waitForTimeout(300);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  report.push(width+'px: country focus/boundary, directory counts/restoration, markers, '+(width<900?'touch + native page magnification rendering':'transparent labels + geographic layer alignment')+', resize/overflow passed');
  await page.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(out+'/map-results.json',JSON.stringify({coverage,report,errors,limitations},null,2));
 console.log(report.join('\n'));await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
