import pathlib,re,json
root=pathlib.Path("site/japan/tokyo")
hub=(root/"index.html").read_text()
slugs=[u.strip("/").split("/")[-1] for u in re.findall(r'<a\s+class="tky-card"[^>]*href="([^"]+)"',hub)[:20]]
report=[]
for slug in slugs:
 p=root/slug/"index.html"
 s=p.read_text()
 assert 'tokyo-editorial-v1' in s,slug
 before=len(s)
 removed=[]
 for label,pat in [
  ("repetitive introduction",r'<section class="tky-block"><div class="tky-dated">.*?<h2>이 주제를 선택하기 전에</h2>.*?</section>'),
  ("generic route",r'<section class="tky-block" id="plan"><h2>시간 낭비를 줄이는 실제 여행 동선</h2>.*?</section>'),
  ("generic tickets",r'<section class="tky-block" id="tickets"><h2>가격·영업시간·예약에서 놓치기 쉬운 조건</h2>.*?</section>'),
  ("generic faq",r'<section class="tky-block"><h2>자주 묻는 질문</h2>.*?</section>'),
  ("generic field checklist",r'<section class="tky-block tokyo-field-check-v307"[^>]*>.*?</section>')
 ]:
  s,n=re.subn(pat,"",s,count=1,flags=re.S)
  if n:removed.append(label)
 s=s.replace('href="#plan"','href="#field-guide"').replace('href="#tickets"','href="#field-guide"')
 # Add concise internal anchor navigation after actual published field guide.
 if 'id="field-guide"' not in s:raise ValueError(slug+" field guide missing")
 if not removed:raise ValueError(slug+" no generic text found")
 p.write_text(s)
 report.append({"slug":slug,"removed":removed,"bytes_saved":before-len(s)})
out=pathlib.Path("audit-reports/tokyo-v1-v20-repeat-cleanup.json")
out.write_text(json.dumps({"updated":len(report),"pages":report,"notes":"Preserved original official links, editorial field guides, existing verified facility specifics and SEO metadata; not a live timetable/price certification."},ensure_ascii=False,indent=2))
print(json.dumps({"updated":len(report),"bytes_saved":sum(x["bytes_saved"] for x in report)},ensure_ascii=False))
