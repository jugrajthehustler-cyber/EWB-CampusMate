import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WorkflowEvent

router = APIRouter(prefix="/workflow", tags=["Workflow automation"])


@router.get("/events")
def list_workflow_events(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
    events = db.scalars(select(WorkflowEvent).order_by(WorkflowEvent.id.desc()).limit(limit)).all()
    return [
        {"id": event.id, "event_type": event.event_type, "student_id": event.student_id,
         "payload": json.loads(event.payload_json), "delivery_status": event.delivery_status,
         "created_at": event.created_at}
        for event in events
    ]
