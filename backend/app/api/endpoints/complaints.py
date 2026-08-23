import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import User, Complaint, ComplaintHistory
from app.schemas.schemas import ComplaintCreate, ComplaintOut, ComplaintStatusUpdate, ComplaintHistoryOut
from app.api.deps import get_current_user, require_admin
from app.services.overdue import calculate_overdue_risk_score
from app.services.email import notify_complaint_status_change

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/upload")
async def upload_complaint_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Handles photo file uploads for resident complaints with size & MIME validation.
    Saves file to backend/uploads/ and returns relative photo_url.
    """
    allowed_mime_types = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/jpg"}
    if file.content_type and file.content_type.lower() not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Allowed image formats: JPEG, PNG, WEBP, GIF."
        )

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    ext = os.path.splitext(file.filename or "photo.jpg")[1].lower()
    if not ext or ext not in allowed_extensions:
        ext = ".jpg"

    contents = await file.read()
    max_size_bytes = 5 * 1024 * 1024  # 5 MB limit
    if len(contents) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum 5 MB limit."
        )

    import base64
    b64_str = base64.b64encode(contents).decode("utf-8")
    mime = file.content_type or "image/jpeg"
    photo_data_url = f"data:{mime};base64,{b64_str}"

    filename = f"photo_{uuid.uuid4().hex[:12]}{ext}"
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return {"photo_url": photo_data_url}

@router.post("", response_model=ComplaintOut)
async def create_complaint(
    complaint_in: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    complaint = Complaint(
        resident_id=current_user.id,
        apartment_id=current_user.apartment_id,
        category=complaint_in.category,
        description=complaint_in.description,
        photo_url=complaint_in.photo_url,
        priority=complaint_in.priority or "Medium",
        status="Open",
        weather_event=complaint_in.weather_event
    )
    db.add(complaint)
    await db.flush()

    # Initial history log entry
    history = ComplaintHistory(
        complaint_id=complaint.id,
        actor_id=current_user.id,
        from_status="None",
        to_status="Open",
        note="Complaint created by resident."
    )
    db.add(history)
    await db.commit()

    # Reload with history
    stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id == complaint.id)
    res = await db.execute(stmt)
    created = res.scalar_one()
    
    out = ComplaintOut.model_validate(created)
    out.overdue_risk_score = calculate_overdue_risk_score(created.created_at, created.category, created.status)
    return out

@router.get("", response_model=List[ComplaintOut])
async def list_complaints(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).options(selectinload(Complaint.history)).order_by(desc(Complaint.created_at))
    
    if current_user.role == "resident":
        stmt = stmt.where(Complaint.resident_id == current_user.id)

    if category:
        stmt = stmt.where(Complaint.category == category)
    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)

    res = await db.execute(stmt)
    complaints = res.scalars().all()

    output = []
    for c in complaints:
        out = ComplaintOut.model_validate(c)
        out.overdue_risk_score = calculate_overdue_risk_score(c.created_at, c.category, c.status)
        output.append(out)
    return output

@router.get("/{complaint_id}", response_model=ComplaintOut)
async def get_complaint(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id == complaint_id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    
    if current_user.role == "resident" and complaint.resident_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    out = ComplaintOut.model_validate(complaint)
    out.overdue_risk_score = calculate_overdue_risk_score(complaint.created_at, complaint.category, complaint.status)
    return out

@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
async def update_complaint_status(
    complaint_id: str,
    status_in: ComplaintStatusUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).options(selectinload(Complaint.history), selectinload(Complaint.resident)).where(Complaint.id == complaint_id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    if status_in.status not in ("Open", "In Progress", "Resolved"):
        raise HTTPException(status_code=400, detail="Invalid status value.")

    old_status = complaint.status
    complaint.status = status_in.status

    # Record immutable history log entry
    history = ComplaintHistory(
        complaint_id=complaint.id,
        actor_id=admin_user.id,
        from_status=old_status,
        to_status=status_in.status,
        note=status_in.note or f"Status updated to {status_in.status}"
    )
    db.add(history)
    await db.commit()
    await db.refresh(complaint)

    # Dispatch email notification to resident
    if complaint.resident and complaint.resident.email:
        await notify_complaint_status_change(
            user_email=complaint.resident.email,
            complaint_id=complaint.id,
            old_status=old_status,
            new_status=status_in.status,
            note=status_in.note
        )

    out = ComplaintOut.model_validate(complaint)
    out.overdue_risk_score = calculate_overdue_risk_score(complaint.created_at, complaint.category, complaint.status)
    return out

@router.patch("/{complaint_id}/priority", response_model=ComplaintOut)
async def update_complaint_priority(
    complaint_id: str,
    priority: str = Query(..., regex="^(Low|Medium|High)$"),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id == complaint_id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    complaint.priority = priority
    await db.commit()
    await db.refresh(complaint)

    out = ComplaintOut.model_validate(complaint)
    out.overdue_risk_score = calculate_overdue_risk_score(complaint.created_at, complaint.category, complaint.status)
    return out
