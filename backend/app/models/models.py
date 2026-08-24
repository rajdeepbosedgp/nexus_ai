import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Apartment(Base):
    __tablename__ = "apartments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    building: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_number: Mapped[str] = mapped_column(String(20), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="apartment")
    complaints: Mapped[list["Complaint"]] = relationship("Complaint", back_populates="apartment")

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="resident")
    apartment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("apartments.id"), nullable=True)

    apartment: Mapped[Apartment | None] = relationship("Apartment", back_populates="users")
    complaints: Mapped[list["Complaint"]] = relationship("Complaint", back_populates="resident")
    notices: Mapped[list["Notice"]] = relationship("Notice", back_populates="admin")

class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    resident_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    apartment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("apartments.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    status: Mapped[str] = mapped_column(String(20), default="Open")
    weather_event: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    resident: Mapped[User] = relationship("User", back_populates="complaints")
    apartment: Mapped[Apartment | None] = relationship("Apartment", back_populates="complaints")
    history: Mapped[list["ComplaintHistory"]] = relationship("ComplaintHistory", back_populates="complaint", cascade="all, delete-orphan")

class ComplaintHistory(Base):
    __tablename__ = "complaint_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    from_status: Mapped[str] = mapped_column(String(20), nullable=False)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="history")
    actor: Mapped[User] = relationship("User")

class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    admin_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    admin: Mapped[User] = relationship("User", back_populates="notices")

class Pattern(Base):
    __tablename__ = "patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    strength_score: Mapped[float] = mapped_column(Float, nullable=False)
    cohesion: Mapped[float] = mapped_column(Float, nullable=False)
    size: Mapped[float] = mapped_column(Float, nullable=False)
    category_spread: Mapped[float] = mapped_column(Float, nullable=False)
    temporal_concentration: Mapped[float] = mapped_column(Float, nullable=False)
    complaint_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    label_source: Mapped[str] = mapped_column(String(20), default="llm")
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(20), default="Active")
