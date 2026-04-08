from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from db.base import BaseModel as DBBase
from db.session import engine
from api.routes.auth import router as auth_router
from api.routes.user import router as user_router
from logger import logger
from core.config import settings
from api.controllers.base_controller import BaseController

# Create tables
DBBase.metadata.create_all(bind=engine)

# Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseController[None].error(exc.detail, status_code=exc.status_code).dict()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=BaseController[None].error("Validation error", exc.errors()).dict()
    )

# Include routers
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/", response_model=dict)
def root():
    return BaseController.success(message="Tapafix API is running!", status_code=200)
