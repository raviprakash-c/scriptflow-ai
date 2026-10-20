#!/usr/bin/env python3
import argparse,json,pathlib,time
import httpx
def load(path):
    text=path.read_text(encoding="utf-8")
    if path.suffix.lower()==".jsonl":return [json.loads(x) for x in text.splitlines() if x.strip()]
    data=json.loads(text);return data if isinstance(data,list) else [data]
def main():
    p=argparse.ArgumentParser();p.add_argument("input",type=pathlib.Path);p.add_argument("--base-url",default="http://localhost:8000");p.add_argument("--out",type=pathlib.Path,default=pathlib.Path("test-pack"));p.add_argument("--timeout",type=int,default=900);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);index=[]
    with httpx.Client(timeout=a.timeout) as client:
        for i,case in enumerate(load(a.input),1):
            name=f"case-{i:03}";record={"input":case}
            try:
                response=client.post(a.base_url+"/api/v1/broll/jobs",json=case,headers={"Idempotency-Key":name})
                record["submit"]={"status":response.status_code,"body":response.json()}
                if response.status_code==202:
                    jid=response.json()["job_id"];end=time.time()+a.timeout
                    while time.time()<end:
                        status=client.get(a.base_url+f"/api/v1/jobs/{jid}").json();record["status"]=status
                        if status.get("status") in ("succeeded","failed"):break
                        time.sleep(1)
                    links=(record.get("status") or {}).get("result",{}).get("links",{});record["downloads"]={}
                    for fname,url in links.items():
                        res=client.get(a.base_url+url);(a.out/f"{name}-{fname}").write_bytes(res.content)
                        record["downloads"][fname]={"status":res.status_code,"bytes":len(res.content)}
            except Exception as exc:record["exception"]={"type":type(exc).__name__,"message":str(exc)}
            (a.out/f"{name}.json").write_text(json.dumps(record,indent=2,ensure_ascii=False))
            index.append({"case":name,"http_status":record.get("submit",{}).get("status"),"job_status":record.get("status",{}).get("status"),"exception":record.get("exception")})
    (a.out/"index.json").write_text(json.dumps(index,indent=2));print(f"Saved {len(index)} results to {a.out}")
if __name__=="__main__":main()
