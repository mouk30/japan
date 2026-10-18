#!/usr/bin/env python3
"""Premium maritime V2 shared header, responsive navigation, contextual CTA.
Preserves existing articles, URLs, SEO head fields and JSON-LD verbatim."""
from pathlib import Path
import re,json,hashlib,collections,html,sys
root=Path("site")
items=[
 ("일본크루즈","/japan-cruise/","cruise"),
 ("연안페리","/booking/japan-cruise/","ferry"),
 ("크루즈 기항지","/things-to-do/cruise-ports/","ports"),
 ("일본 여행지","/japan/","destinations"),
 ("즐길거리","/things-to-do/","experiences"),
 ("동행 가이드","/things-to-do/travel-companions/","companions"),
 ("여행 정보","/practical/","practical"),
 ("항로·예약","/booking/japan-cruise/","reserve")
]
def current(path,key):
 if key=="ports":return path.startswith("things-to-do/cruise-ports/")
 if key=="companions":return path.startswith("things-to-do/travel-companions/")
 if key=="cruise":return path.startswith("japan-cruise/")
 if key=="ferry":return False
 if key=="destinations":return path.startswith("japan/") or path.startswith("explore/")
 if key=="experiences":return path.startswith("things-to-do/") and not ("/cruise-ports/" in path or "/travel-companions/" in path)
 if key=="practical":return path.startswith("practical/")
 return False
def links(path,desktop=False):
 result=[]
 for label,url,key in items:
  aria=' aria-current="page"' if current(path,key) else ''
  cls=' class="nf-nav-reserve"' if key=="reserve" else ''
  result.append('<a'+cls+aria+' href="'+url+'">'+label+'</a>')
 return "".join(result)
def header(path):
 return ('<header class="site-header" role="banner"><div class="wrap header-in">'
 '<a class="brand" href="/" aria-label="NIPPONFERRY 홈으로 이동">'
 '<span class="nf-brand-mark" aria-hidden="true">NF</span><span><strong>NIPPONFERRY</strong>'
 '<small>CRUISE · COASTAL FERRY</small></span></a>'
 '<nav class="desktop-nav" aria-label="주요 메뉴">'+links(path,True)+'</nav>'
 '<button class="menu-toggle" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="nf-mobile-menu">'
 '<span class="nf-toggle-symbol" aria-hidden="true">☰</span>메뉴</button>'
 '<nav class="mobile-menu" id="nf-mobile-menu" aria-label="모바일 주요 메뉴">'+links(path,False)+'</nav>'
 '</div></header>')
def seo(s):
 head=re.search(r"<head\b[^>]*>(.*?)</head>",s,re.I|re.S)
 if not head:return None
 h=head.group(1)
 return (
  tuple(re.findall(r"<title\b[^>]*>.*?</title>",h,re.I|re.S)),
  tuple(re.findall(r"<meta\b[^>]*name=['\"]description['\"][^>]*>",h,re.I|re.S)),
  tuple(re.findall(r"<link\b[^>]*rel=['\"]canonical['\"][^>]*>",h,re.I|re.S)),
  tuple(re.findall(r"<script\b[^>]*type=['\"]application/ld\+json['\"][^>]*>.*?</script>",h,re.I|re.S)),
  len(re.findall(r"<h1\b",s,re.I))
 )
def add_body_class(match):
 tag=match.group()
 c=re.search(r"\bclass\s*=\s*(['\"])(.*?)\1",tag,re.I|re.S)
 if c:
  if "nf-premium-v2" in c.group(2).split():return tag
  return tag[:c.start(2)]+c.group(2)+" nf-premium-v2"+tag[c.end(2):]
 return tag[:-1]+' class="nf-premium-v2">'
