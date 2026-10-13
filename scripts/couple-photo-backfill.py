#!/usr/bin/env python3
"""V10 couple guide 15x3 thumbnail audit + safely licensed WebP backfill.

Only exact city/venue photography or explicitly disclosed same-site exterior.
One failure never inserts a wrong-region replacement. Report is source of truth.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import quote,unquote
from PIL import Image,ImageOps
from concurrent.futures import ThreadPoolExecutor
import re, json, io, html, time
site=Path("site"); home=site/"things-to-do"; venue_dir=site/"images/venues"; venue_dir.mkdir(parents=True,exist_ok=True)
report_dir=Path("audit-reports");report_dir.mkdir(parents=True,exist_ok=True)
reuse=json.loads("[[\"aomori\",\"네부타 와랏세\",\"aomori-nebuta-warasse.webp\",\"\"],[\"aomori\",\"A-FACTORY\",\"aomori-a-factory.webp\",\"\"],[\"aomori\",\"아오모리 베이 에어리어\",\"aomori-a-factory.webp\",\"베이 에어리어의 A-FACTORY 건물 사진이며 해안 전체 전경은 아닙니다.\"],[\"beppu\",\"간나와 온천마을\",\"beppu-umi-jigoku.webp\",\"간나와 지역의 우미지옥 사진으로 마을 전체 풍경은 아닙니다.\"],[\"hakata\",\"하카타 리버레인 일대\",\"hakata-anpanman-host-building.webp\",\"하카타 리바레인 건물 출입구로 주변 일대 전경은 아닙니다.\"],[\"hakodate\",\"가네모리 붉은 벽돌 창고\",\"hakodate-kanemori-warehouses.webp\",\"\"],[\"hakodate\",\"하코다테산 로프웨이\",\"hakodate-mount-ropeway.webp\",\"\"],[\"hirara-miyakojima\",\"시기라 스파·온천\",\"miyakojima-shigira-allamanda.webp\",\"시기라 리조트의 건물 외관으로 스파·온천 내부 사진이 아닙니다.\"],[\"ishigaki\",\"가비라만\",\"ishigaki-kabira-bay.webp\",\"\"],[\"ishigaki\",\"가비라만 글라스보트\",\"ishigaki-kabira-bay.webp\",\"가비라만 해안·보트 풍경으로 실제 탑승 장면 사진은 아닙니다.\"],[\"ishigaki\",\"야이마무라\",\"ishigaki-yaima-village.webp\",\"\"],[\"kagoshima\",\"센간엔 정원\",\"kagoshima-senganen.webp\",\"\"],[\"kanazawa\",\"금박 장식 체험\",\"kanazawa-ishikawa-tourism-hall.webp\",\"금박 체험 장소가 있는 관광물산관 외관으로 체험 중인 모습은 아닙니다.\"],[\"kobe\",\"누노비키 허브정원\",\"kobe-nunobiki-herb-ropeway.webp\",\"누노비키 허브원으로 가는 로프웨이 사진으로 정원 내부 사진이 아닙니다.\"],[\"nagasaki\",\"글로버정원\",\"nagasaki-glover-garden.webp\",\"\"],[\"nagasaki\",\"평화공원\",\"nagasaki-peace-park.webp\",\"\"],[\"naha\",\"슈리성 공원\",\"naha-shureimon.webp\",\"슈리성 공원 수례문 사진으로 복원 중인 정전 내부 사진은 아닙니다.\"],[\"naha\",\"DMM 가리유시 수족관\",\"naha-dmm-kariyushi-aquarium.webp\",\"\"],[\"osaka\",\"가이유칸\",\"osaka-kaiyukan-aquarium.webp\",\"\"],[\"sasebo\",\"구주쿠시마 펄퀸\",\"sasebo-pearl-queen.webp\",\"\"],[\"sasebo\",\"하우스텐보스\",\"sasebo-huis-ten-bosch.webp\",\"\"],[\"shimizu\",\"드림플라자 수변\",\"shimizu-dream-plaza.webp\",\"\"],[\"yokohama\",\"코스모월드 대관람차\",\"yokohama-cosmo-world.webp\",\"\"]]")
new=json.loads("[[\"beppu\",\"당일 이용 온천\",\"Takegawara.jpg\",\"beppu-takegawara-onsen\",\"Marc Heiden\",\"CC BY-SA 3.0\",\"https://creativecommons.org/licenses/by-sa/3.0/\",\"다케가와라 온천 외관의 사례이며 벳푸 전체 당일 이용 온천을 대표하지 않습니다.\"],[\"hakata\",\"오호리공원\",\"Ōhori Park The view NNE from Ukimidō Ōhorikōen Chūō-ku Fukuoka 20260609 154008.jpg\",\"fukuoka-ohori-park\",\"Hirho\",\"CC BY 4.0\",\"https://creativecommons.org/licenses/by/4.0/\",\"\"],[\"hakata\",\"후쿠오카 타워\",\"Fukuoka Tower.JPG\",\"fukuoka-tower\",\"Vickerman625\",\"Public domain\",\"https://commons.wikimedia.org/wiki/File:Fukuoka_Tower.JPG\",\"\"],[\"hakodate\",\"모토마치 언덕\",\"Chachanobori slope Motomachi Hakodate Hokkaido Japan01s3.jpg\",\"hakodate-motomachi-slope\",\"663highland\",\"CC BY-SA 3.0\",\"https://creativecommons.org/licenses/by-sa/3.0/\",\"\"],[\"hirara-miyakojima\",\"요나하 마에하마 해변\",\"202408 Yonaha Maehama Beach around 11 o'clock in summer (JK-DSC0765).jpg\",\"miyakojima-yonaha-maehama\",\"Junyu-K\",\"CC BY-SA 4.0\",\"https://creativecommons.org/licenses/by-sa/4.0/\",\"실제 미야코지마 요나하마에하마 해변 사진입니다.\"],[\"kagoshima\",\"시로야마 전망\",\"Kagoshima view from Shiroyama - Dec 31, 2009.jpg\",\"kagoshima-shiroyama-view\",\"Masahiko OHKUBO\",\"CC BY-SA 2.0\",\"https://creativecommons.org/licenses/by-sa/2.0/\",\"\"],[\"kagoshima\",\"덴몬칸\",\"Tenmonkan G3 Kagoshima Japan.jpg\",\"kagoshima-tenmonkan\",\"Sanjo\",\"CC BY-SA 3.0\",\"https://creativecommons.org/licenses/by-sa/3.0/\",\"\"],[\"kanazawa\",\"히가시차야가이\",\"Higashi Chaya district, Kanazawa (3810704024).jpg\",\"kanazawa-higashi-chaya\",\"Andrea Schaffer\",\"CC BY 2.0\",\"https://creativecommons.org/licenses/by/2.0/\",\"\"],[\"kobe\",\"메리켄파크·하버랜드\",\"Kobe-meriken-park.JPG\",\"kobe-meriken-park-night\",\"Tomomarusan\",\"CC BY 2.5\",\"https://creativecommons.org/licenses/by/2.5/\",\"\"],[\"kobe\",\"기타노 이진칸\",\"Weathercock House Kobe Kitano Ijinkan 風見鶏の館（旧トーマス住宅）.jpg\",\"kobe-kitano-weathercock\",\"Wikimedia Commons contributor\",\"CC BY-SA 3.0\",\"https://creativecommons.org/licenses/by-sa/3.0/\",\"기타노 이진칸 가운데 풍향계의 집 외관 사진입니다.\"],[\"nagasaki\",\"이나사야마 로프웨이\",\"Mt.Inasa Ropeway.jpg\",\"nagasaki-inasa-ropeway\",\"ブルーノ・プラス\",\"CC BY-SA 4.0\",\"https://creativecommons.org/licenses/by-sa/4.0/\",\"\"],[\"naha\",\"국제거리\",\"Kokusai-dori05ss4272.jpg\",\"naha-kokusai-street\",\"663highland\",\"CC BY 2.5\",\"https://creativecommons.org/licenses/by/2.5/\",\"\"],[\"osaka\",\"덴포잔 대관람차\",\"Tempozan Ferris Wheel in Osaka at Dusk.jpg\",\"osaka-tempozan-wheel\",\"TimBray\",\"CC BY-SA 4.0\",\"https://creativecommons.org/licenses/by-sa/4.0/\",\"\"],[\"osaka\",\"도톤보리\",\"Dotonbori, Osaka - DSC05726.JPG\",\"osaka-dotonbori\",\"Daderot\",\"CC0 1.0\",\"https://creativecommons.org/publicdomain/zero/1.0/\",\"\"],[\"shimizu\",\"미호노마쓰바라\",\"Miho no Matsubara 01.jpg\",\"shimizu-miho-matsubara\",\"Σ64\",\"CC BY 3.0\",\"https://creativecommons.org/licenses/by/3.0/\",\"\"],[\"shimizu\",\"니혼다이라 로프웨이\",\"Nihondaira Ropeway.jpg\",\"shimizu-nihondaira-ropeway\",\"Wikimedia Commons contributor\",\"CC BY-SA 3.0\",\"https://creativecommons.org/licenses/by-sa/3.0/\",\"\"],[\"yokohama\",\"요코하마 에어캐빈\",\"YOKOHAMA AIR CABIN - Carrier.jpg\",\"yokohama-air-cabin\",\"NEO-NEED\",\"CC BY-SA 4.0\",\"https://creativecommons.org/licenses/by-sa/4.0/\",\"\"]]")
reuse.append(json.loads("[\"hirara-miyakojima\",\"시기라 오션스카이 리프트\",\"miyakojima-shigira-allamanda.webp\",\"리프트 실사 사진은 아직 확보하지 못했습니다. 시기라 리조트 건물 외관 참고 사진이며 리프트 탑승 장면이 아닙니다.\"]"))
new.append(json.loads("[\"yokohama\",\"붉은벽돌 창고·수변\",\"Yokohama Red Brick Warehouse.jpg\",\"yokohama-redbrick-waterfront\",\"Fred Cherrygarden\",\"CC BY-SA 4.0\",\"https://creativecommons.org/licenses/by-sa/4.0/\",\"\"]"))
status=[]
def sections(content):
    a=content.find('id="ct-topic-dashboard"')
    b=content.find('<div class="ct-panel"',a)
    return a,b if b>a else len(content)
def figure_for_local(asset):
    for p in home.glob("*-cruise-family-guide/index.html"):
        s=p.read_text(encoding="utf8")
        for fig in re.findall(r'<figure\b[^>]*>[\s\S]*?</figure>',s):
            if '/images/venues/'+asset in fig:
                return fig,p
    return None,None
def change_card(page,venue,fig,replace_remote=False):
    s=page.read_text(encoding="utf8")
    a,b=sections(s)
    if a<0:return "dashboard_missing"
    mark='<h3>'+venue+'</h3>'
    i=s.find(mark,a,b)
    if i<0:return "title_missing"
    stop=s.find('</article>',i)
    if stop<0:return "card_incomplete"
    old=s[i:stop]
    if re.search(r'<img\b[^>]*src="/images/venues/',old):return "already_local"
    if re.search(r'<img\b',old) and not replace_remote:return "already_has_remote"
    if replace_remote:
        old=re.sub(r'<figure\b[^>]*>[\s\S]*?</figure>','',old)
    newcard=old.replace(mark,mark+fig,1)
    page.write_text(s[:i]+newcard+s[stop:],encoding="utf8")
    return "linked"
def from_local(item):
    port,title,asset,note=item
    path=venue_dir/asset
    if not path.exists():return {"port":port,"title":title,"result":"missing_local_file"}
    fig,_=figure_for_local(asset)
    if not fig:return {"port":port,"title":title,"result":"missing_attribution"}
    # Always retain the original creator/license from the family guide.
    fig=re.sub(r'alt="[^"]*"', 'alt="'+html.escape(title,quote=True)+' 실제 장소 참고 사진"',fig,count=1)
    if note:
        fig=fig.replace('<figcaption>','<figcaption>'+html.escape(note)+' ',1)
    res=change_card(home/(port+'-cruise-couple-guide')/'index.html',title,fig,replace_remote=True)
    return {"port":port,"title":title,"result":res,"local_src":"/images/venues/"+asset,"same_area_note":note}
for entry in reuse:status.append(from_local(entry))
def new_photo(item):
    port,title,filename,slug,author,lic,licurl,note=item
    file=venue_dir/(slug+'.webp')
    if not file.exists():
        url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1150"
        problem=""
        for attempt in range(2):
            try:
                with urlopen(Request(url,headers={"User-Agent":"NipponFerryCoupleGuideEditorial/1.0 (https://www.nipponferry.com/)","Accept":"image/*"}),timeout=35) as r:
                    if not r.headers.get("Content-Type","").startswith("image/"):raise ValueError("non-image response")
                    data=r.read(16_000_000)
                im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
                im.thumbnail((1150,850),Image.Resampling.LANCZOS)
                im.save(file,"WEBP",quality=82,method=6)
                if file.stat().st_size<3200:raise ValueError("WebP too small")
                problem=""
                break
            except Exception as e:
                problem=str(e)
                if attempt==0:time.sleep(2)
        if problem:return {"port":port,"title":title,"result":"download_failed","error":problem[:240]}
    source="https://commons.wikimedia.org/wiki/File:"+quote(filename.replace(" ","_"),safe="()_,")
    fig=('<figure class="ct-photo nf-couple-webp"><img src="/images/venues/'+slug+'.webp" width="900" height="600" loading="lazy" decoding="async" alt="'+html.escape(title)+' 실제 장소 사진">'
       '<figcaption>'+html.escape(note+' ' if note else '')+'사진: '+html.escape(author)+' · '+html.escape(lic)+' · <a href="'+source+'" rel="noopener noreferrer" target="_blank">사진 원본</a> · <a href="'+html.escape(licurl)+'" rel="noopener noreferrer" target="_blank">라이선스</a> · WebP 변환 및 크기 조정</figcaption></figure>')
    res=change_card(home/(port+'-cruise-couple-guide')/'index.html',title,fig,replace_remote=True)
    return {"port":port,"title":title,"result":res,"local_src":"/images/venues/"+slug+".webp"}
# image fetch parallel; writes to different page for some items so serial application after downloads
# Apply new photos sequentially: multiple cards share HTML files.
ready=[new_photo(item) for item in new]
status.extend(ready)
# Convert existing remote images only when verified Commons File link and source figcaption survives.
for page in sorted(home.glob("*-cruise-couple-guide/index.html")):
    doc=page.read_text(encoding="utf8")
    st,en=sections(doc)
    chunk=doc[st:en]
    cards=re.findall(r'<article class="ct-card">([\s\S]*?)</article>',chunk)
    for card in cards:
        if '/images/venues/' in card or '<img ' not in card:continue
        title_match=re.search(r'<h3>([^<]+)</h3>',card)
        if not title_match:continue
        title=title_match.group(1)
        figures=re.findall(r'<figure\b[^>]*>[\s\S]*?</figure>',card)
        if not figures:continue
        fig=figures[0]
        source=re.search(r'href="https://commons.wikimedia.org/wiki/File:([^"]+)"',fig)
        if not source or '<figcaption>' not in fig:continue
        filename=unquote(source.group(1)).replace('_',' ')
        slug=re.sub('[^a-z0-9-]','-',page.parent.name.replace('-cruise-couple-guide','')+'-'+str(abs(sum(ord(t) for t in title))) )+'-remote'
        file=venue_dir/(slug+'.webp')
        try:
            if not file.exists():
                url='https://commons.wikimedia.org/wiki/Special:FilePath/'+quote(filename,safe='')+'?width=1100'
                with urlopen(Request(url,headers={"User-Agent":"NipponFerryEditorial/1.0 (https://www.nipponferry.com/)"}),timeout=35) as r:data=r.read(16_000_000)
                im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
                im.thumbnail((1100,850),Image.Resampling.LANCZOS);im.save(file,'WEBP',quality=81)
                if file.stat().st_size<3200:raise ValueError("too small")
            old_src=re.search(r'<img[^>]*\bsrc="([^"]+)"',fig)
            if not old_src:continue
            newfig=fig.replace(old_src.group(1),"/images/venues/"+slug+".webp",1).replace('</figcaption>',' · WebP 형식 변환</figcaption>',1)
            doc=doc.replace(fig,newfig,1);page.write_text(doc,encoding='utf8')
            status.append({"port":page.parent.name,"title":title,"result":"remote_to_local","local_src":"/images/venues/"+slug+".webp"})
        except Exception as e:status.append({"port":page.parent.name,"title":title,"result":"remote_failed","error":str(e)[:120]})
# Final 45-card audit: local path must exist and be nontrivial; attribution must exist.
cards_out=[]
for page in sorted(home.glob("*-cruise-couple-guide/index.html")):
    doc=page.read_text(encoding="utf8")
    st,en=sections(doc)
    for card in re.findall(r'<article class="ct-card">([\s\S]*?)</article>',doc[st:en]):
        title=(re.search(r'<h3>([^<]*)</h3>',card) or [None,"?"])[1]
        image=(re.search(r'<img\b[^>]*\bsrc="([^"]*)"',card) or [None,None])[1]
        local=venue_dir/(image.split('/')[-1]) if image and image.startswith('/images/venues/') else None
        state=("local_verified" if local and local.is_file() and local.stat().st_size>3000 and "<figcaption>" in card
               else "remote_needs_review" if image else "missing")
        cards_out.append({"page":page.parent.name,"venue":title,"image_src":image,"status":state})
counts={k:sum(x["status"]==k for x in cards_out) for k in ["local_verified","remote_needs_review","missing"]}
output={"total_pages":len(set(x["page"] for x in cards_out)),"total_cards":len(cards_out),"counts":counts,"changes":status,"cards":cards_out}
(report_dir/"couple-thumbnails.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"pages":output["total_pages"],"cards":len(cards_out),"counts":counts,"linked":sum(x["result"]=="linked" for x in status),"failed":sum(x["result"] in ("download_failed","remote_failed") for x in status)},ensure_ascii=False,indent=2))
