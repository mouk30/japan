#!/usr/bin/env python3
"""Apply the 212 uniquely generated topic illustrations to their own articles.
Do not claim any topic illustration is a documentary photograph."""
import pathlib,re,html,json
root=pathlib.Path("site")
pages=sorted((root/"japan/tokyo").glob("*/index.html"))
assert len(pages)==220
photo_credits=json.loads((root/"tokyo-photo-credits.json").read_text(encoding="utf-8"))
real={p["slug"] for p in photo_credits}
added=0
already=0
for page in pages:
 slug=page.parent.name
 if slug in real:continue
 img="/images/tokyo-topics/"+slug+".svg"
 if not (root/img.lstrip("/")).is_file():raise RuntimeError("Missing image "+img)
 src=page.read_text(encoding="utf-8")
 if 'tokyo-article-photo-v1' in src:
  already+=1
  continue
 m=re.search("<main[^>]*>",src,re.I)
 if not m:raise RuntimeError("Missing main "+slug)
 figure='<figure class="tokyo-article-photo-v1"><img src="'+html.escape(img,quote=True)+'" alt="여행 주제 참고 일러스트. 실제 현장 사진 아님" loading="lazy" decoding="async"><figcaption>주제 참고 일러스트 · 실제 장소를 촬영한 사진이 아닙니다.</figcaption></figure>'
 src=src[:m.end()]+figure+src[m.end():]
 page.write_text(src,encoding="utf-8")
 added+=1
assert added+already==212,(added,already)
print(json.dumps({"total":220,"real_photo_articles":8,"unique_illustration_articles":212,"newly_updated":added,"already_updated":already}))
