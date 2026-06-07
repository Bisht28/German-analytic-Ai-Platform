from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ImportRun(Base):
    __tablename__ = "import_runs"

    import_run_id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False)
    licence = Column(String, nullable=True)
    retrieved_date = Column(String, nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())