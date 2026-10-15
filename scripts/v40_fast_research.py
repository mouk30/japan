#!/usr/bin/env python3
"""V40 faster concurrent Wikimedia photo-candidate search; read-only until candidates chosen."""
from __future__ import annotations
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from v40_commons_research import TOPICS, fetch

def task(arg):
    slug,query=arg
    try:
        return slug,query,fetch(query),None
    except Exception as e:
        return slug,query,[],str(e)[:160]

report={slug:{"options":[],"errors":[],"candidate_count":0} for slug in TOPICS}
tasks=[(slug,q) for slug,queries in TOPICS.items() for q in queries]
with ThreadPoolExecutor(max_workers=5) as pool:
    futures={pool.submit(task,t):t for t in tasks}
    for fut in as_completed(futures):
        slug,q,photos,error=fut.result()
        if error:report[slug]["errors"].append(f"{q}: {error}")
        else:
            for photo in photos:
                if photo["filename"] not in {x["filename"] for x in report[slug]["options"]}:
                    photo["query"]=q
                    report[slug]["options"].append(photo)
        print(f"{slug}: {q}: {len(photos)}",flush=True)
for slug,obj in report.items():
    obj["candidate_count"]=len(obj["options"])
    obj["options"]=obj["options"][:20]
path=Path("docs/v40-fast-candidates.json")
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("V40 FAST CANDIDATES",sum(bool(x["options"]) for x in report.values()),len(report),flush=True)
