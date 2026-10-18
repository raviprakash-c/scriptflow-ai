from fastapi import Request
from fastapi.responses import JSONResponse
class ServiceError(Exception):
    def __init__(self,code,message,retryable=False,details=None,status_code=400):
        self.code,self.message,self.retryable=code,message,retryable
        self.details,self.status_code=details or {},status_code
        super().__init__(message)
async def service_error_handler(_: Request,exc: ServiceError):
    return JSONResponse(status_code=exc.status_code,content={"error":{"code":exc.code,"message":exc.message,"retryable":exc.retryable,"details":exc.details}})
