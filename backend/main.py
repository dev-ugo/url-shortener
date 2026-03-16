"""FastAPI entrypoint and HTTP routes."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from database import create_tables, engine
from models import Link
from schemas import LinkCreate, LinkRead
from services import get_link_by_slug, get_or_create_link, to_link_read

app = FastAPI(title="URL Shortener")

@app.on_event("startup")
def on_startup():
    """Initialize database schema at application startup."""

    create_tables()

@app.post("/links", response_model=LinkRead, status_code=201)
def create_link(body: LinkCreate):
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
def delete_link(slug: str):
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