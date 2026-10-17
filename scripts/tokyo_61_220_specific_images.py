#!/usr/bin/env python3
"""Topic-specific, nonduplicate illustrated covers for Tokyo hub cards 61–220.
These are editorial artwork, not photos, official maps or proprietary Disney art."""
import pathlib,re,html,hashlib,json,random,math
root=pathlib.Path("site")
hub=(root/"japan/tokyo/index.html").read_text(encoding="utf-8")
cards=list(re.finditer(r'<a\s+class="tky-card"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>',hub))
assert len(cards)==220, len(cards)
credits=json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf-8"))
verified={x["slug"] for x in credits}
out=root/"images"/"tokyo-topics";out.mkdir(exist_ok=True)
def esc(s):return html.escape(s,quote=False)
def cat(slug):
 if any(x in slug for x in ["line-stations","metro-","subway-","pasmo","suica","monorail","skyliner","nex","yurikamome","elevator","transport"]):return "rail"
 if slug.startswith("disney") or slug.startswith("disneyland") or slug.startswith("disneysea"):
  if any(x in slug for x in ["hotel","vacation","happy-entry"]):return "hotel"
  if any(x in slug for x in ["ticket","pass","dpa","request","order","seating","booking","package","passport","share"]):return "ticket"
  return "themepark"
 if any(x in slug for x in ["isetan","daimaru","tobu-","takashimaya","mitsukoshi","ginza-six","parco","donki","drugstore","muji","loft","hands","electronics","shopping","cosmetic","taxfree","luggage"]):return "retail"
 if any(x in slug for x in ["ramen","tsukemen","soba","udon","tempura","unagi","yakiniku","izakaya","sushi","bento","kissaten","matcha","wagashi","melonpan","parfait","food","allergy","monjya","sweets","coffee","dessert"]):return "food"
 if any(x in slug for x in ["garden","park","river","cherry","autumn","tram","beach","sunset","nature"]):return "nature"
 if any(x in slug for x in ["museum","art-","sumo","kabuki","teamlab","exhibition"]):return "culture"
 if "cruise" in slug:return "cruise"
 if any(x in slug for x in ["rainy","summer","winter","night","couple"]):return "weather"
 if any(x in slug for x in ["stroller","parents","toddler","family","teens","budget","luxury","firsttime","first-time","arrival","lastday","narita-last"]):return "planning"
 return "district"
