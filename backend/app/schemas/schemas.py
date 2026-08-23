from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "resident"  # "resident" or "admin"
    building: Optional[str] = "Block A"
    floor: Optional[int] = 1
    unit_number: Optional[str] = "101"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    apartment_id: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Complaint Schemas ---
class ComplaintCreate(BaseModel):
    category: str  # Electrical, Plumbing, Cosmetic, Cleaning, General
    description: str
    photo_url: Optional[str] = None
    priority: Optional[str] = "Medium"
    weather_event: Optional[str] = None

class ComplaintStatusUpdate(BaseModel):
    status: str  # Open, In Progress, Resolved
    note: Optional[str] = "Status updated"

class ComplaintHistoryOut(BaseModel):
    id: str
    complaint_id: str
    actor_id: str
    from_status: str
    to_status: str
    note: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class ComplaintOut(BaseModel):
    id: str
    resident_id: str
    apartment_id: Optional[str]
    category: str
    description: str
    photo_url: Optional[str]
    priority: str
    status: str
    weather_event: Optional[str]
    created_at: datetime
    history: List[ComplaintHistoryOut] = []
    overdue_risk_score: Optional[float] = 0.0

    class Config:
        from_attributes = True

# --- Notice Schemas ---
class NoticeCreate(BaseModel):
    title: str
    body: str
    is_important: bool = False

class NoticeOut(BaseModel):
    id: str
    admin_id: str
    title: str
    body: str
    is_important: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Emergent Pattern Schemas ---
class PatternOut(BaseModel):
    id: str
    name: str
    description: str
    strength_score: float
    cohesion: float
    size: float
    category_spread: float
    temporal_concentration: float
    complaint_ids: List[str]
    label_source: str
    detected_at: datetime
    status: str
    complaints: List[ComplaintOut] = []

    class Config:
        from_attributes = True

class PatternDetectResponse(BaseModel):
    detected_count: int
    patterns: List[PatternOut]
    message: str

# --- Dashboard Schemas ---
class DashboardOut(BaseModel):
    total_complaints: int
    open_count: int
    in_progress_count: int
    resolved_count: int
    overdue_count: int
    detected_patterns_count: int
    by_category: dict
    top_overdue: List[ComplaintOut]
