# LinkVault API

The backend for [LinkVault](https://linkvault-web-nine.vercel.app) — a bookmarks manager with auto-fetched favicons, search, sorting, favorites, and password reset.

**Live frontend:** https://linkvault-web-nine.vercel.app
**Live API health check:** https://linkvault-api-fbdv.onrender.com/health
**API docs (Swagger):** https://linkvault-api-fbdv.onrender.com/docs

> Note: the API runs on Render's free tier, which spins down after inactivity. The first request after idle time may take up to 50 seconds to respond.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (hosted on Neon)
- **ORM / Migrations:** SQLAlchemy + Alembic
- **Auth:** JWT (access + refresh tokens), bcrypt password hashing
- **Email:** Resend (password reset)
- **Testing:** pytest, pytest-cov (97% coverage)
- **Linting:** ruff
- **CI:** GitHub Actions (lint + test on every push)
- **Containerization:** Docker

## Features

- User registration, login, and JWT-based auth with automatic token refresh
- Full bookmarks CRUD: create, list, update (rename / favorite), delete
- Search bookmarks by name or link (case-insensitive)
- Sort by date added or alphabetically
- Duplicate-link detection per user
- Auto-fetched favicons via Google's favicon service
- Password reset via email (Resend)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Log in, returns access + refresh tokens |
| POST | `/auth/refresh` | Exchange a refresh token for a new token pair |
| POST | `/auth/forgot-password` | Request a password reset email |
| POST | `/auth/reset-password` | Reset password using a token |
| GET | `/bookmarks` | List bookmarks (supports `search`, `sort` query params) |
| POST | `/bookmarks` | Create a bookmark |
| PATCH | `/bookmarks/{id}` | Update a bookmark (name / favorite status) |
| DELETE | `/bookmarks/{id}` | Delete a bookmark |
| GET | `/health` | Health check |

Full interactive docs available at [`/docs`](https://linkvault-api-fbdv.onrender.com/docs).

## Local Setup

```bash
git clone https://github.com/davidtiger3622/linkvault-api.git
cd linkvault-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in your DATABASE_URL, SECRET_KEY, RESEND_API_KEY, etc. in .env
alembic upgrade head
uvicorn app.main:app --reload
```

Or with Docker:
```bash
docker compose up
```

Run tests:
```bash
pytest --cov=app --cov-report=term-missing -v
```

## License

MIT — see [LICENSE](LICENSE).
