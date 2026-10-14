from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentRead, StudentUpdate
from app.services.workflow_service import publish_student_event

router = APIRouter(prefix="/students", tags=["Students"])


def _save(db: Session, student: Student):
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A student with this email already exists")
    return student


@router.put("/{student_id}", response_model=StudentRead)
def replace_student(student_id: int, payload: StudentCreate, db: Session = Depends(get_db)):
    """Replace all editable student fields; identity and creation timestamp are preserved."""
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in payload.model_dump().items():
        setattr(student, field, value)
    saved = _save(db, student)
    publish_student_event(db, "student.updated", saved.id, {"id": saved.id, "name": saved.name, "course": saved.course, "date_of_birth": saved.date_of_birth})
    return saved


@router.patch("/{student_id}", response_model=StudentRead)
def patch_student(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")
    proposed_email = updates.get("email", student.email)
    proposed_phone = updates.get("phone", student.phone)
    if not proposed_email and not proposed_phone:
        raise HTTPException(status_code=422, detail="A student must have an email address or phone number")
    for field, value in updates.items():
        if hasattr(value, "__str__") and field == "email" and value is not None:
            value = str(value)
        setattr(student, field, value)
    saved = _save(db, student)
    publish_student_event(db, "student.updated", saved.id, {"id": saved.id, "name": saved.name, "course": saved.course, "date_of_birth": saved.date_of_birth})
    return saved
