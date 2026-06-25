from fastapi import APIRouter
from db.repository import get_system_stats

router = APIRouter()


@router.get("/stats")
def stats():
    return get_system_stats()