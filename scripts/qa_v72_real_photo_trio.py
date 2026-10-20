#!/usr/bin/env python3
"""V72 exact public photo rollout verification for three existing travel guides.
Does NOT verify real-time schedules or whether photos represent conditions today.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
import hashlib,json,time,argparse
ORIGIN="https://www.nipponferry.com"
PHOTOS={
"hiroshima-miyajima-ferry-crossing":{"file":"v72-miyajima-island-jr-ferry-gate.webp","author":"MaedaAkihiko","license":"CC BY-SA 4.0","source":"Miyajima-Ferry-STA_JR-Gate.jpg","year":"2022년"},
"shodoshima-ferry-island-access":{"file":"v72-shodoshima-tonosho-ferry-2010.webp","author":"Maarten Heerlien","license":"CC BY 2.0","source":"Shodo-shima_ferry_port_in_Tonosho_","year":"2010년"},
"okinawa-shuri-castle":{"file":"v72-shuri-reconstruction-feb2025.webp","author":"おにく","license":"CC0 1.0","source":"Shuri_Castle_Reconstruction.jpg","year":"2025년"}
}
def request(url):
 last=None
 for retry in range(3):
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NIPPONFERRY-V72-public-photo-QA/1.0)"}),timeout=16) as r:
    if r.status!=200:raise ValueError("HTTP "+str(r.status))
    return r.read(),r.headers.get("content-type","")
  except (TimeoutError,URLError,HTTPError,ValueError) as e:
   last=str(e);time.sleep(1+retry)
 raise RuntimeError(last)
def test(slug,item,mode,root):
 route="/things-to-do/"+slug+"/"
 img="/images/v72-verified/"+item["file"]
 if mode=="live":
  doc,typ=request(ORIGIN+route)
  assert "text/html" in typ.lower(),(slug,typ)
  raw,ityp=request(ORIGIN+img)
  assert ityp.lower().startswith("image/webp"),(slug,ityp)
 else:
  doc=(root/route.lstrip("/")/"index.html").read_bytes()
  raw=(root/img.lstrip("/")).read_bytes()
 s=doc.decode("utf-8","replace")
 for value in [img,ORIGIN+img,item["author"],item["license"],item["source"],item["year"],'href="/favicon.svg"']:
  assert value in s, (slug, "not present",value)
 assert 'href="'+ORIGIN+route+'"' in s,(slug,"canonical")
 assert "AI 생성" not in s,(slug,"obsolete AI copy")
 assert s.count('id="nf-v72-verified-photo"')==1 or (slug!="okinawa-shuri-castle" and s.count('id="nf-v72-verified-photo"')==1),(slug,"V72 provenance")
 assert len(raw)>25000 and raw[:4]==b"RIFF" and raw[8:12]==b"WEBP",(slug,"invalid webp")
 from html.parser import HTMLParser
 class Reader(HTMLParser):
  def __init__(self):super().__init__();self.images=[]
  def handle_starttag(self,tag,attrs):
   if tag=="img":self.images.append(dict(attrs).get("src"))
 p=Reader();p.feed(s)
 assert img in p.images,(slug,"hero src")
 assert "<script type=\"application/ld+json\">" in s,(slug,"missing JSON-LD")
 return {"slug":slug,"mode":mode,"page":ORIGIN+route,"hero":img,"image_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"status":"passed"}
def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=["static","live"],required=True);p.add_argument("--root",default="dist");a=p.parse_args()
 records=[]
 for slug,item in PHOTOS.items():
  try:record=test(slug,item,a.mode,Path(a.root));print("PASS",slug,record["image_bytes"],flush=True);records.append(record)
  except Exception as e:print("FAIL",slug,str(e),flush=True);records.append({"slug":slug,"mode":a.mode,"status":"failed","error":str(e)})
 report={"mode":a.mode,"total":len(records),"passed":sum(x["status"]=="passed" for x in records),"scope":"Existing three verified historical real-photo rollouts and exact public image URLs; no current facilities validation","records":records}
 out=Path("audit-output/v72");out.mkdir(parents=True,exist_ok=True);(out/(a.mode+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("SUMMARY",report["mode"],report["passed"],"/",report["total"])
 if report["passed"]!=len(PHOTOS):raise SystemExit(1)
if __name__=="__main__":main()
