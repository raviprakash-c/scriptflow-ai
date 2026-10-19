import json,logging,sys
from datetime import datetime,timezone
class JsonFormatter(logging.Formatter):
    def format(self,record):
        data={"timestamp":datetime.now(timezone.utc).isoformat(),"level":record.levelname.lower(),"logger":record.name,"message":record.getMessage()}
        for key in ("job_id","correlation_id","event"):
            if hasattr(record,key):data[key]=getattr(record,key)
        if record.exc_info:data["exception"]=self.formatException(record.exc_info)
        return json.dumps(data,ensure_ascii=False)
def configure_logging():
    handler=logging.StreamHandler(sys.stdout);handler.setFormatter(JsonFormatter())
    root=logging.getLogger();root.handlers.clear();root.addHandler(handler);root.setLevel(logging.INFO)
