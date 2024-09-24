import os
import uvicorn
import threading
import inspect
import logging

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

from crewai_saas.api.api_v1.api import api_router
from crewai_saas.core.config import settings
from crewai_saas.core.events import lifespan
from crewai_saas.core.exceptions import CustomException, unicorn_exception_handler

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=lambda router: f"{router.tags[0]}-{router.name}",
    )
    origins = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://crewai-saas-aqnzqc74rq-an.a.run.app",
        "groopy.me",
        "https://groopy.me"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_V1_STR)

    logger.info(f"thread Id : {threading.get_ident()}, method Id : {inspect.currentframe().f_code.co_name}")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 307:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
    return response


app.add_exception_handler(CustomException, unicorn_exception_handler)