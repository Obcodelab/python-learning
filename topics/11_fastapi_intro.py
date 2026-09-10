"""FastAPI introduction.

Routing, request/response models with Pydantic, and the automatic docs.

Run it:
    uv run uvicorn topics.11_fastapi_intro:app --reload

Then open:
    http://127.0.0.1:8000/docs      interactive documentation
    http://127.0.0.1:8000/notes     the GET endpoint below
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Practice API")

# A tiny in-memory store so the example needs no database.
_notes: dict[int, str] = {1: "embeddings turn text into vectors"}
_next_id = 2


class NoteIn(BaseModel):
    """Request body. FastAPI validates incoming JSON against this."""

    text: str = Field(min_length=1, max_length=280)


class NoteOut(BaseModel):
    """Response body."""

    id: int
    text: str


@app.get("/notes", response_model=list[NoteOut])
def list_notes() -> list[NoteOut]:
    return [NoteOut(id=i, text=t) for i, t in _notes.items()]


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int) -> NoteOut:
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut(id=note_id, text=_notes[note_id])


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteIn) -> NoteOut:
    global _next_id
    note_id = _next_id
    _notes[note_id] = note.text
    _next_id += 1
    return NoteOut(id=note_id, text=note.text)
