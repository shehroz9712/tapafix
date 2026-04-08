cls# Tapafix FastAPI Backend

Production-ready FastAPI with clean architecture, MySQL, JWT auth, BaseController responses.

## Setup

1. Install deps:
```
pip install -r requirements.txt
```

2. Copy & edit env:
```
copy .env.example .env
```
Update DATABASE_URL=mysql+pymysql://root:password@localhost/tapafix_db
Generate SECRET_KEY (openssl rand -hex 32)

3. Init Alembic:
```
alembic init db/migrations
```
Edit `db/migrations/env.py`:
```python
from core.config import settings
import sys
sys.path.append('.')
target_metadata = None  # or Base.metadata
# In run_migrations_online():
connectable = create_engine(settings.DATABASE_URL)
```

4. Migrations:
```
alembic revision --autogenerate -m "users table"
alembic upgrade head
```

5. Run:
```
uvicorn main:app --reload
```

## API
http://localhost:8000/docs

**Auth endpoints:** /auth/register, login, refresh, forgot-password, reset-password, logout

**Users (protected):** /users/{id}, /users/

All responses use BaseController format.
