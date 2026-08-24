from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models.models import User, Notice
from app.schemas.schemas import NoticeCreate, NoticeOut
from app.api.deps import get_current_user, require_admin
from app.services.email import notify_important_notice

router = APIRouter(prefix="/notices", tags=["Notices"])

@router.post("", response_model=NoticeOut)
async def create_notice(
    notice_in: NoticeCreate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    notice = Notice(
        admin_id=admin_user.id,
        title=notice_in.title,
        body=notice_in.body,
        is_important=notice_in.is_important
    )
    db.add(notice)
    await db.commit()
    await db.refresh(notice)

    if notice.is_important:
        stmt = select(User.email).where(User.role == "resident")
        res = await db.execute(stmt)
        emails = res.scalars().all()
        if emails:
            await notify_important_notice(list(emails), notice.title, notice.body)

    return NoticeOut.model_validate(notice)

@router.get("", response_model=List[NoticeOut])
async def list_notices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Notice).order_by(desc(Notice.is_important), desc(Notice.created_at))
    res = await db.execute(stmt)
    notices = res.scalars().all()
    return [NoticeOut.model_validate(n) for n in notices]
