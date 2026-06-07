import re
from sqlalchemy import func
from app.models.accident import Accident
from app.models.region import Region


def top_regions(db):
    result = (
        db.query(
            Region.name,
            func.count(Accident.accident_id).label("accidents")
        )
        .join(Accident, Accident.region_id == Region.region_id)
        .group_by(Region.name)
        .order_by(func.count(Accident.accident_id).desc())
        .limit(20)
        .all()
    )

    if not result:
        return []

    max_val = max(r.accidents for r in result)

    return [
        {
            "name": r.name,
            "accidents": r.accidents,
            "note": "Highest in Germany" if r.accidents == max_val else ""
        }
        for r in result
    ]


def yearly_trend(db):
    result = (
        db.query(
            Accident.year,
            func.count(Accident.accident_id).label("accidents")
        )
        .group_by(Accident.year)
        .order_by(Accident.year)
        .all()
    )

    return [
        {
            "year": r.year,
            "accidents": r.accidents,
            "note": ""
        }
        for r in result
    ]


# ✅ FIXED: smart parsing search
def region_summary(db, query: str):

    if not query:
        return {"error": "Empty query"}

    # extract year if present
    year_match = re.search(r"(19|20)\d{2}", query)
    year = int(year_match.group()) if year_match else None

    # extract city name (very simple logic)
    city = re.sub(r"(in\s)?(19|20)\d{2}", "", query, flags=re.IGNORECASE)
    city = city.replace("how many accidents are there", "")
    city = city.strip()

    # query DB
    q = db.query(
        Region.name,
        func.count(Accident.accident_id).label("accidents")
    ).join(Accident, Accident.region_id == Region.region_id)

    if city:
        q = q.filter(Region.name.ilike(f"%{city}%"))

    if year:
        q = q.filter(Accident.year == year)

    result = q.group_by(Region.name).first()

    if not result:
        return {
            "name": city or "Unknown",
            "year": year,
            "accidents": 0,
            "note": "No data found"
        }

    return {
        "name": result.name,
        "year": year,
        "accidents": result.accidents
    }