import pathlib,json,re,html
rows=json.loads("[[\"tokyo-subway-ticket-24-48-72\",\"도쿄 서브웨이 티켓 24·48·72시간권\",\"PASS GUIDE\",\"승차권 종류 · 이용 가능 노선 · 구매 조건\"],[\"odaiba-kirakira-donki\",\"오다이바 돈키호테 쇼핑 안내\",\"STORE GUIDE\",\"실제 점포 운영·다이버시티 건물 동선\"],[\"tokyo-toddler-underfive\",\"5세 이하 자녀 동반 도쿄 여행\",\"FAMILY GUIDE\",\"입장 연령 · 유모차 · 휴식 동선\"],[\"tokyo-lastday-taxfree-baggage\",\"도쿄 출국일 면세·짐 보관\",\"DEPARTURE GUIDE\",\"면세 조건 · 보관 장소 · 공항 이동\"]]")
root=pathlib.Path("site")
jsf=root/"tokyo-card-photos.js";s=jsf.read_text(encoding="utf8");m=json.loads(s.split("const map=",1)[1].split(";document.querySelectorAll",1)[0]);updated=[]
for i,(slug,title,en,sub) in enumerate(rows):
 path=root/"images/tokyo-editorial"/(slug+".svg");path.parent.mkdir(parents=True,exist_ok=True)
 colors=[("#102d4b","#4b7897"),("#2d305a","#8970ad"),("#174c4a","#56a6a0"),("#33415c","#7e95b8")]
 c1,c2=colors[i]
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs><rect width="1280" height="720" fill="url(#g)"/><circle cx="1020" cy="330" r="228" fill="none" stroke="#f0d69a" stroke-width="3" opacity=".68"/><circle cx="1020" cy="330" r="164" fill="none" stroke="#f0d69a" stroke-width="2" opacity=".4"/><text x="76" y="155" font-size="28" fill="#f0d69a" font-family="Arial,sans-serif" font-weight="bold">NIPPONFERRY · TOKYO</text><text x="76" y="308" font-size="46" fill="white" font-family="sans-serif" font-weight="bold">{html.escape(title)}</text><text x="76" y="382" font-size="28" fill="#f0d69a" font-family="Arial,sans-serif">{html.escape(sub)}</text><text x="76" y="478" font-size="23" fill="#eee" font-family="Arial,sans-serif">{en}</text><text x="76" y="629" font-size="21" fill="white" font-family="sans-serif">자체 제작 정보형 디자인 · 현장 실사진 아님</text></svg>'
 path.write_text(svg,encoding="utf8")
 img="/images/tokyo-editorial/"+slug+".svg"
 m[slug]={"src":img,"alt":title+" 정보형 이미지, 현장 사진 아님","caption":"NIPPONFERRY 자체 제작 정보형 그래픽 · 실제 현장 사진 아님","license":"Original editorial SVG","author":"NIPPONFERRY","source":"","source_file":""}
 p=root/"japan/tokyo"/slug/"index.html";doc=p.read_text(encoding="utf8")
 fig='<figure class="tokyo-article-photo-v1"><img src="'+img+'" alt="'+html.escape(title)+' 정보형 그래픽 (실제 사진 아님)" loading="lazy" decoding="async" width="1280" height="720"><figcaption>NIPPONFERRY 제작 정보형 그래픽 · 실제 현장 사진이 아닙니다.</figcaption></figure>'
 doc,n=re.subn(r'<figure class="tokyo-article-photo-v1">.*?</figure>',lambda _:fig,doc,count=1,flags=re.S)
 assert n==1,(slug,n)
 p.write_text(doc,encoding="utf8");updated.append(slug)
jsf.write_text(s.split("const map=",1)[0]+"const map="+json.dumps(m,ensure_ascii=False,separators=(",",":"))+";document.querySelectorAll"+s.split(";document.querySelectorAll",1)[1],encoding="utf8")
report={"updated":updated,"reason":"Image subject insufficient to communicate page's service-specific focus; existing photos replaced with clearly labeled editorial graphic. The original pictures were not necessarily geographically false.","official_link_conclusion":"teamlabplanets.dmm.com official ticket page and /en/guide/access_method were independently confirmed to open, despite CI HEAD 404; they were correctly retained.","next_priority":"Manually inspect the other images in actual visual content; live fact verification of 2026 fare and operating conditions."}
pathlib.Path("audit-reports/tokyo-priority-trust-corrections.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print("updated",len(updated))
