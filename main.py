import uvicorn
import logging

from fastapi import FastAPI, Response, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.seriescatalog import get_series_catalog

from models.userregister import UserRegister
from models.userlogin import UserLogin
from models.seriescatalog import SeriesCatalog

from utils.security import validate
from utils.telemetry import setup_simple_telemetry

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger(__name__)
load_dotenv()

telemetry_enabled = setup_simple_telemetry()
if telemetry_enabled:
    logger.info("Application Insights enabled")
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
else:
    logger.warning("Application Insight disabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Series API",
    description="Series API Lab expert system",
    version="0.0.1",
    lifespan=lifespan
)

if telemetry_enabled:
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI Instrummented")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
        , "version": "0.0.1"
    }

@app.get("/")
async def read_root(request: Request, response: Response):
    return {
        "hello": "world"
    }


@app.post("/signup")
async def signup(user: UserRegister):
    result = await register_user_firebase(user)
    return result


@app.post("/login")
async def login(user: UserLogin):
    result = await login_user_firebase(user)
    return result


@app.get("/series")
async def get_series() -> list[SeriesCatalog]:
    series: list[SeriesCatalog] = await get_series_catalog()
    return series


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")