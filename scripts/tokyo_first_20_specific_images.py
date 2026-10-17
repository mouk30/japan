#!/usr/bin/env python3
"""First 20 visible Tokyo cards: distinct subject-specific illustrations.
Four existing verified observatory photos are retained unchanged."""
import pathlib,json,re,html,hashlib
root=pathlib.Path("site")
hub=(root/"japan/tokyo/index.html").read_text(encoding="utf8")
top=re.findall(r'<a\s+class="tky-card"[^>]*href="([^"]+)"',hub)[:20]
slugs=[x.rstrip("/").split("/")[-1] for x in top]
assert len(slugs)==20 and len(set(slugs))==20,slugs
photos={x["slug"] for x in json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf8"))}
scenes={
"tokyo-ramen-best-areas":("RAMEN","도쿄 라멘 · 지역별 맛집","noodles"),
"tokyo-sushi-breakfast-guide":("SUSHI","초밥 · 해산물 아침식사","sushi"),
"tokyo-tsukishima-monjayaki":("MONJAYAKI","쓰키시마 철판 몬자야키","griddle"),
"tokyo-yakitori-izakaya-guide":("IZAKAYA","야키토리 · 이자카야","skewers"),
"tokyo-depachika-food-halls":("DEPACHIKA","백화점 지하 식품관","foodhall"),
"tokyo-night-view-observation-comparison":("NIGHT VIEWS","도쿄 야경 전망대 4곳 비교","nightviews"),
"tokyo-subway-route-map-korean":("TOKYO METRO","노선도 · 역번호 · 환승","metromap"),
"tokyo-subway-ticket-24-48-72":("SUBWAY TICKET","24 · 48 · 72시간권","tickets"),
"tokyo-yamanote-line-transfer-guide":("YAMANOTE LINE","JR 야마노테선 · 환승","loop"),
"tokyo-haneda-airport-train-guide":("HANEDA","하네다공항 · 철도 이동","haneda"),
"tokyo-narita-airport-train-guide":("NARITA","나리타공항 · 철도 이동","narita"),
"tokyo-ginza-department-store-route":("GINZA","긴자 백화점 쇼핑 동선","ginza"),
"tokyo-shinjuku-isetan-shopping":("ISETAN","신주쿠 이세탄 백화점","isetan"),
"tokyo-ginza-mitsukoshi-depachika":("MITSUKOSHI","긴자 미쓰코시 · 식품관","mitsukoshi"),
"tokyo-station-character-street":("CHARACTER STREET","도쿄역 캐릭터스트리트","character"),
"tokyo-mega-donki-shibuya":("MEGA DONKI","시부야 메가 돈키호테 · 쇼핑","donki")
}
def rect(x,y,w,h,fill,rx=0,stroke="none",sw=0):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def circle(x,y,r,fill,stroke="none",sw=0):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def line(x1,y1,x2,y2,col,sw=6):
 return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" fill="none"/>'
def label(x,y,t,size=28,color="#f8fafc",weight=700):
 return f'<text x="{x}" y="{y}" font-family="Noto Sans CJK KR,Malgun Gothic,Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(t)}</text>'
def visual(kind):
 gold="#f5c978";milk="#f5eee0";ink="#142f48";mint="#7ed1c7";red="#e58279"
 if kind=="noodles":
  return circle(480,315,160,milk)+circle(480,315,133,"#c5814a")+''.join(f'<path d="M{360+i*26} 280q55 -48 105 0t85 0" fill="none" stroke="#f5d978" stroke-width="9"/>' for i in range(5))+circle(420,315,35,milk)+circle(420,315,20,"#eac65c")+rect(525,250,65,70,"#417d5a",8)+line(330,155,620,245,gold,12)+line(350,132,640,222,milk,9)
 if kind=="sushi":
  return rect(240,255,480,162,"#d2a071",24)+''.join(rect(270+i*108,294,80,72,milk,22)+rect(270+i*108,280,80,37,["#e99273","#eead88","#dba98b","#d76e69"][i],18) for i in range(4))+circle(690,258,45,ink,"#eef4e8",9)+circle(690,258,24,"#485f3a")
 if kind=="griddle":
  return rect(240,206,480,225,"#333d4b",22, "#b8c1c9",15)+circle(480,319,130,"#b87a49")+''.join(circle(380+i*38,280+(i%3)*26,13,["#dbcd8f","#9dc47e","#d18c5d"][i%3]) for i in range(7))+line(620,160,660,340,milk,22)
 if kind=="skewers":
  return rect(260,280,440,140,"#a04c35",24)+''.join(line(310+i*95,170,350+i*95,375,"#d8b68a",9)+''.join(circle(317+i*95+j*7,226+j*36,27,["#c36a45","#e8a771","#ce754b"][j]) for j in range(3)) for i in range(4))
 if kind=="foodhall":
  return rect(230,210,500,220,milk,9)+rect(210,182,540,56,red,8)+''.join(rect(255+i*120,266,92,95,["#e6ab72","#83c7bc","#d98778","#f0c977"][i],10) for i in range(4))+''.join(circle(300+i*120,300,28,milk) for i in range(4))+rect(248,385,465,17,ink,3)
 if kind=="nightviews":
  return ''.join(rect(250+i*132,260-(i%3)*53,92,180+(i%3)*53,"#416789",7) for i in range(4))+''.join(circle(282+i*132,310,9,gold) for i in range(4))+circle(705,175,45,gold)
 if kind=="metromap":
  return ''.join(f'<path d="M{250+i*76} 185V375H{690-i*52}" fill="none" stroke="{c}" stroke-width="13" stroke-linejoin="round"/>' for i,c in enumerate(["#e78675","#74bd8b","#e5bb61","#7d91cc"]))+''.join(circle(250+i*76,260,16,milk,ink,6) for i in range(4))
 if kind=="tickets":
  return ''.join(rect(235+i*166,213,145,206,["#e5b977","#88bfb5","#a7a0d2"][i],13)+label(253+i*166,324,["24H","48H","72H"][i],38,ink) for i in range(3))
 if kind=="loop":
  return '<ellipse cx="480" cy="315" rx="225" ry="120" fill="none" stroke="#a7cf76" stroke-width="25"/>'+''.join(circle(480+225*__import__("math").cos(i*3.14159265/3),315+120*__import__("math").sin(i*3.14159265/3),19,milk,ink,5) for i in range(6))+rect(391,276,178,79,milk,24)+label(423,329,"JR",45,ink)
 if kind in ("haneda","narita"):
  return '<path d="M475 158L504 266L673 310V340L504 323L488 406H462L447 323L278 340V310L447 266Z" fill="#e7eef0"/>'+rect(282,400,400,14,mint,5)+label(380,441,"HND" if kind=="haneda" else "NRT",30,gold)
 if kind in ("ginza","isetan","mitsukoshi"):
  return rect(278,195,404,235,milk,7)+rect(270,185,420,33,red if kind=="isetan" else gold,6)+''.join(rect(302+i*101,244+j*69,68,50,"#91babb",4) for i in range(4) for j in range(2))+rect(433,361,94,69,ink,4)+label(319,177,{"ginza":"GINZA","isetan":"ISETAN","mitsukoshi":"MITSUKOSHI"}[kind],30,milk)
 if kind=="character":
  return rect(270,245,420,190,milk,14)+''.join(circle(360+i*117,278,42,["#e7bb83","#cf9b91","#a6cbbc"][i]) for i in range(3))+''.join(circle(345+i*117,270,5,ink)+circle(375+i*117,270,5,ink) for i in range(3))+label(352,408,"TOKYO STATION",29,ink)
 if kind=="donki":
  return rect(258,182,444,252,"#ece6df",10)+rect(240,200,480,88,"#e6aa4a",12)+label(297,260,"MEGA DONKI",52,ink)+''.join(rect(285+i*96,317,70,78,"#72a4b4",9) for i in range(4))
 return circle(480,300,130,gold)
count=0
for slug,(en,ko,kind) in scenes.items():
 assert slug in slugs and slug not in photos
 digest=hashlib.sha256(slug.encode()).hexdigest();bg=["#102b43","#14253f","#21314c","#173744"][int(digest[:2],16)%4]
 scene=visual(kind)
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img"><title>{html.escape(ko)} 주제 일러스트</title><rect width="960" height="540" fill="{bg}"/><circle cx="810" cy="105" r="130" fill="#98c9d3" opacity=".1"/><circle cx="160" cy="445" r="175" fill="#f6d187" opacity=".07"/>{label(50,84,en,39)}{label(51,130,ko,24,"#afcbd4",500)}{scene}{rect(0,480,960,60,"#11263a")}{label(42,520,"NIPPONFERRY · TOPIC ILLUSTRATION",18,"#e8e9e3",500)}</svg>'''
 (root/"images"/"tokyo-topics"/(slug+".svg")).write_text(svg,encoding="utf-8")
 count+=1
assert count==16 and len(set(slugs)&photos)==4
report={"scope":"first 20 Tokyo hub cards","topic_specific_unique_illustrations_replaced":count,"existing_exact_photos_retained":4,"total":20,"slugs":slugs}
pathlib.Path("audit-reports/tokyo-first-20-specific-images.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="slugs"},ensure_ascii=False))
