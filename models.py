from sqlalchemy import Column, Integer, String
from database import Base


class AuditReport(Base):

    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True, index=True)

    website = Column(String)

    title = Column(String)

    meta_description = Column(String)

    h1_count = Column(Integer)

    total_images = Column(Integer)

    missing_alt_tags = Column(Integer)

    seo_score = Column(Integer)