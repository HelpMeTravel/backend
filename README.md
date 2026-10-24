# HelpMeTravel Backend

FastAPI backend with PostgreSQL, running in Docker.

## Prerequisites

* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Quickstart

### 1. Clone the repository
```bash
git clone git@github.com:HelpMeTravel/backend.git
cd backend
```

### 2. Set up environment variables
Create a `.env` file in the root folder (next to `docker-compose.yml`):

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=helpmetravel_db
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/helpmetravel_db
SECRET_KEY=secretjwtkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Run the app
```bash
docker compose up --build
```

---

## Endpoints & Docs

Once the containers are up:

* **Swagger API Docs:** http://localhost:8000/docs
* **Health Check:** http://localhost:8000/app/health

---

## Useful Commands

* **Stop containers:**
  ```bash
  docker compose down
  ```

* **Reset database and wipe data:**
  ```bash
  docker compose down -v
  ```