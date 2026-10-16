# Download a freely licensed *real* Tokyo skyline photograph, attribute the author, and convert to WebP.
# File: Tokyo Tower, Minato City.jpg; author David Kernan; CC BY 4.0.
import json, pathlib, urllib.request, urllib.parse, io, time
from PIL import Image
target=pathlib.Path('site/images/venues/tokyo-city-night-real.webp')
title='File:Tokyo_Tower,_Minato_City.jpg'
api='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','titles':title,'prop':'imageinfo','iiprop':'url','iiurlwidth':'1280','format':'json'})
urls=[]
headers={'User-Agent':'NIPPONFERRY-Editorial-RealPhoto/1.0 (license attribution: https://www.nipponferry.com/japan/tokyo/; contact via website)','Accept':'image/avif,image/webp,image/*,*/*'}
try:
 req=urllib.request.Request(api,headers=headers)
 with urllib.request.urlopen(req,timeout=18) as response:data=json.load(response)
 for page in data.get('query',{}).get('pages',{}).values():
  for info in page.get('imageinfo',[]):urls.extend([info.get('thumburl',''),info.get('url','')])
except Exception as e:print('Commons API:',type(e).__name__,str(e)[:120])
urls.extend([
'https://commons.wikimedia.org/wiki/Special:Redirect/file/Tokyo_Tower%2C_Minato_City.jpg?width=1280',
'https://commons.wikimedia.org/wiki/Special:Redirect/file/Tokyo_Tower%2C_Minato_City.jpg'
])
failures=[]
for uri in dict.fromkeys(u for u in urls if u):
 try:
  req=urllib.request.Request(uri,headers=headers)
  with urllib.request.urlopen(req,timeout=32) as response:
   raw=response.read(17*1024*1024)
  im=Image.open(io.BytesIO(raw))
  im.load()
  if im.width<800 or im.height<500:raise ValueError('Photo dimensions too small')
  im=im.convert('RGB')
  im.thumbnail((1500,1000))
  target.parent.mkdir(parents=True,exist_ok=True)
  im.save(target,'WEBP',quality=84,method=6)
  with Image.open(target) as verified:verified.verify()
  print(json.dumps({'saved':str(target),'source':uri,'px':[im.width,im.height],'bytes':target.stat().st_size,'credit':'David Kernan','license':'CC BY 4.0'},ensure_ascii=False))
  break
 except Exception as e:failures.append({'url':uri,'issue':str(e)[:180]});time.sleep(2)
else:raise RuntimeError('Real Wikimedia photo unavailable: '+json.dumps(failures)[:1700])
