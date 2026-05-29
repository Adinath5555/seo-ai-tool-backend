from pydantic import BaseModel


class Website(BaseModel):
    url: str


class UpdateReport(BaseModel):
    seo_score: int