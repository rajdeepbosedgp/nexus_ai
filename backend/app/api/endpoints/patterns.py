from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.models import User, Complaint, Pattern
from app.schemas.schemas import PatternOut, PatternDetectResponse, ComplaintOut
from app.api.deps import get_current_user, require_admin
from app.services.pattern_discovery import discover_emergent_patterns
from app.services.overdue import calculate_overdue_risk_score

router = APIRouter(prefix="/patterns", tags=["Patterns"])

@router.post("/detect", response_model=PatternDetectResponse)
async def trigger_pattern_discovery(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Fetch all open / in-progress complaints to run detection on
    stmt = select(Complaint)
    res = await db.execute(stmt)
    complaints = res.scalars().all()

    complaints_data = [
        {
            "id": c.id,
            "category": c.category,
            "description": c.description,
            "created_at": c.created_at,
            "weather_event": c.weather_event
        }
        for c in complaints
    ]

    discovered = await discover_emergent_patterns(complaints_data)

    pattern_objects = []
    for pat in discovered:
        db_pattern = Pattern(
            name=pat["name"],
            description=pat["description"],
            strength_score=pat["strength_score"],
            cohesion=pat["cohesion"],
            size=pat["size"],
            category_spread=pat["category_spread"],
            temporal_concentration=pat["temporal_concentration"],
            complaint_ids=pat["complaint_ids"],
            label_source=pat["label_source"],
            status="Active"
        )
        db.add(db_pattern)
        pattern_objects.append(db_pattern)

    await db.commit()

    # Hydrate pattern output with linked complaints
    out_patterns = []
    for p in pattern_objects:
        await db.refresh(p)
        c_stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id.in_(p.complaint_ids))
        c_res = await db.execute(c_stmt)
        linked_complaints = c_res.scalars().all()
        
        c_outs = []
        for lc in linked_complaints:
            out_c = ComplaintOut.model_validate(lc)
            out_c.overdue_risk_score = calculate_overdue_risk_score(lc.created_at, lc.category, lc.status)
            c_outs.append(out_c)

        p_out = PatternOut.model_validate(p)
        p_out.complaints = c_outs
        out_patterns.append(p_out)

    msg = f"Pattern Discovery Engine analyzed {len(complaints_data)} complaints and identified {len(out_patterns)} emergent pattern(s)."
    return PatternDetectResponse(
        detected_count=len(out_patterns),
        patterns=out_patterns,
        message=msg
    )

@router.get("", response_model=List[PatternOut])
async def list_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Pattern).order_by(desc(Pattern.detected_at))
    res = await db.execute(stmt)
    patterns = res.scalars().all()

    output = []
    for p in patterns:
        c_stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id.in_(p.complaint_ids))
        c_res = await db.execute(c_stmt)
        linked_complaints = c_res.scalars().all()
        
        c_outs = [ComplaintOut.model_validate(lc) for lc in linked_complaints]

        p_out = PatternOut.model_validate(p)
        p_out.complaints = c_outs
        output.append(p_out)

    return output

@router.get("/{pattern_id}", response_model=PatternOut)
async def get_pattern_detail(
    pattern_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Pattern).where(Pattern.id == pattern_id)
    res = await db.execute(stmt)
    pattern = res.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="Emergent pattern not found.")

    c_stmt = select(Complaint).options(selectinload(Complaint.history)).where(Complaint.id.in_(pattern.complaint_ids))
    c_res = await db.execute(c_stmt)
    linked_complaints = c_res.scalars().all()

    p_out = PatternOut.model_validate(pattern)
    p_out.complaints = [ComplaintOut.model_validate(lc) for lc in linked_complaints]
    return p_out
