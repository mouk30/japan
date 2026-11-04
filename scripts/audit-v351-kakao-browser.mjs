import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

const base = process.env.LOCAL_BASE_URL || 'http://127.0.0.1:8765';
const pages = [
  ['home', '/'],
  ['cruise-ports', '/things-to-do/cruise-ports/'],
  ['takamatsu', '/things-to-do/takamatsu-cruise-udon-market-return/'],
  ['things-to-do', '/things-to-do/'],
  ['food', '/things-to-do/food-experience/'],
  ['osaka-return', '/guide/osaka-busan-ferry/']
];
const sizes = [['mobile', 390, 844], ['tablet', 768, 1024], ['desktop', 1440, 900]];
const expected = 'https://open.kakao.com/o/g4ilP4Ji';
const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
const report = [];
await mkdir('audit-reports/v351', { recursive: true });
for (const [name, route] of pages) {
  for (const [device, width, height] of sizes) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const errors = [];
    let detail = {};
    try {
      const response = await page.goto(base + route, { waitUntil: 'domcontentloaded', timeout: 30000 });
      if (response?.status() !== 200) errors.push('HTTP_' + response?.status());
      // Wait for the lazy-loaded floating image before measuring its natural dimensions.
      await page.locator('a.kakao-float img').evaluate(async (img) => {
        if (!img.complete) await new Promise(resolve => {
          img.addEventListener('load', resolve, { once: true });
          img.addEventListener('error', resolve, { once: true });
          setTimeout(resolve, 5000);
        });
        if (img.complete && img.naturalWidth > 0) await img.decode().catch(() => {});
      });
      detail = await page.evaluate((expected) => {
        const buttons = [...document.querySelectorAll('a.kakao-float')];
        const a = buttons[0];
        const img = a?.querySelector('img');
        const r = a?.getBoundingClientRect();
        const style = a && getComputedStyle(a);
        const center = r && document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        const hit = !!a && !!center && (center === a || a.contains(center));
        const overlapping = r ? [...document.querySelectorAll('a,button,[role="button"]')].filter(el => el !== a && !a?.contains(el)).filter(el => {
          const b = el.getBoundingClientRect();
          const intersection = Math.max(0, Math.min(r.right,b.right)-Math.max(r.left,b.left))*Math.max(0, Math.min(r.bottom,b.bottom)-Math.max(r.top,b.top));
          return intersection > 0 && getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).display !== 'none';
        }).slice(0,5).map(el=>({tag:el.tagName, className:String(el.className).slice(0,60),href:el.getAttribute('href'),text:(el.textContent||'').trim().slice(0,90),rect:(()=>{const q=el.getBoundingClientRect();return {left:q.left,top:q.top,right:q.right,bottom:q.bottom}})()})) : [];
        return {
          count: buttons.length, href: a?.href, target: a?.target, rel: a?.rel,
          position: style?.position, visible: !!r && r.width >= 44 && r.height >= 44 && r.left >= -1 && r.top >= -1 && r.right <= innerWidth+1 && r.bottom <= innerHeight+1,
          hit, imageLoaded: !!img && img.complete && img.naturalWidth > 0,
          overlap: overlapping, rect: r && {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}
        };
      }, expected);
      if (detail.count !== 1) errors.push('KAKAO_COUNT_' + detail.count);
      if (detail.href !== expected || detail.target !== '_blank' || !detail.rel?.includes('noopener')) errors.push('KAKAO_LINK');
      if (detail.position !== 'fixed' || !detail.visible) errors.push('KAKAO_NOT_FIXED_VISIBLE');
      if (!detail.imageLoaded) errors.push('KAKAO_IMAGE');
      if (!detail.hit) errors.push('KAKAO_BLOCKED_CENTER');
      if (detail.overlap?.length) errors.push('KAKAO_CTA_OVERLAP');
      if (!errors.length) {
        const popupPromise = page.waitForEvent('popup', { timeout: 5000 });
        await page.locator('a.kakao-float').click({ timeout: 5000 });
        const popup = await popupPromise;
        const url = popup.url();
        detail.clickUrl = url;
        if (!url.startsWith(expected)) errors.push('KAKAO_CLICK_TARGET');
        await popup.close().catch(()=>{});
      }
      await page.screenshot({path:`audit-reports/v351/${name}-${device}.png`,fullPage:false});
    } catch (e) { errors.push('BROWSER_ERROR'); detail.error = String(e).slice(0,300); }
    report.push({ name, route, device, errors, detail });
    await context.close();
  }
}
await browser.close();
const summary = { cases:report.length, passed:report.filter(r=>!r.errors.length).length, failures:report.filter(r=>r.errors.length) };
await writeFile('audit-reports/v351/report.json', JSON.stringify({summary,report},null,2)+'\n');
console.log('V351_KAKAO_BROWSER_QA', JSON.stringify(summary));
if (summary.failures.length) process.exitCode = 1;
