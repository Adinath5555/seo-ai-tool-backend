from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))

db = client["seo_ai_tool"]

reports_collection = db["audit_reports"]