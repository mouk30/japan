#!/usr/bin/env python3
"""Connect recorded location-specific WebP to its Tokyo article and OG metadata.
The remainder of 220 pages stay untouched rather than getting incorrect substitutes."""
import json,pathlib,re,html
root=pathlib.Path("site")
pages=sorted((root/"japan/tokyo").glob("*/index.html"))
assert len(pages)==220,len(pages)
photos=json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf8"))
by={p["slug"]:p for p in photos}
changed=0; checked=0
for page in pages:
 slug=page.parent.name
 p=by.get(slug)
 if not p:continue
 image=(root/p["src"].lstrip("/"))
 if not image.is_file() or image.read_bytes()[:4]!=b"RIFF":raise RuntimeError("Bad photo "+str(image))
 text=page.read_text(encoding="utf8")
 head='https://www.nipponferry.com'+p["src"]
 if 'property="og:image"' not in text:
  text=text.replace("</head>",'<meta property="og:image" content="'+html.escape(head,quote=True)+'"><meta name="twitter:card" content="summary_large_image"></head>',1)
 if 'tokyo-article-photo-v1' not in text:
  title=html.escape(p["title"],quote=True)
  link=html.escape(p["source"],quote=True)
  author=html.escape(p["credit"])
  license=html.escape(p["license"])
  figure='<figure class="tokyo-article-photo-v1"><img src="'+html.escape(p["src"],quote=True)+'" alt="'+title+' — 실제 현장 사진" loading="lazy" decoding="async"><figcaption>사진: '+author+' · '+license+' · <a href="'+link+'" target="_blank" rel="noopener noreferrer">원본 및 이용 조건</a></figcaption></figure>'
  m=re.search(r"<main\\b[^>]*>",text,re.I)
  if not m:raise RuntimeError("Missing main element: "+str(page))
  text=text[:m.end()]+figure+text[m.end():]
 page.write_text(text,encoding="utf8")
 changed+=1
 checked+=1
css=root/"tokyo-guide.css"
st=css.read_text(encoding="utf8")
if ".tokyo-article-photo-v1{" not in st:
 st+='\n/* Licensed, subject-matched article imagery */\n.tokyo-article-photo-v1{margin:18px auto 24px;max-width:900px}.tokyo-article-photo-v1 img{display:block;width:100%;max-height:480px;object-fit:cover;border-radius:16px}.tokyo-article-photo-v1 figcaption{font-size:12px;line-height:1.5;color:#627387;margin-top:8px}.tokyo-article-photo-v1 figcaption a{text-decoration:underline}\n'
 css.write_text(st,encoding="utf8")
print(json.dumps({"pages":len(pages),"photo_articles_updated":changed,"photo_coverage_pct":round(changed/len(pages)*100,1)}))
