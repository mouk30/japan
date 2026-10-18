import re,json,pathlib,html
base=pathlib.Path("site")
js=(base/"tokyo-card-photos.js").read_text()
photos=json.loads(js.split("const map=",1)[1].split(";document.querySelectorAll",1)[0])
ok=[];skip=[]
for slug,photo in photos.items():
 path=base/"japan"/"tokyo"/slug/"index.html"
 if not path.is_file() or not photo["src"].endswith(".webp"):
  skip.append(slug);continue
 page=path.read_text()
 figure=re.search(r'<figure class="tokyo-article-photo-v1">.*?</figure>',page,re.S)
 if not figure or not photo.get("source"):
  skip.append(slug);continue
 q=lambda t:html.escape(str(t),quote=True)
 new='<figure class="tokyo-article-photo-v1"><img src="'+q(photo["src"])+'" alt="'+q(photo.get("alt","도쿄 여행 사진"))+'" loading="lazy" decoding="async"><figcaption>실제 관련 사진 · '+q(photo.get("author","Wikimedia Commons"))+' · '+q(photo.get("license",""))+' · <a href="'+q(photo["source"])+'" rel="noopener noreferrer" target="_blank">사진 원본 및 라이선스</a></figcaption></figure>'
 page=page[:figure.start()]+new+page[figure.end():]
 page=page.replace("공식 정보 확인일 2026년 10월 17일","작성 당시 정보 기준일 2026년 10월 17일 · 최신 운영정보는 공식 링크에서 재확인")
 path.write_text(page)
 ok.append(slug)
pathlib.Path("audit-reports/tokyo-article-hero-sync.json").write_text(json.dumps({"updated":len(ok),"skipped":skip},ensure_ascii=False,indent=2))
print("Updated",len(ok),"skipped",len(skip))
