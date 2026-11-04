import fs from 'node:fs';
import {ChromeVisualBrowser} from './packages/candidate/archify/bin/visual-check.mjs';
const browser=new ChromeVisualBrowser('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
try{
 const session=await browser.sessionPromise;
 await browser.inspect({artifactPath:process.cwd()+'/runs/association-base/workspace/output/shared-opportunity-identifiers.html',width:1440,height:900,theme:'light'});
 const evaluate=async expression=>(await browser.cdp.send('Runtime.evaluate',{expression,returnByValue:true},session)).result.value;
 const measure=()=>evaluate('({innerHeight,scrollHeight:document.documentElement.scrollHeight,diagram:document.querySelector(".diagram-container").getBoundingClientRect().toJSON(),card:document.querySelector(".cards")?.getBoundingClientRect().toJSON()})');
 const before=await measure();
 await evaluate(`document.querySelectorAll('.diagram-container,.diagram-container>svg').forEach(e=>{const r=e.getBoundingClientRect();for(const [k,v] of Object.entries({width:r.width+'px',height:r.height+'px','min-height':r.height+'px','max-height':r.height+'px','box-sizing':'border-box'}))e.style.setProperty(k,v,'important')})`);
 const response=await browser.cdp.send('Emulation.setDeviceMetricsOverride',{width:1440,height:before.scrollHeight,deviceScaleFactor:1,mobile:false},session);
 await browser.cdp.send('Runtime.evaluate',{expression:'new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))',awaitPromise:true},session);
 const after=await measure();
 const shot=await browser.cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false},session);
 const bytes=Buffer.from(shot.data,'base64');fs.writeFileSync('fullpage-probe.png',bytes);
 console.log(JSON.stringify({before,after,response,pngWidth:bytes.readUInt32BE(16),pngHeight:bytes.readUInt32BE(20)},null,2));
}finally{await browser.close()}
