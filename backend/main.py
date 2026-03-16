"""FastAPI entrypoint and HTTP routes."""

import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select

from config import DELETE_API_KEY
from database import create_tables, engine
from models import Link
from schemas import LinkCreate, LinkRead
from services import get_link_by_slug, get_or_create_link, to_link_read


def get_client_ip(request: Request) -> str:
    """Return client IP, preferring X-Forwarded-For when behind a proxy."""

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def verify_delete_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Authorize delete operations using a shared secret header."""

    if not DELETE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DELETE_API_KEY is not configured on the server.",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, DELETE_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key.")

app = FastAPI(title="URL Shortener")
limiter = Limiter(key_func=get_client_ip)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def on_startup():
    """Initialize database schema at application startup."""

    create_tables()

@app.post("/links", response_model=LinkRead, status_code=201)
@limiter.limit("10/minute")
def create_link(request: Request, body: LinkCreate):
    """Create a short link or return existing one for the same URL."""

    with Session(engine) as session:
        link = get_or_create_link(session, body.url)
    return to_link_read(link)


@app.get("/links", response_model=list[LinkRead])
def list_links():
    """List stored links from newest to oldest."""

    with Session(engine) as session:
        links = session.exec(select(Link).order_by(Link.created_at.desc())).all()
    return [to_link_read(link) for link in links]


@app.delete("/links/{slug}", status_code=204)
def delete_link(slug: str, _: None = Depends(verify_delete_api_key)):
    """Delete a stored link by slug."""

    with Session(engine) as session:
        link = get_link_by_slug(session, slug)
        session.delete(link)
        session.commit()


@app.get("/{slug}")
def redirect(slug: str):
    """Redirect to the original URL associated with a slug."""

    with Session(engine) as session:
        link = get_link_by_slug(session, slug)
    return RedirectResponse(url=link.original_url, status_code=302)

app.mount("/", StaticFiles(directory="/app/frontend", html=True), name="frontend")