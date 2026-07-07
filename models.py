from pydantic import BaseModel


class AuditReport(BaseModel):
    website: str
    title: str
    meta_description: str
    h1_count: int
    total_images: int
    missing_alt_tags: int
    seo_score: int