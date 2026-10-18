import pathlib,re,json,collections,html
base=pathlib.Path("site/japan/tokyo")
pages=sorted(base.glob("*/index.html"))
rows=[]
for path in pages:
 t=path.read_text(encoding="utf8")
 plain=html.unescape(re.sub(r"<[^>]+>"," ",t))
 headings=re.findall(r'<h2[^>]*>(.*?)</h2>',t)
 fig=re.search(r'<figure class="tokyo-article-photo-v1">.*?</figure>',t,re.S)
 svg=bool(fig and ".svg" in fig.group())
 textblocks=[html.unescape(re.sub(r"<[^>]+>"," ",x)).strip() for x in re.findall(r'<p[^>]*>(.*?)</p>',t,re.S)]
 rows.append({"slug":path.parent.name,"svg_in_body":svg,"paragraphs":len(textblocks),"generic_headings":[x for x in headings if x in {"이 주제를 선택하기 전에","시간 낭비를 줄이는 실제 여행 동선","가격·영업시간·예약에서 놓치기 쉬운 조건","자주 묻는 질문","방문자가 가장 많이 혼동하는 세 가지"}],"content_words":len(plain.split()),"verified_date_claim":"공식 정보 확인일" in plain,"official_links":len(re.findall(r'href="https?://',t))})
counter=collections.Counter()
for item in rows:counter.update(item["generic_headings"])
report={"article_count":len(rows),"body_svg":sum(x["svg_in_body"] for x in rows),"generic_heading_frequencies":dict(counter),"official_verified_date_claims":sum(x["verified_date_claim"] for x in rows),"zero_external_links":sum(x["official_links"]==0 for x in rows),"needs_editorial_review":[x for x in rows if x["generic_headings"] or x["verified_date_claim"] or x["svg_in_body"]],"limitations":"Automated structure audit only. Content accuracy, operating times, prices and actual routes require manual confirmation against individual official sources."}
pathlib.Path("audit-reports/tokyo-220-content-quality.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k not in ("needs_editorial_review","limitations")},ensure_ascii=False))
