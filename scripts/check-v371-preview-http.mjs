#!/usr/bin/env node
// V371: fail-closed HTTP smoke test for a real Vercel Preview URL.
// Usage: node scripts/check-v371-preview-http.mjs https://preview.example.vercel.app/
// Requires an externally accessible preview; a READY build alone is not proof of accessibility.
const raw = process.argv[2];
if (!raw) { console.error('Usage: node scripts/check-v371-preview-http.mjs https://preview-host/'); process.exit(2); }
let base;
try {
  base = new URL(raw);
  if (base.protocol !== 'https:' || !base.hostname) throw new Error('HTTPS URL required');
  if (base.username || base.password) throw new Error('Credentials in URL are forbidden');
} catch (error) { console.error('Invalid preview URL:', error.message); process.exit(2); }
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 15000);
try {
  const response = await fetch(base, { signal: controller.signal, redirect: 'follow', headers: { 'user-agent': 'NIPPONFERRY-V371-preview-smoke/1.0' } });
  const html = await response.text();
  const failures = [];
  // A successful response from an unrelated redirect target is not a valid Preview smoke test.
  const finalUrl = new URL(response.url);
  if (finalUrl.origin !== base.origin) failures.push('Redirected outside requested Preview origin');
  if (/\/(?:login|signin|auth)(?:\/|$)/i.test(finalUrl.pathname)) failures.push('Redirected to authentication page');
  if (!response.ok) failures.push('HTTP status ' + response.status);
  if (!/text\/html/i.test(response.headers.get('content-type') || '')) failures.push('Non-HTML content-type');
  if (!/<html[\s>]/i.test(html) || !/<title[\s>]/i.test(html)) failures.push('Missing HTML/title (possible login or error page)');
  if (/vercel authentication|authentication required|deployment protection/i.test(html.slice(0, 15000))) failures.push('Preview appears access-protected');
  const canonical = html.match(/<link\b[^>]*rel=["']canonical["'][^>]*>/i)?.[0] || html.match(/<link\b[^>]*href=["'][^"']+["'][^>]*rel=["']canonical["'][^>]*>/i)?.[0];
  if (!canonical) failures.push('No canonical link on homepage');
  console.log(JSON.stringify({ url: base.origin + base.pathname, status: response.status, finalUrl: response.url, htmlBytes: html.length, canonicalPresent: Boolean(canonical), failures }, null, 2));
  if (failures.length) process.exitCode = 1;
} catch (error) {
  console.error('Preview HTTP check blocked/failed:', error.message);
  process.exitCode = 1;
} finally { clearTimeout(timeout); }
