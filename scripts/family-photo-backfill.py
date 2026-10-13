#!/usr/bin/env python3
"""Carefully curated 15-guide, 45-card photo backfill.
Only exact Commons File names manually checked against subject and license.
Success writes local WebP + page links; failure leaves cards untouched. Outputs full inventory.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
import io, json, re, html, time
rows=json.loads("[[\"hakata\",\"후쿠오카시 과학관\",\"Fukuoka City Science Museum 20180801.jpg\",\"hakata-science-museum\",\"そらみみ\",\"BY-SA-4.0\"],[\"hakodate\",\"가네모리 붉은 벽돌 창고\",\"Hakodate Kanemori Red Brick Warehouse 20231223a.jpg\",\"hakodate-kanemori-warehouses\",\"掬茶\",\"BY-SA-4.0\"],[\"hakodate\",\"하코다테산 로프웨이\",\"Hakodate Ropeway 01.jpg\",\"hakodate-mount-ropeway\",\"yamauchi\",\"BY-2.0\"],[\"hirara-miyakojima\",\"미야코지마 해중공원\",\"Miyako miyakojima kaichukoen.jpg\",\"miyakojima-underwater-park\",\"Paipateroma\",\"BY-SA-4.0\"],[\"ishigaki\",\"이시가키 야이마무라\",\"Ishigaki yaimamura makishi house.jpg\",\"ishigaki-yaima-village\",\"Paipateroma\",\"BY-SA-4.0\"],[\"ishigaki\",\"이시가키 시가지 문화 산책\",\"Ishigaki eugrena mall.jpg\",\"ishigaki-euglena-mall\",\"Paipateroma\",\"BY-SA-4.0\"],[\"kagoshima\",\"이오월드 가고시마 수족관\",\"2025 Kagoshima Aquarium and Sakurajima.jpg\",\"kagoshima-ioworld-aquarium\",\"Taiwankengo\",\"BY-SA-4.0\"],[\"kagoshima\",\"센간엔 사쓰마 문화 체험\",\"Sengan-en 1.jpg\",\"kagoshima-senganen\",\"Christophe95\",\"BY-SA-4.0\"],[\"kagoshima\",\"사쿠라지마 페리\",\"Sakurajima ferry.jpg\",\"kagoshima-sakurajima-ferry\",\"NMaia\",\"BY-SA-4.0\"],[\"kanazawa\",\"화과자 만들기\",\"Wagashi 001.jpg\",\"kanazawa-wagashi-experience\",\"Toukou Sousui 淙穂鶫箜\",\"BY-2.0\"],[\"kanazawa\",\"가나자와 21세기 미술관\",\"21st Century Museum of Contemporary Art, Kanazawa003.jpg\",\"kanazawa-21st-museum\",\"金沢市\",\"BY-2.1-jp\"],[\"kobe\",\"고베 호빵맨 어린이 박물관\",\"130720 Kobe Anpanman Children's Museum & Mall Kobe Japan02s3.jpg\",\"kobe-anpanman-museum\",\"663highland\",\"BY-2.5\"],[\"nagasaki\",\"나가사키 펭귄 수족관\",\"Nagasaki penguin aquarium, Japan (4577433688).jpg\",\"nagasaki-penguin-aquarium\",\"pelican\",\"BY-SA-2.0\"],[\"nagasaki\",\"평화공원·원폭 자료\",\"20190202 Nagasaki Peace Park Statue of Peace-2.jpg\",\"nagasaki-peace-park\",\"Balon Greyjoy\",\"CC0-1.0\"],[\"naha\",\"오키나와현립 박물관·미술관\",\"Okinawa Prefectural Museum & Art Museum08ss4272.jpg\",\"naha-prefectural-museum\",\"663highland\",\"BY-2.5\"],[\"sasebo\",\"펄퀸 유람선\",\"Excursion Boat \\\"Pearl Queen\\\" of Kujukushima Pearl Sea Resort.JPG\",\"sasebo-pearl-queen\",\"そらみみ\",\"BY-SA-4.0\"],[\"shimizu\",\"드림플라자 수변\",\"231027 S-Pulse Dream Plaza Shizuoka Japan01s3.jpg\",\"shimizu-dream-plaza\",\"663highland\",\"BY-SA-4.0\"],[\"yokohama\",\"핫케이지마 시파라다이스\",\"八景島シーパラダイス アクアスタジアム - panoramio.jpg\",\"yokohama-hakkeijima-seaparadise\",\"Otota DANA\",\"BY-3.0\"]]")
rows += [
 ["hirara-miyakojima","우에노 독일문화촌","Ueno German Culture Village - J - 2020 March 27.jpg","miyakojima-ueno-german-village","Nesnad","BY-SA-4.0"],
 ["kanazawa","이시카와 관광물산관 금박 체험","Ishikawa kanko bussan.jpg","kanazawa-ishikawa-tourism-hall","Opqr","BY-SA-4.0"]
]
rows += [
 ["kobe","누노비키 허브원 로프웨이","Cable car in Kobe, Japan; May 2017.jpg","kobe-nunobiki-herb-ropeway","Mark Pegrum","BY-SA-2.0"],
 ["osaka","가이유칸","Kaiyūkan.jpg","osaka-kaiyukan-aquarium","Sakai Yayoi","CC0-1.0"],
 ["osaka","레고랜드 디스커버리센터 오사카","LEGOLAND Discovery Center Osaka.jpg","osaka-legoland-discovery","Dale Cruse","BY-2.0"],
 ["osaka","유니버설 스튜디오 재팬","USJ Entrance 2026.jpg","osaka-usj-entrance","Sakai Yayoi","CC0-1.0"],
 ["sasebo","하우스텐보스","200320 Huis Ten Bosch Sasebo Nagasaki pref Japan01s3.jpg","sasebo-huis-ten-bosch","663highland","BY-2.5"],
 ["yokohama","요코하마 코스모월드","Yokohama Cosmo World and Clock Ferris Wheel (4611157059).jpg","yokohama-cosmo-world","Jorge Láscar","BY-2.0"]
]
rows += [
 ["sasebo","구주쿠시마 수족관 우미키라라","Saikai Pearlsea Umikirara.jpg","sasebo-umikirara-aquarium","Atsasebo","BY-SA-3.0"],
 ["shimizu","시미즈 수산시장·스시 문화","KASHI NO ICHI in shimizu ward.jpg","shimizu-kashi-no-ichi-market","Halowand","BY-SA-4.0"]
]
site=Path("site"); dst=site/"images"/"venues"; dst.mkdir(parents=True,exist_ok=True)
reports=Path("audit-reports"); reports.mkdir(exist_ok=True)
licenses={"CC0-1.0":"https://creativecommons.org/publicdomain/zero/1.0/","BY-2.0":"https://creativecommons.org/licenses/by/2.0/","BY-2.5":"https://creativecommons.org/licenses/by/2.5/","BY-2.1-jp":"https://creativecommons.org/licenses/by/2.1/jp/","BY-3.0":"https://creativecommons.org/licenses/by/3.0/","BY-SA-3.0":"https://creativecommons.org/licenses/by-sa/3.0/","BY-SA-2.0":"https://creativecommons.org/licenses/by-sa/2.0/","BY-SA-4.0":"https://creativecommons.org/licenses/by-sa/4.0/"}
def get(item):
    port,venue,source,slug,artist,lic=item
    assert lic in licenses
    page=site/"things-to-do"/(port+"-cruise-family-guide")/"index.html"
    source_url="https://commons.wikimedia.org/wiki/File:"+quote(source.replace(" ","_"),safe="()_,")
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(source,safe="")+"?width=1200"
    for attempt in range(2):
        try:
            req=Request(url,headers={"User-Agent":"NipponFerryEditorial/1.0 (https://www.nipponferry.com/)","Accept":"image/*"})
            with urlopen(req,timeout=38) as stream:
                if not stream.headers.get("Content-Type","").startswith("image/"):
                    raise ValueError("Not an image HTTP response")
                payload=stream.read(16_000_000)
            pic=ImageOps.exif_transpose(Image.open(io.BytesIO(payload))).convert("RGB")
            pic.thumbnail((1200,850),Image.Resampling.LANCZOS)
            out=dst/(slug+".webp")
            pic.save(out,format="WEBP",quality=82,method=6)
            if out.stat().st_size<3500:raise ValueError("WebP unexpectedly small")
            return {"port":port,"venue":venue,"source":source_url,"artist":artist,"license":lic,"license_url":licenses[lic],"slug":slug,"bytes":out.stat().st_size,"state":"downloaded"}
        except Exception as error:
            if attempt==1:return {"port":port,"venue":venue,"slug":slug,"source":source_url,"state":"failed","error":str(error)[:260]}
            time.sleep(2)
with ThreadPoolExecutor(max_workers=5) as pool: output=list(pool.map(get,rows))
for item in output:
    if item["state"]!="downloaded":continue
    page=site/"things-to-do"/(item["port"]+"-cruise-family-guide")/"index.html"
    document=page.read_text(encoding="utf-8")
    root=document.find('id="ct-topic-dashboard"')
    if root<0:item["state"]="no_dashboard";continue
    needle="<h3>"+item["venue"]+"</h3>"
    at=document.find(needle,root)
    if at<0:item["state"]="no_matching_card";continue
    boundary=document.find("</article>",at)
    if boundary<0:item["state"]="card_incomplete";continue
    card=document[at:boundary]
    if "<img " in card or "<img\n" in card:
        if '/images/venues/' in card:
            item["state"]="already_had_local_photo"
            continue
        card=re.sub(r'<figure class="ct-photo"[^>]*>[\s\S]*?</figure>', '', card)
        if "<img " in card or "<img\n" in card:
            item["state"]="other_image_markup"
            continue
    url="/images/venues/"+item["slug"]+".webp"
    source=html.escape(item["source"],quote=True)
    artist=html.escape(item["artist"])
    credit=('<figure class="ct-photo nf-reviewed-photo"><img src="'+url+'" alt="'+html.escape(item["venue"])+' 현장 실사 사진" loading="lazy" decoding="async" width="900" height="600">'
      '<figcaption>사진: '+artist+' · '+html.escape("CC0 1.0" if item["license"]=="CC0-1.0" else "CC "+item["license"])+
      ' · <a href="'+source+'" target="_blank" rel="noopener noreferrer">원본 사진</a>'+
      ' · <a href="'+item["license_url"]+'" target="_blank" rel="noopener noreferrer">이용 허락</a>'+
      ' · WebP 크기·형식 변환</figcaption></figure>')
    card=card.replace(needle,needle+credit,1)
    document=document[:at]+card+document[boundary:]
    page.write_text(document,encoding="utf-8")
    item["state"]="published"
# Authoritative audit across 15 family TOP3 grids
summary=[]
for page in sorted((site/"things-to-do").glob("*-cruise-family-guide/index.html")):
    content=page.read_text(encoding="utf-8")
    pos=content.find('id="ct-topic-dashboard"')
    end=content.find('<div class="ct-panel"',pos)
    if pos<0:continue
    cards=re.findall(r'<article class="ct-card">([\s\S]*?)</article>',content[pos:end])
    for card in cards:
        title=re.search(r'<h3>([^<]+)</h3>',card)
        img=re.search(r'<img\b[^>]*\bsrc="([^"]+)"',card)
        src=img.group(1) if img else None
        path=site/src.lstrip("/") if src and src.startswith("/") else None
        summary.append({"page":page.parent.name,"venue":title.group(1) if title else "?","image_src":src,"status":"local_verified" if path and path.is_file() and path.stat().st_size>3000 else ("remote_needs_check" if src else "missing")})
counts={key:sum(row["status"]==key for row in summary) for key in ["local_verified","remote_needs_check","missing"]}
report={"total_pages":len(set(x["page"] for x in summary)),"total_cards":len(summary),"counts":counts,"backfill":output,"cards":summary}
(reports/"family-thumbnails.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"total_cards":len(summary),"counts":counts,"newly_published":sum(x["state"]=="published" for x in output),"failed":sum(x["state"]=="failed" for x in output)},ensure_ascii=False,indent=2))
