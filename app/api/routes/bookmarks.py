from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.bookmark import Bookmark
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkOut, BookmarkUpdate

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def get_favicon_url(link: str) -> str:
    domain = urlparse(link).netloc or urlparse(f"//{link}").netloc
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


@router.post("", response_model=BookmarkOut, status_code=201)
def create_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Bookmark)
        .filter(Bookmark.owner_id == current_user.id, Bookmark.url == payload.url)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="This link is already saved — try searching for it instead")

    bookmark = Bookmark(
        name=payload.name,
        url=payload.url,
        favicon_url=get_favicon_url(payload.url),
        owner_id=current_user.id,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.get("", response_model=list[BookmarkOut])
def list_bookmarks(
    search: str | None = Query(default=None),
    sort: str = Query(default="date", pattern="^(date|alphabetical)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Bookmark).filter(Bookmark.owner_id == current_user.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Bookmark.name.ilike(pattern), Bookmark.url.ilike(pattern)))

    if sort == "alphabetical":
        query = query.order_by(Bookmark.name.asc())
    else:
        query = query.order_by(Bookmark.created_at.desc())

    return query.all()


@router.patch("/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.owner_id == current_user.id)
        .first()
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if payload.name is not None:
        bookmark.name = payload.name
    if payload.is_favorite is not None:
        bookmark.is_favorite = payload.is_favorite

    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookmark = (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.owner_id == current_user.id)
        .first()
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return None