def svg_scene(c,accent,light,seed,slug):
 # Clear, original symbolic graphics aligned to editorial subject; not an asserted physical likeness.
 if c=="rail":
  n=seed%5+3
  lines=''.join(f'<path d="M{220+i*95} 237 Q{260+i*55} {230+(i%3)*52} {310+i*77} 408" stroke="{[accent,light,"#e9ad7c","#a9bee8"][i%4]}" stroke-width="13" fill="none" stroke-linecap="round"/><circle cx="{220+i*95}" cy="237" r="15" fill="#f4f0e7"/>' for i in range(n))
  return lines+'<rect x="300" y="318" width="365" height="114" rx="24" fill="#eff3f0"/><rect x="336" y="337" width="286" height="53" rx="9" fill="#46718d"/><path d="M320 412H645" stroke="'+accent+'" stroke-width="14"/><circle cx="380" cy="430" r="14" fill="#172b41"/><circle cx="587" cy="430" r="14" fill="#172b41"/>'
 if c=="ticket":
  return ''.join(f'<g transform="translate({265+i*160} {223+i*18}) rotate({-8+i*8} 80 100)"><rect width="155" height="197" rx="16" fill="{[accent,light,"#f3be83"][i]}"/><circle cx="0" cy="102" r="15" fill="#172c42"/><circle cx="155" cy="102" r="15" fill="#172c42"/><path d="M25 104H130" stroke="#284b57" stroke-width="4" stroke-dasharray="9 6"/><circle cx="79" cy="63" r="27" fill="#fff4d9" opacity=".8"/><rect x="28" y="142" width="102" height="12" rx="6" fill="#284b57" opacity=".35"/></g>' for i in range(3))
 if c=="themepark":
  return '<circle cx="481" cy="309" r="143" stroke="'+accent+'" stroke-width="14" fill="none"/>'+''.join(f'<path d="M481 309L{481+141*math.cos(i*math.pi/5):.1f} {309+141*math.sin(i*math.pi/5):.1f}" stroke="{light}" stroke-width="7"/><circle cx="{481+141*math.cos(i*math.pi/5):.1f}" cy="{309+141*math.sin(i*math.pi/5):.1f}" r="19" fill="#f4e9d8"/>' for i in range(10))+'<circle cx="481" cy="309" r="29" fill="'+accent+'"/><path d="M330 457H632" stroke="#eedab8" stroke-width="21"/>'
 if c=="hotel":
  return '<rect x="322" y="182" width="323" height="270" rx="15" fill="#ece8dd"/>'+''.join(f'<rect x="{350+i*72}" y="{218+j*62}" width="45" height="44" rx="5" fill="{accent}" opacity="{.65+i*.06:.2f}"/>' for i in range(4) for j in range(3))+'<path d="M468 452V388h44v64" fill="#244b60"/><path d="M304 192L481 112L661 192" fill="'+light+'"/>'
 if c=="retail":
  return '<rect x="290" y="211" width="380" height="247" rx="19" fill="#efe9df"/><path d="M282 231H679" stroke="'+accent+'" stroke-width="36"/><path d="M378 211Q378 133 481 133Q583 133 583 211" stroke="'+light+'" stroke-width="17" fill="none"/>'+''.join(f'<rect x="{327+i*105}" y="285" width="82" height="115" rx="8" fill="{[accent,"#8daac9","#e8b57c"][i]}"/>' for i in range(3))
 if c=="food":
  return '<ellipse cx="480" cy="365" rx="225" ry="91" fill="#f3e9dc"/><ellipse cx="480" cy="355" rx="180" ry="63" fill="#b58254"/>'+''.join(f'<ellipse cx="{363+i*48}" cy="{342+(i%2)*14}" rx="30" ry="16" fill="{[light,accent,"#f4cf8d"][i%3]}" transform="rotate({i*14-27} {363+i*48} 342)"/>' for i in range(6))+'<path d="M340 198L654 284 M350 165L671 251" stroke="#eed2a6" stroke-width="10" stroke-linecap="round"/>'
 if c=="nature":
  return '<path d="M80 448Q250 279 411 448M391 448Q570 215 879 448" fill="'+accent+'" opacity=".54"/><path d="M493 440V264" stroke="#e7bf92" stroke-width="26"/>'+''.join(f'<circle cx="{493+math.cos(i*1.2)*70:.1f}" cy="{224+math.sin(i*1.2)*64:.1f}" r="63" fill="{[accent,light,"#91bb9d"][i%3]}"/>' for i in range(5))+'<path d="M0 460H960" stroke="#d4bd86" stroke-width="8"/>'
 if c=="culture":
  return '<path d="M264 258L480 140L696 258Z" fill="'+accent+'"/><rect x="277" y="277" width="406" height="164" rx="4" fill="#e9e8e0"/>'+''.join(f'<rect x="{320+i*80}" y="294" width="27" height="140" fill="#7b98a6"/>' for i in range(5))+'<rect x="265" y="428" width="430" height="17" fill="'+light+'"/>'
 if c=="cruise":
  return '<path d="M120 395Q210 365 300 395T480 395T660 395T840 395V485H120" fill="'+accent+'" opacity=".8"/><path d="M240 315H720L658 392H297Z" fill="#e9ebe6"/><rect x="360" y="240" width="237" height="75" rx="5" fill="#d3e7eb"/><rect x="466" y="180" width="43" height="61" fill="'+light+'"/>'+''.join(f'<rect x="{388+i*59}" y="260" width="36" height="30" rx="3" fill="#54859b"/>' for i in range(3))
 if c=="weather":
  return '<circle cx="677" cy="191" r="81" fill="'+light+'" opacity=".88"/>'+''.join(f'<rect x="{235+i*98}" y="{310-(i%3)*49}" width="76" height="{180+(i%3)*49}" rx="6" fill="{accent}" opacity=".82"/>' for i in range(6))+'<path d="M160 440H820" stroke="#e7e9de" stroke-width="8"/>'
 if c=="planning":
  return '<rect x="286" y="215" width="393" height="227" rx="24" fill="#f5efe6"/><path d="M286 274H679" stroke="'+accent+'" stroke-width="54"/>'+''.join(f'<circle cx="{337+i*93}" cy="{323+(i%2)*55}" r="26" fill="{[accent,light,"#ebb98e"][i%3]}"/>' for i in range(4))+'<path d="M351 405H618" stroke="#8caaa9" stroke-width="11" stroke-dasharray="26 12"/>'
 return '<path d="M210 454V285H336V454M345 454V189H480V454M490 454V245H642V454M654 454V305H761V454" fill="'+accent+'" opacity=".8"/><circle cx="742" cy="158" r="62" fill="'+light+'" opacity=".86"/>'+''.join(f'<rect x="{367+i*29}" y="{232+j*42}" width="11" height="21" rx="2" fill="#eed9ad"/>' for i in range(3) for j in range(4))
