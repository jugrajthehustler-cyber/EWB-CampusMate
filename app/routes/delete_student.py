from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.services.workflow_service import publish_student_event

router = APIRouter(prefix="/students", tags=["Students"])


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)) -> Response:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    snapshot = {"id": student.id, "name": student.name, "course": student.course, "date_of_birth": student.date_of_birth}
    db.delete(student)
    db.commit()
    publish_student_event(db, "student.deleted", student_id, snapshot)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
