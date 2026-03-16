"""Business logic helpers for URL management."""

import random
import string

import validators
from fastapi import HTTPException
from sqlmodel import Session, select

from config import BASE_URL, SLUG_LENGTH
from models import Link
from schemas import LinkRead


def generate_slug() -> str:
    """Generate a random alphanumeric slug."""

    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=SLUG_LENGTH))


def unique_slug(session: Session) -> str:
    """Return a unique slug, or fail after several attempts."""

    for _ in range(10):
        slug = generate_slug()
        if not session.exec(select(Link).where(Link.slug == slug)).first():
            return slug
    raise HTTPException(500, "Impossible de generer un slug unique.")


def to_link_read(link: Link) -> LinkRead:
    """Convert a Link model to API response schema."""

    return LinkRead(
        slug=link.slug,
        original_url=link.original_url,
        short_url=f"{BASE_URL}/{link.slug}",
        created_at=link.created_at,
    )


def get_or_create_link(session: Session, original_url: str) -> Link:
    """Validate URL and return existing link or create a new one."""

    if not validators.url(original_url):
        raise HTTPException(422, "URL invalide.")

    existing = session.exec(select(Link).where(Link.original_url == original_url)).first()
    if existing:
        return existing

    slug = unique_slug(session)
    link = Link(slug=slug, original_url=original_url)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def get_link_by_slug(session: Session, slug: str) -> Link:
    """Fetch a link by slug or raise 404 if missing."""

    link = session.exec(select(Link).where(Link.slug == slug)).first()
    if not link:
        raise HTTPException(404, "Lien introuvable.")
    return link
