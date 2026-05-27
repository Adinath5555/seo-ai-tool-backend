from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

from database import engine, SessionLocal, Base
from models import AuditReport

app = FastAPI()

Base.metadata.create_all(bind=engine)


class Website(BaseModel):
    url: str


@app.get("/")
def home():
    return {"message": "SEO AI Tool Backend Running"}


@app.post("/audit")
def audit_website(website: Website):

    db = SessionLocal()

    response = requests.get(website.url, timeout=5)

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string if soup.title else "No title found"

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    meta_content = (
        meta_description.get("content")
        if meta_description
        else "No meta description found"
    )

    h1_tags = soup.find_all("h1")

    h1_count = len(h1_tags)

    images = soup.find_all("img")

    total_images = len(images)

    missing_alt_tags = 0

    for image in images:

        if not image.get("alt"):
            missing_alt_tags += 1

    seo_score = 0

    if title != "No title found":
        seo_score += 30

    if meta_content != "No meta description found":
        seo_score += 30

    if h1_count > 0:
        seo_score += 20

    if missing_alt_tags == 0:
        seo_score += 20

    new_report = AuditReport(

        website=website.url,

        title=title,

        meta_description=meta_content,

        h1_count=h1_count,

        total_images=total_images,

        missing_alt_tags=missing_alt_tags,

        seo_score=seo_score
    )

    db.add(new_report)

    db.commit()

    db.refresh(new_report)

    return {
        "id": new_report.id,
        "website": website.url,
        "title": title,
        "meta_description": meta_content,
        "h1_count": h1_count,
        "total_images": total_images,
        "missing_alt_tags": missing_alt_tags,
        "seo_score": seo_score
    }


@app.get("/reports")
def get_reports():

    db = SessionLocal()

    reports = db.query(AuditReport).all()

    return reports

@app.get("/reports/{report_id}")
def get_report(report_id: int):

    db = SessionLocal()

    report = db.query(AuditReport).filter(
        AuditReport.id == report_id
    ).first()

    return report