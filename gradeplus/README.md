# GradeAtlas Backend (Production-ready)

This repository contains the GradeAtlas Flask backend, upgraded for production deployment.

## Quick start (local)

1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # PowerShell: venv\Scripts\Activate.ps1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update values

```bash
cp .env.example .env
```

4. Initialize database migrations

```bash
set FLASK_APP=app.py        # Windows PowerShell
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run locally

```bash
python app.py
```

## Deployment

- Use `gunicorn wsgi:app` or the provided `Procfile` for Render/Railway.
- Ensure environment variables from `.env` are set in the deployment platform.
- For production use PostgreSQL and configure `DATABASE_URL` accordingly.

## Notes

- Authentication uses JWT access + refresh tokens.
- Rate limiting, caching (Redis optional), and migrations are supported.
- Do NOT commit `.env` with secrets.

