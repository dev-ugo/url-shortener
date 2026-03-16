# url-shortener

A minimalist URL shortener with a web interface.  
Paste a long URL, get a short one.

## Stack

| Layer | Tool |
|---|---|
| Backend | Python · FastAPI |
| Database | SQLite |
| Frontend | HTML / CSS / JS |
| Infra | Docker |

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- No external dependencies, no API key required

## Getting started

```bash
git clone <repo-url>
cd url-shortener
docker compose up --build
```

Open **http://localhost:8000**

## Usage

1. **Paste a URL** into the input field
2. **Click "Raccourcir"** — a short link is generated instantly
3. **Copy the link** using the button, or click it to be redirected
4. **Delete a link** by hovering over it and clicking ✕

> Data is kept as long as the container is running.  
> A restart starts fresh with an empty database.

## Project structure

```
url-shortener/
├── docker-compose.yml      # Service orchestration
├── data/                   # SQLite database (auto-generated)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py             # FastAPI app
└── frontend/
    └── index.html          # Web interface
```

## API

| Method | Route | Description |
|---|---|---|
| `POST` | `/links` | Create a short link |
| `GET` | `/{slug}` | Redirect to original URL |
| `GET` | `/links` | List all links |
| `DELETE` | `/links/{slug}` | Delete a link |

**Example**
```bash
curl -X POST http://localhost:8000/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/a-very-long-url"}'
```

```json
{
  "slug": "aB3x9z",
  "original_url": "https://example.com/a-very-long-url",
  "short_url": "http://localhost:8000/aB3x9z",
  "created_at": "2026-03-16T09:00:00"
}
```
## Stop

```bash
docker compose down
```