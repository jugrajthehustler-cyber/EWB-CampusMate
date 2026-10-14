from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Student

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Student)) or 0
    course_rows = db.execute(
        select(Student.course, func.count(Student.id)).group_by(Student.course).order_by(Student.course)
    ).all()
    course_counts = {course or "Not specified": count for course, count in course_rows}
    return {"total_students": total, "course_counts": course_counts}
