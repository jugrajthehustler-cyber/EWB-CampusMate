from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import retrieve_facts, maybe_generate_with_ollama

router = APIRouter(prefix="/ai", tags=["AI assistant"])


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AskResponse(BaseModel):
    answer: str
    intent: str
    source_count: int
    ai_used: bool
    note: str | None = None
    facts: dict
    records: list[dict]


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    result = retrieve_facts(db, payload.question)
    answer, ai_used, note = maybe_generate_with_ollama(payload.question, result)
    return AskResponse(
        answer=answer,
        intent=result["kind"],
        source_count=len(result["records"]),
        ai_used=ai_used,
        note=note,
        facts=result["facts"],
        records=result["records"],
    )
