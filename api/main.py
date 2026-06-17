from datetime import datetime, timezone
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Newcastle Repair Centre Contact API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.230:8090",
        "http://localhost:8090",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_DIR = Path("/app/data")
ENQUIRIES_FILE = DATA_DIR / "enquiries.jsonl"


class ContactEnquiry(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=5, max_length=30)
    vehicle: str | None = Field(default=None, max_length=120)
    message: str = Field(..., min_length=5, max_length=1000)
    company: str | None = Field(default=None, max_length=100)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/contact")
def submit_contact_form(enquiry: ContactEnquiry):
    # Honeypot spam check. Real users should never fill this field in.
    if enquiry.company:
        return {"success": True, "message": "Enquiry received"}

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    enquiry_data = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "name": enquiry.name,
        "phone": enquiry.phone,
        "vehicle": enquiry.vehicle,
        "message": enquiry.message,
    }

    try:
        with ENQUIRIES_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(enquiry_data) + "\n")
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save enquiry")

    return {
        "success": True,
        "message": "Thank you. Your enquiry has been sent.",
    }