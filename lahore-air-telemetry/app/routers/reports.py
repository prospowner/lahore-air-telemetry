# app/routers/reports.py
from typing import List

from app.database import get_db
from app.models.report import Report
from app.models.zone import Zone
from app.schemas.report import ReportCreate, ReportResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("", response_model=ReportResponse, status_code=201)
def create_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """Submit a crowd-sourced local hazard report (e.g., waste burning, heavy smoke)."""
    zone = db.query(Zone).filter(Zone.id == report_data.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Specified zone not found")

    new_report = Report(
        zone_id=report_data.zone_id,
        category=report_data.category,
        description=report_data.description,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    """Retrieve all submitted community hazard reports."""
    reports = db.query(Report).order_by(Report.submitted_at.desc()).all()
    return reports


@router.patch("/{report_id}/status")
def update_report_status(
    report_id: int, status: str = Query(...), db: Session = Depends(get_db)
):
    """
    Update the verification status of a community hazard report (Authority Triage).
    Allowed states: Pending, Investigating, Resolved, False Report.
    """
    allowed_statuses = ["Pending", "Investigating", "Resolved", "False Report"]
    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {allowed_statuses}",
        )

    # Query the report from your database model
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
