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

> SQLite data is persisted in `./data/links.db` through the Docker volume `./data:/app/data`.

## Project structure

```
url-shortener/
├── .github/
│   └── workflows/
│       └── security.yml    # CI security checks (gitleaks, pip-audit, bandit)
├── Dockerfile              
├── docker-compose.yml      
├── requirements.txt        
├── data/                   # SQLite database folder (auto-generated)
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── main.py             
│   ├── models.py
│   ├── schemas.py
│   └── services.py
└── frontend/
    ├── index.html          
    ├── styles.css          
    └── app.js              
```

## Frontend assets

- `GET /` serves `frontend/index.html`
- Static files are served from `frontend/` under `/static`
  - `/static/styles.css`
  - `/static/app.js`

## API

| Method | Route | Description |
|---|---|---|
| `POST` | `/links` | Create a short link |
| `GET` | `/{slug}` | Redirect to original URL |
| `GET` | `/links` | List all links |
| `DELETE` | `/links/{slug}` | Delete a link |

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