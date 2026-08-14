from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.models import Url
from src.db.session import get_db
from src.schemas.url import UrlOut

router = APIRouter()


@router.get("/urls", response_model=list[UrlOut])
def list_urls(db: Session = Depends(get_db)):
    return db.query(Url).order_by(Url.created_at.desc()).all()
