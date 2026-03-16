"""Business logic helpers for URL management."""
import ipaddress
import random
import secrets
import socket
import string
from urllib.parse import urlparse

import validators
from fastapi import HTTPException
from sqlmodel import Session, select

from config import BASE_URL, SLUG_LENGTH
from models import Link
from schemas import LinkRead

def generate_slug() -> str:
    """Generate a cryptographically secure random alphanumeric slug."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(SLUG_LENGTH))


def unique_slug(session: Session) -> str:
    """Return a unique slug, or fail after several attempts."""
    for _ in range(10):
        slug = generate_slug()
        if not session.exec(select(Link).where(Link.slug == slug)).first():
            return slug
    raise HTTPException(500, "Impossible de generer un slug unique.")

PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),       
    ipaddress.ip_network("169.254.0.0/16"),    
    ipaddress.ip_network("::1/128"),           
    ipaddress.ip_network("fc00::/7"),          
]

def is_private_ip(hostname: str) -> bool:
    """Return True if the hostname resolves to a private/internal IP."""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        return any(ip in network for network in PRIVATE_NETWORKS)
    except (socket.gaierror, ValueError):
        return True  

def check_ssrf(url: str) -> None:
    """Raise 422 if the URL targets an internal or private address."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(422, "Seules les URLs http/https sont acceptées.")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(422, "URL invalide.")

    if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise HTTPException(422, "URL non autorisée.")

    if is_private_ip(hostname):
        raise HTTPException(422, "URL non autorisée.")

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

    check_ssrf(original_url)

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