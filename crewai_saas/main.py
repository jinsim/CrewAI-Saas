import json
import os
import uvicorn

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

from crewai_saas.api.api_v1.api import api_router
from crewai_saas.core.config import settings
from crewai_saas.core.events import lifespan
from crewai_saas.core.exceptions import CustomException, unicorn_exception_handler


def create_app() -> FastAPI:
    # init FastAPI with lifespan
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=lambda router: f"{router.tags[0]}-{router.name}",
    )
    # set CORS
    # Set all CORS enabled origins
    origins = [
        "http://127.0.0.1:3000",  # 로컬 개발 환경
        "http://localhost:3000",  # 로컬 개발 환경
        "https://crewai-saas-aqnzqc74rq-an.a.run.app",  # 배포된 백엔드
        # 필요에 따라 다른 도메인 추가
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # 명시적으로 허용할 도메인 리스트
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    # Include the routers
    app.include_router(api_router, prefix=settings.API_V1_STR)


    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 307:  # 리디렉션 응답에만 헤더 추가
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
    return response


app.add_exception_handler(CustomException, unicorn_exception_handler)