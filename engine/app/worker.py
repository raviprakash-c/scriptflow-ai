import asyncio,logging
from pathlib import Path
from .models import JobRequest
from .render import render_job
from .store import get_job,patch_job
log=logging.getLogger("scriptflow.worker")
async def run_job(job_id):
    try:
        job=get_job(job_id)
        if not job:return
        patch_job(job_id,status="running",progress=1,stage="starting")
        request=JobRequest.model_validate(job["request"])
        input_path=Path(job["input_path"]) if job.get("input_path") else None
        def progress(pct,stage):patch_job(job_id,progress=max(0,min(100,int(pct))),stage=stage)
        result=await asyncio.to_thread(render_job,job_id,request,input_path,progress)
        patch_job(job_id,status="succeeded",progress=100,stage="complete",result=result,error=None)
        log.info("job succeeded",extra={"job_id":job_id,"event":"job_succeeded"})
    except Exception as exc:
        code="INVALID_INPUT" if isinstance(exc,ValueError) else "RENDER_FAILED"
        patch_job(job_id,status="failed",progress=0,stage="failed",error={"code":code,"message":str(exc) or "Job failed","retryable":code!="INVALID_INPUT","details":{"type":type(exc).__name__}})
        log.exception("job failed",extra={"job_id":job_id,"event":"job_failed"})
