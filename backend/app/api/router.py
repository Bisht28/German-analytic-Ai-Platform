from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.analytics import top_regions, yearly_trend, region_summary

api_router = APIRouter(prefix="/analytics")


@api_router.get("/top-regions")
def get_top_regions(db: Session = Depends(get_db)):
    return top_regions(db)


@api_router.get("/yearly-trend")
def get_yearly_trend(db: Session = Depends(get_db)):
    return yearly_trend(db)


@api_router.get("/region-summary")
def get_region_summary(
    query: str = Query(...),
    db: Session = Depends(get_db)
):
    return region_summary(db, query)