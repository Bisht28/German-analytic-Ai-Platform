from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.faq import router as faq_router
from api.stats import router as stats_router
from api.query import router as query_router

from db.connection import get_connection

app = FastAPI(
    title="RoadInsight AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# API Routers
app.include_router(faq_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(query_router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "RoadInsight AI"
    }


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()

        return {
            "status": "healthy",
            "database": result[0] == 1
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }