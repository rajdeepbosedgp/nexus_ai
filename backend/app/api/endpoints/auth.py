from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import User, Apartment
from app.schemas.schemas import UserRegister, UserLogin, UserOut, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    apt = Apartment(
        building=user_in.building or "Block A",
        floor=user_in.floor or 1,
        unit_number=user_in.unit_number or "101"
    )
    db.add(apt)
    await db.flush()

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role if user_in.role in ("resident", "admin") else "resident",
        apartment_id=apt.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token_str = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=token_str, user=UserOut.model_validate(user))

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token_str = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=token_str, user=UserOut.model_validate(user))

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
