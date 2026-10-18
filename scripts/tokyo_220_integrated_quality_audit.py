import pathlib,re,json,collections,urllib.parse,posixpath,html
base=pathlib.Path("site");index=(base/"japan/tokyo/index.html").read_text(encoding="utf8")
slugs=re.findall(r'<a\s+class="tky-card"[^>]*href="/japan/tokyo/([^/]+)/"',index)
assert len(slugs)==220,(len(slugs),"Expected 220 cards")
js=(base/"tokyo-card-photos.js").read_text(encoding="utf8")
photos=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
out=[];internal_missing=[];cross_links=0;link_total=0;pages_with_issues=0;schemas_failed=0
exists=lambda p:(base/p.lstrip("/")).exists() or (base/p.lstrip("/")/"index.html").exists()
for v,slug in enumerate(slugs,1):
 path=base/"japan/tokyo"/slug/"index.html"
 if not path.exists():out.append({"v":v,"slug":slug,"errors":["missing_article"]});continue
 s=path.read_text(encoding="utf8");issues=[];warnings=[]
 title=re.search(r'<title>(.*?)</title>',s,re.S)
 desc=re.search(r'<meta\s+name="description"\s+content="([^"]*)"',s)
 canon=re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"',s)
 if not title or not title.group(1).strip():issues.append("missing_title")
 if not desc or len(desc.group(1).strip())<35:warnings.append("description_short_or_missing")
 expected="https://www.nipponferry.com/japan/tokyo/"+slug+"/"
 if not canon or canon.group(1)!=expected:issues.append("bad_or_missing_canonical")
 scripts=re.findall(r'<script\s+type="application/ld\+json"\s*>(.*?)</script>',s,re.S)
 if not scripts:issues.append("missing_jsonld")
 for script in scripts:
  try:json.loads(html.unescape(script))
  except:issues.append("invalid_jsonld");schemas_failed+=1
 if '<h1' not in s:issues.append("missing_h1")
 if "tokyo-article-photo-v1" not in s:issues.append("missing_hero")
 photo=photos.get(slug)
 if not photo:issues.append("missing_card_photo_map")
 elif not exists(photo["src"]):issues.append("missing_card_image_file")
 for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',s,re.I):
  if src.startswith("/") and not exists(src):issues.append("missing_img:"+src[:80])
 for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"',s,re.I):
  href=html.unescape(href);link_total+=1
  if href.startswith("#"):
   if href!="#" and not re.search(r'\bid=["\\\']'+re.escape(href[1:])+r'["\\\']',s):warnings.append("unresolved_fragment:"+href)
   continue
  if not href.startswith("/") or href.startswith("//"):continue
  pathonly=urllib.parse.urlsplit(href).path
  if not exists(pathonly):
   internal_missing.append({"v":v,"slug":slug,"href":href})
  if pathonly.startswith("/japan/tokyo/"):cross_links+=1
 if "방문자가 가장 많이 혼동하는 세 가지" in s:warnings.append("generic_three_misconceptions")
 if "이 주제를 선택하기 전에" in s:warnings.append("generic_preamble")
 if v==213:warnings.append("2010_historical_illumination_photo_not_current")
 if issues:pages_with_issues+=1
 out.append({"v":v,"slug":slug,"errors":sorted(set(issues)),"warnings":sorted(set(warnings)),"image_source":(photo or {}).get("source_file")})
summary={"total":len(slugs),"pages_with_errors":pages_with_issues,"missing_internal_links":len(internal_missing),"internal_link_examples":internal_missing[:120],"invalid_schema_blocks":schemas_failed,"local_links_checked":link_total,"tokyo_internal_links":cross_links,"generic_preamble_pages":sum("generic_preamble" in x.get("warnings",[]) for x in out),"generic_three_pages":sum("generic_three_misconceptions" in x.get("warnings",[]) for x in out),"editorial_image_count":sum((photos.get(s) or {}).get("src","").endswith(".svg") for s in slugs),"warnings":"Automated source audit: not a browser/mobile QA, complete link HTTP check, current facility fact check, or independent visual photo verification.","pages":out}
pathlib.Path("audit-reports/tokyo-220-integrated-quality-audit.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in summary.items() if k not in ("pages","internal_link_examples")},ensure_ascii=False))
