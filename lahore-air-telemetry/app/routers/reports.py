import os
import shutil
from typing import List, Optional

from app.database import get_db
from app.models.report import Report
from app.models.zone import Zone
from app.schemas.report import ReportResponse
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from PIL import ExifTags, Image
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/reports", tags=["Reports"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PROFANITY_LIST = ["spam", "badword1"]  # Add relevant filter keywords if needed

# Track user votes by client IP to prevent multi-voting: {report_id: {client_ip: "up" | "down"}}
report_votes_tracker: dict[int, dict[str, str]] = {}


def check_profanity(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(word in text_lower for word in PROFANITY_LIST)


def extract_gps_from_exif(image_path: str):
    """Extracts latitude and longitude from image EXIF metadata if available."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None, None

        for tag_id, value in exif_data.items():
            tag = ExifTags.TAGS.get(tag_id)
            if tag == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = ExifTags.GPSTAGS.get(t)
                    gps_data[sub_tag] = value[t]

                def convert_to_degrees(val):
                    d, m, s = val
                    return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)

                if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                    lat = convert_to_degrees(gps_data["GPSLatitude"])
                    if gps_data.get("GPSLatitudeRef") == "S":
                        lat = -lat
                    lon = convert_to_degrees(gps_data["GPSLongitude"])
                    if gps_data.get("GPSLongitudeRef") == "W":
                        lon = -lon
                    return lat, lon
    except Exception as e:
        print(f"EXIF Extraction Error: {e}")
    return None, None


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(
    zone_id: int = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Submit a crowd-sourced local hazard report with optional image EXIF & moderation check."""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Specified zone not found")

    if check_profanity(description):
        raise HTTPException(
            status_code=400,
            detail="Report rejected: Content flagged by automated moderation filter.",
        )

    image_url = None
    lat, lon = None, None

    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_url = f"/static/uploads/{file.filename}"
        lat, lon = extract_gps_from_exif(file_path)

    new_report = Report(
        zone_id=zone_id,
        category=category,
        description=description,
        image_url=image_url,
        latitude=lat,
        longitude=lon,
        upvotes=0,
        downvotes=0,
        verification_status="Pending",
        moderation_status="Approved",
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    """Retrieve all submitted community hazard reports sorted by upvotes and recency."""
    reports = (
        db.query(Report)
        .order_by(Report.upvotes.desc(), Report.submitted_at.desc())
        .all()
    )
    return reports


@router.post("/{report_id}/vote")
def vote_report(
    report_id: int,
    request: Request,
    direction: str = Query(..., pattern="^(up|down)$"),
    db: Session = Depends(get_db),
):
    """Vote on a report with strict single-vote enforcement per IP, toggle behavior, and auto-escalation."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    client_ip = request.client.host

    if report_id not in report_votes_tracker:
        report_votes_tracker[report_id] = {}

    previous_vote = report_votes_tracker[report_id].get(client_ip)

    if previous_vote == direction:
        # Toggle off: user clicked the same vote button again to retract
        report_votes_tracker[report_id].pop(client_ip)
        if direction == "up":
            report.upvotes = max(0, report.upvotes - 1)
        else:
            report.downvotes = max(0, report.downvotes - 1)
        message = "Vote retracted"
    else:
        # Revert previous vote if switching sides (e.g. up to down)
        if previous_vote == "up":
            report.upvotes = max(0, report.upvotes - 1)
        elif previous_vote == "down":
            report.downvotes = max(0, report.downvotes - 1)

        # Apply new vote
        if direction == "up":
            report.upvotes += 1
        elif direction == "down":
            report.downvotes += 1

        report_votes_tracker[report_id][client_ip] = direction
        message = "Vote recorded"

    # Threshold Auto-Escalation Logic
    net_upvotes = report.upvotes - report.downvotes
    if net_upvotes >= 5 and report.verification_status == "Pending":
        report.verification_status = "High Priority"
        message += " and report auto-escalated to High Priority!"

    db.commit()
    db.refresh(report)
    return {
        "message": message,
        "upvotes": report.upvotes,
        "downvotes": report.downvotes,
        "verification_status": report.verification_status,
    }

    # Threshold Auto-Escalation Logic
    net_upvotes = report.upvotes - report.downvotes
    if net_upvotes >= 5 and report.verification_status == "Pending":
        report.verification_status = "High Priority"
        message += " and report auto-escalated to High Priority!"

    db.commit()
    db.refresh(report)
    return {
        "message": message,
        "upvotes": report.upvotes,
        "downvotes": report.downvotes,
        "verification_status": report.verification_status,
    }


@router.patch("/{report_id}/status")
def update_report_status(
    report_id: int, status: str = Query(...), db: Session = Depends(get_db)
):
    """
    Update the verification status of a community hazard report (Authority Triage).
    Allowed states: Pending, High Priority, Investigating, Resolved, False Report.
    """
    allowed_statuses = [
        "Pending",
        "High Priority",
        "Investigating",
        "Resolved",
        "False Report",
    ]
    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {allowed_statuses}",
        )

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Hazard report not found")

    report.verification_status = status
    db.commit()
    db.refresh(report)

    return {
        "message": f"Report #{report_id} status updated successfully",
        "id": report.id,
        "verification_status": report.verification_status,
    }
