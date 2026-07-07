from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import requests

from database import reports_collection
from schemas import Website, UpdateReport
from services import audit_website_service

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


@app.get("/")
def home():
    return {"message": "SEO AI Tool Backend Running"}


@app.post("/audit")
async def audit_website(website: Website):

    try:
        result = audit_website_service(website.url)

    except requests.exceptions.RequestException:
        return {
            "error": "Website unreachable or invalid URL"
        }

    report = {
        "website": website.url,
        "title": result["title"],
        "meta_description": result["meta_description"],
        "h1_count": result["h1_count"],
        "total_images": result["total_images"],
        "missing_alt_tags": result["missing_alt_tags"],
        "seo_score": result["seo_score"],
        "ai_feedback": result["ai_feedback"]
    }

    inserted = await reports_collection.insert_one(report)

    report["_id"] = str(inserted.inserted_id)

    return report


@app.get("/reports")
async def get_reports():

    reports = []

    async for report in reports_collection.find():

        report["_id"] = str(report["_id"])

        reports.append(report)

    return reports


@app.get("/reports/{report_id}")
async def get_report(report_id: str):

    report = await reports_collection.find_one(
        {"_id": ObjectId(report_id)}
    )

    if report is None:
        return {"message": "Report not found"}

    report["_id"] = str(report["_id"])

    return report


@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):

    result = await reports_collection.delete_one(
        {"_id": ObjectId(report_id)}
    )

    if result.deleted_count == 0:
        return {"message": "Report not found"}

    return {"message": "Report deleted successfully"}


@app.put("/reports/{report_id}")
async def update_report(
    report_id: str,
    updated_data: UpdateReport
):

    result = await reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {
            "$set": {
                "seo_score": updated_data.seo_score
            }
        }
    )

    if result.matched_count == 0:
        return {"message": "Report not found"}

    updated_report = await reports_collection.find_one(
        {"_id": ObjectId(report_id)}
    )

    updated_report["_id"] = str(updated_report["_id"])

    return updated_report