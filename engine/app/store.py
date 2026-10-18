import threading,uuid
from datetime import datetime,timezone
_lock=threading.RLock();_jobs={};_keys={}
def now():return datetime.now(timezone.utc).isoformat()
def create_job(payload,key,digest,input_path=None):
    with _lock:
        if key and key in _keys:
            old_hash,job_id=_keys[key]
            return (_jobs[job_id],"replay") if old_hash==digest else (None,"conflict")
        job_id=str(uuid.uuid4())
        record={"job_id":job_id,"status":"queued","progress":0,"stage":"queued","created_at":now(),"updated_at":now(),"request":payload,"input_path":str(input_path) if input_path else None,"result":None,"error":None}
        _jobs[job_id]=record
        if key:_keys[key]=(digest,job_id)
        return record,"created"
def get_job(job_id):
    with _lock:return _jobs.get(job_id)
def patch_job(job_id,**changes):
    with _lock:
        _jobs[job_id].update(changes);_jobs[job_id]["updated_at"]=now();return dict(_jobs[job_id])
def list_jobs():
    with _lock:return [dict(x) for x in _jobs.values()]
