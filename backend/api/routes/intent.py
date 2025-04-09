from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
import uuid
from sqlalchemy.orm import Session
from database.database import SessionLocal
from models import Intent, DataProduct

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/intent")
async def create_intent(intent_name: str = Form(...), problem: str = Form(...), data_product: str = Form(...),
                        workflows: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """Creates an intent object and saves it to the database."""

    # Fetch the related data product
    data_product = db.query(DataProduct).filter(DataProduct.name == data_product).first()
    if not data_product:
        raise HTTPException(status_code=404, detail="Data product not found!")

    intent = Intent(
        name=intent_name,
        problem=problem,
        data_product_name=data_product.name,
        # workflows=workflows
    )

    db.add(intent)
    db.commit()

    return JSONResponse(status_code=200, content={
        "message": "Intent created successfully",
        "intent_name": intent_name
    })


@router.get("/intents")
async def get_intents(db: Session = Depends(get_db)):
    """Retrieves all stored intents."""
    intents = db.query(Intent).all()
    return JSONResponse(status_code=200, content={"intents": [intent.to_dict() for intent in intents]})


@router.delete("/intent/{intent_name}")
async def delete_intent(intent_name: str, db: Session = Depends(get_db)):
    """Deletes an intent by its ID."""

    # Fetch the intent by ID
    intent = db.query(Intent).filter(Intent.name == intent_name).first()

    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found!")

    # Delete the intent
    db.delete(intent)
    db.commit()

    return JSONResponse(status_code=200, content={
        "message": f"Intent with ID {intent_name} deleted successfully"
    })
