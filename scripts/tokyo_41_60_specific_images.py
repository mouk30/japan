#!/usr/bin/env python3
"""41–60 Tokyo station guides: 20 uniquely labeled schematic visuals, not actual maps."""
import pathlib,re,json,html,hashlib,math
site=pathlib.Path("site")
hub=(site/"japan/tokyo/index.html").read_text(encoding="utf8")
slugs=[x.rstrip("/").split("/")[-1] for x in re.findall(r'<a\s+class="tky-card"[^>]*href="([^"]+)"',hub)[40:60]]
assert len(slugs)==20 and len(set(slugs))==20
details={
"shinjuku-exits":("SHINJUKU","동쪽 · 서쪽 · 남쪽 출구",["EAST","WEST","SOUTH"],"BUS TERMINAL"),
"shibuya-hachiko-miyamasuzaka":("SHIBUYA","하치코 · 미야마스자카 · 신남",["HACHIKO","MIYAMASUZAKA","NEW SOUTH"],"HACHIKO"),
"tokyo-keiyo-platform":("TOKYO STATION","게이요선 · 마루노우치 · 야에스",["KEIYO","MARUNOUCHI","YAESU"],"KEIYO LINE"),
"ikebukuro-east-west":("IKEBUKURO","동·서쪽 출구와 백화점",["EAST","WEST","SHOPPING"],"DEPARTMENT STORES"),
"ginza-three-lines":("GINZA","긴자선 · 마루노우치선 · 히비야선",["G LINE","M LINE","H LINE"],"G · M · H"),
"asakusa-operators":("ASAKUSA","4개 철도 · 센소지 접근",["GINZA","ASAKUSA","TOBU"],"SENSO-JI"),
"ueno-park-ameyoko":("UENO","공원 · 아메요코 · JR 개찰",["PARK","AMEYOKO","JR"],"UENO PARK"),
"otemachi-transfer-five":("OTEMACHI","5개 지하철 노선 환승",["M · T","C · Z","I LINE"],"5 METRO LINES"),
"kasumigaseki-government":("KASUMIGASEKI","관공서 · 히비야 출구",["GOVERNMENT","HIBIYA","METRO"],"OFFICE DISTRICT"),
"roppongi-museum-exits":("ROPPONGI","미드타운 · 롯폰기힐스",["MIDTOWN","HILLS","MUSEUM"],"ART DISTRICT"),
"omotesando-three-subways":("OMOTESANDO","G · C · Z · 하라주쿠",["G LINE","C LINE","Z LINE"],"HARAJUKU"),
"akasaka-nagatacho-connection":("AKASAKA / NAGATACHO","연결 환승 · 아카사카역 구분",["MITSUKE","NAGATACHO","TRANSFER"],"CONNECTED STATIONS"),
"kudanshita-budokan":("KUDANSHITA","무도관 · 치도리가후치",["BUDOKAN","MOAT","METRO"],"BUDOKAN"),
"kanda-jr-ginza-transfer":("KANDA","JR · 긴자선 · 맛집 거리",["JR","GINZA","FOOD"],"TRANSFER"),
"nippori-skyliner-jr":("NIPPORI","스카이라이너 · JR · 야나카",["SKYLINER","JR","YANAKA"],"AIRPORT TRAIN"),
"akihabara-station-gates":("AKIHABARA","전기가이 · 히비야선",["ELECTRIC TOWN","JR","HIBIYA"],"ELECTRIC TOWN"),
"tsukiji-two-stations":("TSUKIJI","쓰키지 · 쓰키지시조 구분",["TSUKIJI","SHIJO","MARKET"],"TWO STATIONS"),
"toyosu-shijomae-travel":("TOYOSU / SHIJOMAE","팀랩 · 시장 · 역 이동",["TOYOSU","SHIJOMAE","MARKET"],"TEAMLAB"),
"oshiage-skytree-access":("OSHIAGE","스카이트리역 · 전망대",["OSHIAGE","SKYTREE","ENTRY"],"SKYTREE"),
"shinagawa-keikyu-jr":("SHINAGAWA","게이큐 · JR · 신칸센",["KEIKYU","JR","SHINKANSEN"],"RAIL CONNECTION")
}
assert set(slugs)==set(details)
out=site/"images"/"tokyo-topics";out.mkdir(exist_ok=True)
for i,slug in enumerate(slugs):
 en,ko,labels,feature=details[slug]
 seed=int(hashlib.sha256(slug.encode()).hexdigest()[:10],16)
 tones=[("#132b44","#77c5bf","#f3c67c"),("#20324c","#a9b4ed","#e4b17f"),("#183745","#8cd0af","#e6c982"),("#243047","#8ebad7","#dfb4a0")]
 bg,accent,gold=tones[i%4]
 angle=(seed%80)-40
 paths=[]
 for k in range(3):
  x=235+k*245
  y=260+((seed>>(k*3))%70)
  d=f"M{120+k*18} {y+140} L{x} {y+25} L{x+110} {y+25} L{830-k*22} {y-78}"
  c=["#eaa57c","#7dcab7","#b4a6df"][k]
  paths.append(f'<path d="{d}" stroke="{c}" stroke-width="13" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
  paths.append(f'<circle cx="{x}" cy="{y+25}" r="19" fill="{bg}" stroke="{c}" stroke-width="9"/>')
  paths.append(f'<rect x="{145+k*225}" y="{375+(k%2)*26}" width="205" height="43" rx="10" fill="#f6f3e8"/><text x="{247+k*225}" y="{403+(k%2)*26}" font-size="{18 if len(labels[k])>12 else 22}" font-weight="700" fill="#19364c" text-anchor="middle" font-family="Arial,sans-serif">{html.escape(labels[k])}</text>')
 feature_text=f'<text x="490" y="209" font-family="Arial,sans-serif" text-anchor="middle" fill="{gold}" font-size="29" font-weight="700">{html.escape(feature)}</text>'
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img"><title>{html.escape(ko)}를 위한 주제 개념도 (실제 역 지도 아님)</title><rect width="960" height="540" fill="{bg}"/><circle cx="810" cy="90" r="130" fill="{accent}" opacity=".11"/><text x="45" y="68" fill="white" font-size="{31 if len(en)>18 else 39}" font-family="Arial,sans-serif" font-weight="700">{html.escape(en)}</text><text x="46" y="113" fill="{accent}" font-size="23" font-family="Arial,sans-serif">{html.escape(ko)}</text>{feature_text}{''.join(paths)}<rect x="0" y="484" width="960" height="56" fill="#091e32" opacity=".8"/><text x="40" y="519" font-size="17" fill="#e6e8e6" font-family="Arial,sans-serif">NIPPONFERRY · TOPIC ILLUSTRATION / NOT AN ACTUAL STATION MAP</text></svg>'''
 (out/(slug+".svg")).write_text(svg,encoding="utf8")
report={"range":"41-60","count":20,"unique_files":20,"type":"topic-specific schematics","warning":"Illustrations are not actual station maps, physical signs, or verified exit geometry.","slugs":slugs}
audit=pathlib.Path("audit-reports");audit.mkdir(exist_ok=True)
(audit/"tokyo-41-60-specific-images.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"range":report["range"],"count":20,"unique_files":20}))
