from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.models import User, Complaint, Pattern
from app.schemas.schemas import DashboardOut, ComplaintOut
from app.api.deps import get_current_user
from app.services.overdue import calculate_overdue_risk_score, is_complaint_overdue

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardOut)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Complaint).options(selectinload(Complaint.history))
    if current_user.role == "resident":
        stmt = stmt.where(Complaint.resident_id == current_user.id)

    res = await db.execute(stmt)
    all_complaints = res.scalars().all()

    total = len(all_complaints)
    open_cnt = sum(1 for c in all_complaints if c.status == "Open")
    in_prog_cnt = sum(1 for c in all_complaints if c.status == "In Progress")
    resolved_cnt = sum(1 for c in all_complaints if c.status == "Resolved")

    # Overdue evaluation
    overdue_cnt = sum(1 for c in all_complaints if is_complaint_overdue(c.created_at, c.category, c.status))

    # Category counts
    by_cat = {}
    for c in all_complaints:
        by_cat[c.category] = by_cat.get(c.category, 0) + 1

    # Detected pattern count
    pat_stmt = select(func.count(Pattern.id))
    pat_res = await db.execute(pat_stmt)
    pat_count = pat_res.scalar() or 0

    # Calculate risk score and sort for top overdue list
    out_complaints = []
    for c in all_complaints:
        out = ComplaintOut.model_validate(c)
        out.overdue_risk_score = calculate_overdue_risk_score(c.created_at, c.category, c.status)
        if out.overdue_risk_score > 0:
            out_complaints.append(out)

    top_overdue = sorted(out_complaints, key=lambda x: x.overdue_risk_score, reverse=True)[:5]

    return DashboardOut(
        total_complaints=total,
        open_count=open_cnt,
        in_progress_count=in_prog_cnt,
        resolved_count=resolved_cnt,
        overdue_count=overdue_cnt,
        detected_patterns_count=pat_count,
        by_category=by_cat,
        top_overdue=top_overdue
    )
