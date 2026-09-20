const { chromium } = require('C:/Users/YEP15/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
const browser=await chromium.launch({channel:'msedge',headless:true});
const results=[];
for(const [width,height] of [[1920,1080],[1440,900],[1366,768],[1024,768],[768,1024],[430,932],[390,844],[360,800],[1440,600]]){
 const context=await browser.newContext({viewport:{width,height}});const page=await context.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/temp-home-intro/');await page.waitForTimeout(2400);
 const state=await page.evaluate(()=>({active:document.documentElement.classList.contains('intro-active'),locked:document.body.classList.contains('is-locked'),overflow:document.documentElement.scrollWidth>innerWidth,result:document.documentElement.dataset.introResult}));
 await page.screenshot({path:`temp-home-intro/${width}x${height}.png`});results.push({width,height,...state,errors});await context.close();
}
for(const mode of ['skip','escape','reload','reduced','no-js','storage-blocked','resize']){
 const context=await browser.newContext({reducedMotion:mode==='reduced'?'reduce':'no-preference',javaScriptEnabled:mode!=='no-js'});const page=await context.newPage();
 if(mode==='storage-blocked') await page.addInitScript(()=>{Object.defineProperty(window,'sessionStorage',{get(){throw Error('blocked')}})});
 await page.goto('http://127.0.0.1:8765/temp-home-intro/');
 if(mode==='skip') await page.locator('.home-intro__skip').click();
 if(mode==='escape') {await page.waitForTimeout(200);await page.keyboard.press('Escape');}
 if(mode==='resize'){await page.waitForTimeout(200);await page.setViewportSize({width:390,height:844});}
 await page.waitForTimeout(2200);
 if(mode==='reload'){await page.reload();await page.waitForTimeout(300);}
 results.push({mode,...await page.evaluate(()=>({active:document.documentElement.classList.contains('intro-active'),locked:document.body.classList.contains('is-locked'),result:document.documentElement.dataset.introResult,visible:!!document.querySelector('h1').getBoundingClientRect().height}))});await context.close();
}
fs.writeFileSync('temp-home-intro/test-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));await browser.close();
})();
