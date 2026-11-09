import fs from 'node:fs';
import path from 'node:path';
const names=['','area','beppu','couple','family','first-trip','fuji','fukuoka','hakodate','hakone','hiroshima','hokkaido','hotel','kagoshima','kobe','kyoto','nagasaki','nagoya','okinawa','osaka','otaru','ryokan','sapporo','sendai','shimonoseki','tokyo','tsushima','yokohama'];
const base='site/stay';
const found=[];
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.name==='index.html')found.push(p.replaceAll('\\','/'));}}
walk(base);
const expected=names.map(n=>path.posix.join(base,n,'index.html')).sort();
if(JSON.stringify(found.sort())!==JSON.stringify(expected))throw Error('Existing stay index page set changed: '+JSON.stringify(found));
for(const n of names){const f=path.posix.join(base,n,'index.html');const html=fs.readFileSync(f,'utf8');const matches=[...html.matchAll(/<a[^>]*href=['\"]\/booking[^'\"]*['\"][^>]*>크루즈·페리 예약 준비 가이드 →/g)];if(matches.length!==1)throw Error(f+': expected exactly one explicit ferry booking CTA, got '+matches.length);if(!html.includes('rel=\'canonical\'')&&!html.includes('rel="canonical"'))throw Error(f+': canonical missing');if(!html.includes('name=\'robots\'')&&!html.includes('name="robots"'))throw Error(f+': robots missing');}
console.log('PASS: 28 pre-existing /stay/ guides; explicit ferry CTA, canonical and robots present. Does not validate photo rights or browser rendering.');
