from pathlib import Path
import json,re
root=Path("site/things-to-do")
rows=[]
for p in sorted(root.glob("*/index.html")):
  h=p.read_text("utf-8")
  for m in list(re.finditer(r'<p class="v\d+-image-credit"',h)):
    i=m.start()
    img=h.rfind("<img",0,i)
    mid=h[img:i]
    handler=("this.insertAdjacentHTML" in mid and "onerror=" in mid and len(mid)<1300)
    end=h.find("</div>')\">",i)
    rows.append({"slug":p.parent.name,"credit_position":i,"embedded_in_handler":handler,
                 "handler_end_found":end!=-1,"sample":mid[-260:],"end_sample":h[i:i+160]})
report={"checked_photo_credits":len(rows),"embedded":sum(x["embedded_in_handler"] for x in rows),
"broken":sum(x["embedded_in_handler"] and not x["handler_end_found"] for x in rows),
"cases":[x for x in rows if x["embedded_in_handler"]],"other_credits":len(rows)-sum(x["embedded_in_handler"] for x in rows)}
out=Path("docs/v42-image-audit/markup-diagnostics.json")
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="cases"},ensure_ascii=False),flush=True)
print("affected",[(x["slug"],x["handler_end_found"]) for x in report["cases"]],flush=True)
