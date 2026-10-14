import json
import logging
from datetime import date, datetime, timezone
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import WorkflowEvent

logger = logging.getLogger(__name__)


def publish_student_event(db: Session, event_type: str, student_id: int | None, student_data: dict) -> WorkflowEvent:
    """Persist an event, then optionally POST it to a configured n8n webhook.

    Webhook failure is recorded and does not roll back the student CRUD operation.
    Only minimal fields are included in the webhook payload.
    """
    safe_data = {}
    for key, value in student_data.items():
        if key in {"id", "name", "course", "date_of_birth"}:
            safe_data[key] = value.isoformat() if isinstance(value, (date, datetime)) else value
    payload = {"event_type": event_type, "student_id": student_id, "student": safe_data, "occurred_at": datetime.now(timezone.utc).isoformat()}
    event = WorkflowEvent(
        event_type=event_type,
        student_id=student_id,
        payload_json=json.dumps(payload, ensure_ascii=False),
        delivery_status="recorded",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    if settings.n8n_webhook_url:
        try:
            response = httpx.post(settings.n8n_webhook_url, json=payload, timeout=3.0)
            response.raise_for_status()
            event.delivery_status = "delivered"
        except Exception as exc:
            logger.warning("Could not deliver n8n webhook: %s", type(exc).__name__)
            event.delivery_status = "delivery_failed"
        db.add(event)
        db.commit()
        db.refresh(event)
    return event
