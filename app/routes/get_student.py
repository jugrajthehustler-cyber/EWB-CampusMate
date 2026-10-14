from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentRead

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=list[StudentRead])
def list_students(
    name: str | None = Query(default=None, max_length=120),
    course: str | None = Query(default=None, max_length=120),
    date_of_birth_after: date | None = None,
    date_of_birth_before: date | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = select(Student)
    if name:
        statement = statement.where(Student.name.ilike(f"%{name}%"))
    if course:
        statement = statement.where(Student.course.ilike(f"%{course}%"))
    if date_of_birth_after:
        statement = statement.where(Student.date_of_birth > date_of_birth_after)
    if date_of_birth_before:
        statement = statement.where(Student.date_of_birth < date_of_birth_before)
    statement = statement.order_by(Student.id).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
