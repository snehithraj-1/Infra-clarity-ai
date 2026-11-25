import asyncio
from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_v1_router
from app.config import config
from app.jobs.storage import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("infraclarity")


async def periodic_job_cleanup():
    while True:
        try:
            await asyncio.sleep(config.storage.cleanup_interval_seconds)
            purged = storage.cleanup_old_jobs(config.storage.job_ttl_seconds)
            if purged > 0:
                logger.info(f"Storage cleanup: purged {purged} expired inspection jobs")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in background cleanup worker: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {config.app.name} v{config.app.version}")
    cleanup_task = asyncio.create_task(periodic_job_cleanup())
    yield
    cleanup_task.cancel()
    logger.info("InfraClarity AI server shut down")


app = FastAPI(
    title=config.app.name,
    version=config.app.version,
    description=config.app.description,
    lifespan=lifespan,
)

# CORS configuration for frontend dev origin and network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned API routes
app.include_router(api_v1_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal server error occurred", "status_code": 500},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