def add_cta(s,path):
 if "nf-v2-cta" in s:return s,False
 m=re.search(r'<footer\s+class=["\']site-footer["\']',s,re.I)
 if not m:return s,False
 if path.startswith("japan/tokyo/") and path != "japan/tokyo/index.html":
  text=("TRAVEL BEYOND TOKYO","도쿄 여행과 일본 바다 여행을 함께 준비하세요.",
        "기항지 관광과 연안페리 항로를 확인하고 이동 시간을 계획하세요.",
        "/things-to-do/cruise-ports/","크루즈 기항지 살펴보기")
 elif path.startswith("things-to-do/") and ("cruise-port" in path or "port-" in path or path=="things-to-do/cruise-ports/index.html"):
  text=("PORTS · TRANSFERS · RETURN TO SHIP","기항지에서의 시간을 더 정확하게 계획하세요.",
        "선사별 귀선 시각과 셔틀·환승 조건은 해당 항차 공식 안내로 확인하세요.",
        "/booking/japan-cruise/","항로·예약 가이드 보기")
 elif path in ["japan/index.html","things-to-do/index.html","things-to-do/travel-companions/index.html","japan/tokyo/index.html"]:
  text=("JAPAN CRUISE & COASTAL FERRY","여행지부터 바닷길까지 하나의 일정으로.",
        "크루즈 기항지와 연안페리 이동정보를 연결해 여행을 준비하세요.",
        "/booking/japan-cruise/","항로·예약 준비")
 else:return s,False
 eyebrow,title,desc,url,label=text
 card=('<section class="nf-v2-cta-wrap" aria-label="함께 확인할 여행 준비 정보"><div class="nf-v2-cta">'
       '<div><span class="nf-v2-eyebrow">'+eyebrow+'</span><strong>'+title+'</strong><p>'+desc+'</p></div>'
       '<a href="'+url+'">'+label+' ↗</a></div></section>')
 return s[:m.start()]+card+s[m.start():],True
stats=collections.Counter()
detail=[]
for f in root.rglob("*.html"):
 path=f.relative_to(root).as_posix()
 if path in ("404.html",) or "/photo-review/" in path:continue
 s=f.read_text(encoding="utf8")
 if "nf-premium-v2.css" in s: stats["previously_migrated"]+=1;continue
 if not re.search(r'<header\s+class=["\']site-header["\']',s,re.I):stats["no_shared_header"]+=1;continue
 if not re.search(r"</head>",s,re.I) or not re.search(r"<body\b",s,re.I):stats["not_html_shell"]+=1;continue
 old=seo(s)
 if old is None:raise ValueError(("no head",path))
 modified,n=re.subn(r'<header\s+class=["\']site-header["\'][^>]*>.*?</header>',lambda _:header(path),s,count=1,flags=re.I|re.S)
 if n!=1:raise AssertionError(("header replace",path,n))
 modified=re.sub(r"<body\b[^>]*>",add_body_class,modified,count=1,flags=re.I|re.S)
 modified=re.sub(r"</head>",'<link rel="stylesheet" href="/nf-premium-v2.css?v=20261018"></head>',modified,count=1,flags=re.I)
 modified=re.sub(r"</body>",'<script src="/nf-premium-v2.js" defer></script></body>',modified,count=1,flags=re.I)
 modified,cta=add_cta(modified,path)
 if seo(modified)!=old:raise AssertionError(("SEO changed",path))
 if cta:stats["cta_added"]+=1
 if modified!=s:
  f.write_text(modified,encoding="utf8")
  stats["pages_changed"]+=1
  if len(detail)<20:detail.append(path)
report={"stats":dict(stats),"sample_paths":detail,"rules":["Canonical, title, meta description, JSON-LD and h1 counts preserved byte-for-byte.","Original page body outside nav and optional contextual CTA retained.","No new articles or slugs. Header navigation and branding standardized.","Mobile behavior is backed by original page menu listeners and accessibility helper."],"verify":"Browser QA on high-traffic hub and article templates required."}
out=Path("audit-reports/nf-premium-v2")
out.mkdir(parents=True,exist_ok=True)
(out/"migration-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
assert stats["pages_changed"]>500,stats
