from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Region(Base):
    __tablename__ = "regions"

    region_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ags = Column(String, index=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    parent_region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=True)

    parent = relationship("Region", remote_side=[region_id])