# CareerGenie AI

CareerGenie AI is a React/Vite career command center backed by FastAPI, SQLAlchemy, JWT authentication, and a SQLite/PostgreSQL-compatible data layer. The current release includes authenticated login, seeded opportunities across internships, fellowships, hackathons, and scholarships, search/filtering, a dashboard, application tracking, and profile editing.

## Local installation

Requirements: Node.js 20+, Python 3.12+, and Git.

```powershell
npm install
py -3.12 -m pip install -r backend\requirements.txt
copy backend\.env.example backend\.env
npm run dev
```

In a second terminal:

```powershell
py -3.12 -m uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:5173` (or the port printed by Vite). API docs are available at `http://localhost:8000/docs`. Demo login: `alex@example.com` / `career123`.

## Configuration

The backend defaults to `sqlite:///./careergenie.db` for local development. For Supabase, set `DATABASE_URL` to a SQLAlchemy URL such as `postgresql+psycopg://...` and set a strong `JWT_SECRET`. Set `CORS_ORIGINS` to a comma-separated list of deployed frontend URLs. The frontend reads `VITE_API_URL` from its environment.

## Deploy

### Vercel

Import the repository into Vercel, use the detected Vite settings, and set `VITE_API_URL` to the deployed Render API URL plus `/api`. `vercel.json` provides SPA fallback routing.

### Render

Use the included `render.yaml` Blueprint or create a Python web service with `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Configure `DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS` in Render environment variables. Supabase provides the PostgreSQL connection string.

## API surface

- `POST /api/auth/signup` and `POST /api/auth/login`
- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/opportunities?q=&category=`
- `GET/POST /api/profile`
- `GET/POST /api/applications`
- Interactive OpenAPI docs at `/docs`

## Validation

```powershell
npm run build
py -3.12 -m py_compile backend\main.py backend\db.py backend\models.py backend\schemas.py backend\security.py
```

External Vercel, Render, Supabase, Gemini, Cloudinary, SMTP, and GitHub operations require account credentials and project secrets; placeholders are intentionally not committed.
