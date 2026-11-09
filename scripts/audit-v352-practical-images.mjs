import { readFile, mkdir, writeFile } from 'node:fs/promises';
const html = await readFile('site/practical/index.html', 'utf8');
const cards = [...html.matchAll(/<a class="dircard" href="([^"]+)"><img[^>]*?src="([^"]+)"[^>]*>[\s\S]*?<h2>([^<]+)<\/h2>/g)]
  .map(m => ({route:m[1],image:m[2],title:m[3]}));
const byImage = new Map();
for(const c of cards) byImage.set(c.image,[...(byImage.get(c.image)||[]),c]);
const reused = [...byImage.entries()].filter(([,list])=>list.length>=2)
  .map(([image,list])=>({image,count:list.length,routes:list.map(x=>x.route),titles:list.map(x=>x.title)}))
  .sort((a,b)=>b.count-a.count);
const knownMismatches = [
  ['/practical/hokkaido-winter-bus-tour/','/images/hokkaido.jpg','autumn temple photograph used for winter Hokkaido bus tour'],
  ['/practical/japan-luggage-delivery/','/images/car.jpg','tram photograph used for luggage delivery'],
  ['/practical/setsugekka-train/','/images/rail.jpg','generic Hiroshima tram used for Niigata Setsugekka train']
].map(([route,image,reason])=>({route,image,reason,stillPresent:cards.some(c=>c.route===route&&c.image===image)}));
const report={cards:cards.length,reused,knownMismatches,policy:'Only replace with source-verified real photos of the exact subject; no fabricated or unrelated substitute photos.'};
await mkdir('audit-reports/v352',{recursive:true});
await writeFile('audit-reports/v352/practical-image-inventory.json',JSON.stringify(report,null,2)+'\n');
console.log('V352_PRACTICAL_IMAGE_INVENTORY',JSON.stringify({cards:cards.length,reusedGroups:reused.length,knownUnresolved:knownMismatches.filter(x=>x.stillPresent)}));
