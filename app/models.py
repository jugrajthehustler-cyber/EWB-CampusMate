from datetime import date, datetime
from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(254), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    course: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    student_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    payload_json: Mapped[str] = mapped_column(String(4000), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(40), nullable=False, default="recorded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