count=0;kept=[];used=[]
palette=[("#112f4b","#70bfd0","#e8c38e"),("#25314d","#9eb6e8","#f2c488"),("#163d47","#85c8aa","#e9ba8f"),("#352d48","#bea1d4","#eabf7c"),("#142d44","#9bbaad","#e7a991"),("#293246","#b4c8da","#eaba86"),("#2d344f","#8ea9d3","#dbc3a0")]
for position,match in enumerate(cards[60:220],61):
 slug=match.group(1).strip("/").split("/")[-1]
 heading=re.search(r"<h3[^>]*>(.*?)</h3>",match.group(2),re.S)
 assert heading,slug
 title=html.unescape(re.sub(r"<[^>]*>","",heading.group(1))).strip()
 if slug in verified:
  kept.append(slug);continue
 kind=cat(slug);digest=int(hashlib.sha256(slug.encode()).hexdigest()[:10],16)
 bg,accent,light=palette[digest%len(palette)]
 parts=[];current=""
 for ch in title:
  current+=ch
  if len(current)>=20 and (ch in (" ","·","/") or len(current)>=24):
   parts.append(current.strip());current=""
 if current:parts.append(current.strip())
 if len(parts)>2:parts=[parts[0],(" ".join(parts[1:]))[:32]]
 texts="".join(f'<text x="46" y="{107+j*40}" fill="{light if j else "#ffffff"}" font-family="Noto Sans CJK KR,Malgun Gothic,sans-serif" font-size="{25 if len(p)>27 else 30}" font-weight="700">{esc(p)}</text>' for j,p in enumerate(parts))
 art=svg_scene(kind,accent,light,digest,slug)
 # Stable subject-specific icon+title, different illustration every post.
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img"><title>{esc(title)} — 편집용 주제 일러스트, 실제 현장 사진 아님</title><rect width="960" height="540" fill="{bg}"/><circle cx="{680+digest%145}" cy="{104+digest%65}" r="{90+digest%55}" fill="{accent}" opacity=".10"/><path d="M26 27H934" stroke="{accent}" stroke-width="5"/>{texts}{art}<rect x="0" y="480" width="960" height="60" fill="#091f34" opacity=".88"/><text x="40" y="516" font-family="Arial,sans-serif" fill="#f5f5ee" font-size="19">TOKYO GUIDE  /  {kind.upper()}  /  CONCEPT ILLUSTRATION</text><text x="922" y="516" text-anchor="end" font-size="20" fill="{light}" font-family="Arial,sans-serif">{position:03d}</text></svg>'''
 (out/(slug+".svg")).write_text(svg,encoding="utf-8")
 count+=1;used.append({"index":position,"slug":slug,"title":title,"category":kind,"image":"/images/tokyo-topics/"+slug+".svg"})
assert count+len(kept)==160
report={"scope":"Tokyo cards 61–220","total_positions":160,"new_topic_specific_images":count,"previously_licensed_photos_preserved":len(kept),"preserved_photo_slugs":kept,"source_kind":"original SVG concept illustration; not actual site photographs or operational maps","entries":used}
audit=pathlib.Path("audit-reports");audit.mkdir(exist_ok=True)
(audit/"tokyo-61-220-specific-images.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ("entries","preserved_photo_slugs")},ensure_ascii=False))
