import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const excluded = new Set(['.git', 'node_modules', '.next', 'dist', 'build', 'audit-reports']);
function collect(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (excluded.has(entry.name)) continue;
    const filename = path.join(dir, entry.name);
    if (entry.isDirectory()) collect(filename, out);
    else if (entry.isFile() && filename.endsWith('.html')) out.push(filename);
  }
  return out;
}
const files = collect(root);
const bookingPattern = /예약|예매|발권|승선|수속|운항|시간표|요금|유류할증료|booking|reservation|check.in|timetable|fare/i;
const findings = [];
let relevantLinks = 0;
for (const file of files) {
  const html = fs.readFileSync(file, 'utf8');
  for (const match of html.matchAll(/<a\b([^>]*?)>([\s\S]*?)<\/a\s*>/gi)) {
    const attrs = match[1];
    const hrefMatch = attrs.match(/\bhref\s*=\s*(["'])(.*?)\1/i);
    if (!hrefMatch) continue;
    const href = hrefMatch[2].trim();
    if (!/^https?:\/\//i.test(href)) continue;
    const label = match[2].replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 160);
    if (!bookingPattern.test(label)) continue;
    relevantLinks++;
    let reason = null;
    try {
      const url = new URL(href);
      if (url.protocol === 'http:') reason = 'insecure-http-review';
      else if (url.username || url.password) reason = 'embedded-credentials-review';
      else if (/^(localhost|127\.0\.0\.1|0\.0\.0\.0)$/i.test(url.hostname)) reason = 'local-host-review';
    } catch { reason = 'invalid-url-review'; }
    if (reason) findings.push({ file: path.relative(root, file), label, href, reason });
  }
}
const report = { version: 'V369', mode: 'read-only', htmlFiles: files.length, relevantExternalLinks: relevantLinks, findingsCount: findings.length, findings, note: 'Candidates only: no network reachability, booking availability, or operator ownership verification performed.' };
fs.mkdirSync('audit-reports/v369', { recursive: true });
fs.writeFileSync('audit-reports/v369/external-booking-link-safety.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ htmlFiles: files.length, relevantExternalLinks: relevantLinks, findingsCount: findings.length }));
