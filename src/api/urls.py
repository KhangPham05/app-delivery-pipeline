import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import Url
from src.db.session import get_db
from src.schemas.url import UrlCreate, UrlOut

router = APIRouter()

SHORT_CODE_LENGTH = 6
SHORT_CODE_ALPHABET = string.ascii_letters + string.digits
MAX_SHORT_CODE_ATTEMPTS = 5


def _generate_short_code() -> str:
    return "".join(secrets.choice(SHORT_CODE_ALPHABET) for _ in range(SHORT_CODE_LENGTH))


@router.get("/urls", response_model=list[UrlOut])
def list_urls(db: Session = Depends(get_db)):
    return db.query(Url).order_by(Url.created_at.desc()).all()


@router.post("/urls", response_model=UrlOut, status_code=status.HTTP_201_CREATED)
def create_url(payload: UrlCreate, db: Session = Depends(get_db)):
    # Rely on the DB's unique constraint to catch collisions rather than
    # check-then-insert, which would race under concurrent requests.
    for attempt in range(MAX_SHORT_CODE_ATTEMPTS):
        url = Url(short_code=_generate_short_code(), original_url=str(payload.original_url))
        db.add(url)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(url)
        return url

    raise HTTPException(status_code=500, detail="Could not generate a unique short code")
