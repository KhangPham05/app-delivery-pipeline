import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import Click, Url
from src.db.session import get_db
from src.schemas.url import UrlCreate, UrlOut, UrlStats

router = APIRouter()

SHORT_CODE_LENGTH = 6
SHORT_CODE_ALPHABET = string.ascii_letters + string.digits
MAX_SHORT_CODE_ATTEMPTS = 5
RECENT_CLICKS_LIMIT = 10


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


@router.get("/urls/{short_code}/stats", response_model=UrlStats)
def get_url_stats(
    short_code: str = Path(min_length=6, max_length=6),
    db: Session = Depends(get_db),
):
    url = db.query(Url).filter(Url.short_code == short_code).first()
    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    total_clicks = db.query(func.count(Click.id)).filter(Click.url_id == url.id).scalar()

    recent_clicks = (
        db.query(Click.clicked_at)
        .filter(Click.url_id == url.id)
        .order_by(Click.clicked_at.desc())
        .limit(RECENT_CLICKS_LIMIT)
        .all()
    )

    return UrlStats(
        short_code=url.short_code,
        total_clicks=total_clicks,
        recent_clicks=[clicked_at for (clicked_at,) in recent_clicks],
    )


# Kept as the last route in this router: a bare {short_code} path is a
# catch-all for any single path segment, so it must never be registered
# ahead of more specific routes (see app.include_router order in main.py).
@router.get("/{short_code}")
def redirect_to_original(
    short_code: str = Path(min_length=6, max_length=6),
    db: Session = Depends(get_db),
):
    url = db.query(Url).filter(Url.short_code == short_code).first()
    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    db.add(Click(url_id=url.id))
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_302_FOUND)
