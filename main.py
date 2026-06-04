from fastapi import FastAPI
import requests

from database import engine, SessionLocal, Base
from models import AuditReport
from schemas import Website, UpdateReport
from services import audit_website_service
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "SEO AI Tool Backend Running"}


@app.post("/audit")
def audit_website(website: Website):

    db = SessionLocal()

    try:

        result = audit_website_service(
            website.url
        )

    except requests.exceptions.RequestException:

        db.close()

        return {
            "error": "Website unreachable or invalid URL"
        }

    title = result["title"]

    meta_content = result["meta_description"]

    h1_count = result["h1_count"]

    total_images = result["total_images"]

    missing_alt_tags = result["missing_alt_tags"]

    seo_score = result["seo_score"]

    ai_feedback = result["ai_feedback"]

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

    db.close()

    return {
    "id": new_report.id,
    "website": website.url,
    "title": title,
    "meta_description": meta_content,
    "h1_count": h1_count,
    "total_images": total_images,
    "missing_alt_tags": missing_alt_tags,
    "seo_score": seo_score,
    "ai_feedback": ai_feedback
}

@app.get("/reports")
def get_reports():

    db = SessionLocal()

    reports = db.query(AuditReport).all()
    db.close()

    return reports


@app.get("/reports/{report_id}")
def get_report(report_id: int):

    db = SessionLocal()

    report = db.query(AuditReport).filter(
    AuditReport.id == report_id
    ).first()
    db.close()
    return report

@app.delete("/reports/{report_id}")
def delete_report(report_id: int):

    db = SessionLocal()

    report = db.query(AuditReport).filter(
        AuditReport.id == report_id
    ).first()

    if report is None:
        db.close()
        return {"message": "Report not found"}

    db.delete(report)

    db.commit()
    db.close()

    return {"message": "Report deleted successfully"}


@app.put("/reports/{report_id}")
def update_report(
    report_id: int,
    updated_data: UpdateReport
):

    db = SessionLocal()

    report = db.query(AuditReport).filter(
        AuditReport.id == report_id
    ).first()

    if report is None:
        db.close()
        return {"message": "Report not found"}

    report.seo_score = updated_data.seo_score

    db.commit()

    db.refresh(report)
    db.close()

    return report