# EPAM Project API

Production-style asynchronous FastAPI backend with PostgreSQL, Redis, SQLAlchemy
2.0, Alembic, JWT authentication, Argon2 password hashing, and
`dependency-injector`.

## Implemented data model

- `User`: UUID identity, normalized unique email, Argon2 password hash, names,
  and timezone-aware timestamps.
- `Project`: UUID identity, owner relationship, many-to-many members, description,
  and timestamps.
- `Document`: UUID identity, file reference, and project relationship.

`Document.file_path` stores a path or future object-storage key. SQLAlchemy does
not have Django's `FileField`, and an `UploadFile` object must not be stored in a
database column.

## Authentication endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/register` | Register a user and hash the password |
| `POST` | `/login` | Return a 1-hour access token and 1-day refresh token |
| `POST` | `/refresh` | Rotate a valid refresh token |
| `POST` | `/password_reset` | Consume a short-lived, single-use reset token |
| `POST` | `/change_password` | Change password using an access token and current password |
| `GET` | `/health` | Liveness check |

Email delivery and the public password-reset request endpoint are intentionally
deferred. The existing `/password_reset` endpoint only consumes a reset token;
it never resets a password from an email address alone.

## Local setup

Install Python and dependencies:

```bash
uv python install 3.12
uv sync --all-groups
cp .env.example .env
```

Replace `JWT_SECRET_KEY` in `.env` with a secure random value:

```bash
openssl rand -hex 32
```

Start PostgreSQL and Redis:

```bash
docker compose -f deploy/docker/compose.yaml up -d postgres redis
```

Apply the migration:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Open Swagger UI at <http://127.0.0.1:8000/docs> and test the endpoints.

## Test and quality commands

```bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy app
```

## Password-reset testing before email delivery

The reset-token issuance method is internal: `AuthService.issue_password_reset_token`.
The automated API test demonstrates issuance and consumption without exposing a
dangerous public endpoint that returns reset tokens. When email is added, a public
request endpoint should always return a generic response and deliver the token only
through the verified email channel.
