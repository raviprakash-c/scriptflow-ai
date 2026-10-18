import hashlib, json, logging, os, re, uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, File, Header, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from .config import settings
from .errors import ServiceError, service_error_handler
from .logging_config import configure_logging
from .models import JobRequest
from .store import create_job, get_job, list_jobs
from .worker import run_job

configure_logging()
logger=logging.getLogger("scriptflow.api")
settings.output_dir.mkdir(parents=True,exist_ok=True)
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
app=FastAPI(title="ScriptFlow AI B-roll Engine",version="0.2.0",description="Script/audio to scene-timed B-roll render API",lifespan=lifespan)
app.add_exception_handler(ServiceError,service_error_handler)
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])
@app.middleware("http")
async def correlation(request: Request, call_next):
    cid=request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
    request.state.correlation_id=cid
    response=await call_next(request); response.headers["X-Correlation-Id"]=cid
    return response
@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.exception("unhandled request error",extra={"correlation_id":getattr(request.state,"correlation_id",None),"event":"api_error"})
    return JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An internal error occurred.","retryable":True,"details":{"correlation_id":getattr(request.state,"correlation_id",None)}}})
@app.get("/health",tags=["operations"])
def health(): return {"status":"ok","service":settings.app_name}
@app.get("/ready",tags=["operations"])
def ready(): return {"status":"ready","output_dir_writable":os.access(settings.output_dir,os.W_OK)}
def _submit(request, key, digest, background, input_path=None):
    job,state=create_job(request.model_dump(mode="json"),key,digest,input_path)
    if state=="conflict": raise ServiceError("IDEMPOTENCY_KEY_REUSED","Idempotency-Key already used for a different request.",False,{"header":"Idempotency-Key"},409)
    if state=="created": background.add_task(run_job,job["job_id"])
    return {"job_id":job["job_id"],"status":job["status"],"status_url":f"/api/v1/jobs/{job['job_id']}","idempotent_replay":state=="replay"}
@app.post("/api/v1/broll/jobs",status_code=202,tags=["jobs"])
async def submit(request: JobRequest, background: BackgroundTasks, idempotency_key: Annotated[str|None,Header(alias="Idempotency-Key")]=None):
    if idempotency_key and len(idempotency_key)>200: raise ServiceError("INVALID_IDEMPOTENCY_KEY","Idempotency-Key too long.")
    if request.audio_url: raise ServiceError("REMOTE_AUDIO_UNAVAILABLE","Remote audio URL ingestion is not enabled; use the upload endpoint.",False,{},501)
    return _submit(request,idempotency_key,hashlib.sha256(request.model_dump_json().encode()).hexdigest(),background)
@app.post("/api/v1/broll/jobs/upload",status_code=202,tags=["jobs"])
async def submit_upload(background: BackgroundTasks, file: UploadFile=File(...), voice: str="en-IN-female", aspect_ratios: str="16:9", style: str="bright, modern, real-world footage", avoid: str="", idempotency_key: Annotated[str|None,Header(alias="Idempotency-Key")]=None):
    suffix=Path(file.filename or "").suffix.lower()
    if suffix not in {".mp3",".wav",".m4a"}: raise ServiceError("UNSUPPORTED_AUDIO_TYPE","Upload mp3, wav, or m4a audio.",False,{"filename":file.filename},415)
    ratios=[x.strip() for x in aspect_ratios.split(",") if x.strip()]
    req=JobRequest(audio_url="https://local-upload.invalid/audio",voice=voice,aspect_ratios=ratios,style=style,avoid=[x.strip() for x in avoid.split(",") if x.strip()])
    folder=settings.output_dir/"uploads"; folder.mkdir(parents=True,exist_ok=True); path=folder/f"{uuid.uuid4()}{suffix}"
    size=0
    with path.open("wb") as fh:
        while True:
            chunk=await file.read(1024*1024)
            if not chunk: break
            size+=len(chunk)
            if size>settings.max_upload_mb*1024*1024:
                path.unlink(missing_ok=True); raise ServiceError("UPLOAD_TOO_LARGE","Audio exceeds configured size limit.",False,{"max_mb":settings.max_upload_mb},413)
            fh.write(chunk)
    digest=hashlib.sha256(path.read_bytes()+req.model_dump_json().encode()).hexdigest()
    return _submit(req,idempotency_key,digest,background,path)
@app.get("/api/v1/jobs",tags=["jobs"])
def jobs(): return {"jobs":[{"job_id":j["job_id"],"status":j["status"],"progress":j["progress"],"stage":j["stage"],"created_at":j["created_at"]} for j in list_jobs()]}
@app.get("/api/v1/jobs/{job_id}",tags=["jobs"])
def status(job_id: str):
    job=get_job(job_id)
    if not job: raise ServiceError("JOB_NOT_FOUND","No job exists with this id.",False,{"job_id":job_id},404)
    result=job["result"]
    return {"job_id":job_id,"status":job["status"],"progress":job["progress"],"stage":job["stage"],"created_at":job["created_at"],"updated_at":job["updated_at"],"result":{"links":result.get("outputs",{}),"duration":result.get("duration"),"warnings":result.get("warnings",[])} if result else None,"error":job["error"]}
@app.get("/api/v1/jobs/{job_id}/files/{filename}",tags=["outputs"])
def download(job_id: str, filename: str):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}",filename) or ".." in filename: raise ServiceError("INVALID_FILENAME","Invalid output filename.")
    if not get_job(job_id): raise ServiceError("JOB_NOT_FOUND","No job exists with this id.",False,{"job_id":job_id},404)
    path=settings.output_dir/job_id/filename
    if not path.exists() or not path.is_file(): raise ServiceError("OUTPUT_NOT_FOUND","Output file is not available.",False,{"filename":filename},404)
    return FileResponse(path,filename=filename)
@app.post("/api/v1/jobs/{job_id}/retry",status_code=202,tags=["jobs"])
def retry(job_id: str, background: BackgroundTasks, idempotency_key: Annotated[str|None,Header(alias="Idempotency-Key")]=None):
    old=get_job(job_id)
    if not old: raise ServiceError("JOB_NOT_FOUND","No job exists with this id.",False,{"job_id":job_id},404)
    if old["status"]!="failed": raise ServiceError("JOB_NOT_FAILED","Only failed jobs can be retried.",False,{"status":old["status"]},409)
    from .store import create_job
    digest=hashlib.sha256((job_id+str(uuid.uuid4())).encode()).hexdigest()
    fresh,_=create_job(old["request"],idempotency_key,digest,Path(old["input_path"]) if old.get("input_path") else None)
    background.add_task(run_job,fresh["job_id"])
    return {"job_id":fresh["job_id"],"status":fresh["status"],"status_url":f"/api/v1/jobs/{fresh['job_id']}","retry_of":job_id}
