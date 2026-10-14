from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentRead
from app.services.workflow_service import publish_student_event

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A student with this email already exists")
    publish_student_event(db, "student.created", student.id, {"id": student.id, "name": student.name, "course": student.course, "date_of_birth": student.date_of_birth})
    return student
