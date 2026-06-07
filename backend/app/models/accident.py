from sqlalchemy import Column, Integer, Float, ForeignKey
from app.core.database import Base

class Accident(Base):
    __tablename__ = "accidents"

    accident_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)