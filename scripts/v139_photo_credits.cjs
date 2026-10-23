'use strict';
/* V139: compact photo attributions at build time.
 * Existing photographer, source URL, CC license, adaptation notice and distinctions
 * are preserved byte-for-byte inside a native, accessible disclosure near the footer.
 * Content/operations citations and general notes are not suppressed.
 */
const CLASS_HINT = '(?:photo[-_]?credit|photo[-_]?source|photo[-_]?provenance|image[-_]?credit|image[-_]?source|nf-v\\d+-credit|nf\\d+-credit|nf84-home__meta|nf83-credit|d62-source|v65-note|d61-home-note|v104-theme-note)';
const CREDIT_BLOCK = new RegExp('<(p|figcaption|div|a|small)\\b([^>]*\\bclass\\s*=\\s*"[^"]*' + CLASS_HINT + '[^"]*"[^>]*)>([\\s\\S]*?)<\\/\\1>', 'gi');
const FIGCAPTION = /<figcaption\b([^>]*)>([\s\S]*?)<\/figcaption>/gi;
const LICENSE_CLUES = /commons\.wikimedia\.org|creativecommons\.org|CC\s*BY|Public\s+domain|저작권|사진|촬영|이미지|원본|출처|WebP|photo/i;
const STANDALONE_CLUES = /commons\.wikimedia\.org|creativecommons\.org|CC\s*BY|Public\s+domain|사진 원본|원본 사진|저작권 표시/i;

function escapeText(t){
  return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function textOnly(s){
  return s.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
}
function compactPhotoAttribution(html){
  if (typeof html !== 'string'||!html.includes('</body>'))return {html,credits:0};
  if (html.includes('class="nf-photo-credits-panel"'))return {html,credits:0};
  const entries=[];
  let result=html.replace(CREDIT_BLOCK,(full,tag,attrs,body)=>{
    const cls=attrs.match(/\bclass\s*=\s*"([^"]+)"/i)?.[1]||'';
    if (!LICENSE_CLUES.test(body))return full;
    // A regional note is only photo-only when original photographic source links exist.
    if (/(?:^|\s)(?:v65-note|d61-home-note|v104-theme-note)(?:\s|$)/.test(cls)&&!/commons\.wikimedia\.org/.test(body))return full;
    // Don't move potentially complex cards or structural navigation containers.
    if(tag.toLowerCase()==='div'&&/<(?:div|section|article|nav)\b/i.test(body))return full;
    if(body.length>12000)return full;
    entries.push({kind:cls,content:tag.toLowerCase()==='a'?full:body});
    return '';
  });
  // Some source captions have no class. Only move photo-attribution captions
  // whose content has a specific photo/license link; keep ordinary captions.
  result=result.replace(FIGCAPTION,(full,attrs,body)=>{
    if(!STANDALONE_CLUES.test(body)||!/(?:사진|원본|Photo|CC\s*BY|license|저작권)/i.test(body))return full;
    if(body.length>4000||/<(?:figcaption|figure|div)\b/i.test(body))return full;
    entries.push({kind:'figcaption',content:body});
    return '';
  });
  if(!entries.length)return {html,credits:0};
  const creditItems=entries.map((e,i)=>{
    const first=textOnly(e.content).slice(0,70);
    const label=first.length>0?first:'사진 '+(i+1);
    return '<li><strong>'+escapeText(label)+'</strong><div>'+e.content+'</div></li>';
  }).join('');
  const block='<details class="nf-photo-credits-panel" aria-label="사진 출처와 저작권 정보">'+
    '<summary>사진 출처·저작권</summary><ol class="nf-photo-credits-panel__list">'+
    creditItems+'</ol></details>';
  // Keep a single compact disclosure immediately before the existing footer.
  // When there is no footer, insert just before </body>.
  if(/<footer\b/i.test(result)){
    result=result.replace(/<footer\b/i,block+'<footer');
  }else{
    result=result.replace(/<\/body>/i,block+'</body>');
  }
  const css='<link rel="stylesheet" href="/nf-v139-photo-credits.css?v=20261023">';
  if(!result.includes('/nf-v139-photo-credits.css')){
    result=result.replace(/<\/head>/i,css+'</head>');
  }
  return {html:result,credits:entries.length};
}
module.exports={compactPhotoAttribution};
