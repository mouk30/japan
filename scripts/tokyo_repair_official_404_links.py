import pathlib,json
mapping=json.loads("{\"https://ginza6.tokyo/floor\":\"https://ginza6.tokyo/shops/\",\"https://www.donki.com/store/shop_detail.php?shop_id=376\":\"https://www.donki.com/en/store/shop_detail.php?shop_id=442\",\"https://www.gotokyo.org/en/destinations/central-tokyo/tsukishima/index.html\":\"https://www.gotokyo.org/en/spot/85/index.html\",\"https://www.gotokyo.org/en/plan/tokyo-outline/travel-tips/index.html\":\"https://www.gotokyo.org/en/plan/tips-for-tokyo-sightseeing/index.html\",\"https://www.shijou.metro.tokyo.lg.jp/english/toyosu/\":\"https://www.shijou.metro.tokyo.lg.jp/info/0/kenngaku/kenngaku1\",\"https://www.tokyo-zoo.net/english/ueno/\":\"https://www.tokyo-zoo.net/en/ueno/visitor-info/index.html\",\"https://www.tokyoeki-1bangai.co.jp/en/tokyocharacterstreet/\":\"https://www.tokyoeki-1bangai.co.jp/tokyocharacterstreet/\"}")
changed=[]
for p in pathlib.Path("site/japan/tokyo").glob("*/index.html"):
 src=p.read_text(encoding="utf8");after=src
 for old,new in mapping.items():after=after.replace(old,new)
 if after!=src:
  p.write_text(after,encoding="utf8")
  changed.append({"page":p.parent.name,"replacements":[old for old in mapping if old in src]})
assert len(changed)>=7,changed
pathlib.Path("audit-reports/tokyo-verified-official-404-repairs.json").write_text(json.dumps({"changed_pages":len(changed),"repaired_original_urls":len(mapping),"false_positives_rechecked_by_web":["https://teamlabplanets.dmm.com/en","https://teamlabplanets.dmm.com/en/guide/access_method"],"pages":changed},ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"changed_pages":len(changed),"old_urls":len(mapping)},ensure_ascii=False))
