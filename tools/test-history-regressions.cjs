const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.CIRS_BROWSER_DIR?path.join(process.env.CIRS_BROWSER_DIR,'node_modules/playwright-core'):'playwright-core');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CIRS_CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const expected=['cbse-2019','ncc-2025','mun-2025','report-2025','cbse-2026','ib-2026'];
 for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
  const p=await b.newPage({viewport,reducedMotion:'reduce'});await p.goto((process.env.CIRS_PREVIEW_URL||'http://127.0.0.1:8878')+'/school-history.html');
  for(const id of ['report-2019','ranking-2019'])assert.equal(await p.locator('#record-'+id+' .hx-rec__source a[href$=".pdf"]').getAttribute('href'),'assets/documents/school-info/annual-report-2019.pdf');
  assert.deepEqual(await p.locator('#hx-grid [data-hx-open]').evaluateAll(es=>es.slice(-6).map(e=>e.dataset.hxOpen)),expected);
  for(const filter of ['all','later']){
   await p.locator('[data-hx-filter="'+filter+'"]').click();
   await p.locator('[data-hx-open="cbse-2019"]').click();
   for(const id of expected){
    await p.waitForFunction(id=>location.hash==='#record-'+id,id);
    assert.equal(await p.locator('#hx-dialog-title').textContent(),await p.locator('#record-'+id+' .hx-rec__title').textContent());
    if(id!==expected.at(-1))await p.locator('[data-hx-step="1"]').click();
   }
   assert.equal(await p.locator('[data-hx-step="1"]').isDisabled(),true);
   for(const id of expected.slice(0,-1).reverse()){
    await p.locator('[data-hx-step="-1"]').click();await p.waitForFunction(id=>location.hash==='#record-'+id,id);
   }
   await p.locator('[data-hx-close]').click();await p.waitForFunction(()=>!document.getElementById('hx-dialog').open);
  }
  console.log('PASS History sources/order and filtered Earlier/Later navigation '+viewport.width);await p.close();
 }
 await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
