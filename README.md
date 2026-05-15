Project Management MVP

Quick start

1) Backend (FastAPI)
- Create a `.env` file at project root (copy `.env.example`) and set `OPENROUTER_API_KEY` if you want to test AI calls.
- Activate the Python virtualenv in `backend/.venv` or use the same Python environment used during development.

Run backend tests:

    ./backend/.venv/bin/python -m unittest backend.test_db backend.test_main -v

Run the backend server for manual testing:

    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

The backend exposes:
- `GET /api/ping` — health
- `POST /api/auth/login` — demo login (`user` / `password`)
- `POST /api/auth/logout`
- `GET /api/kanban` — returns user's board
- `POST /api/kanban` — update board
- `POST /api/ai/ping` — simple AI connectivity check
- `POST /api/ai/chat` — structured AI chat that may return `kanbanUpdate`

2) Frontend (Next.js)

Install dependencies and run unit tests:

    cd frontend
    npm install
    npm run test:unit

Run dev server:

    npm run dev

Notes
- Use `.env.example` to create a `.env` with `OPENROUTER_API_KEY` for real AI calls. Without it, AI chat tests are mocked.
- Frontend sign-in uses demo credentials and also posts to `/api/auth/login` so backend cookie-based auth works during manual testing.
- Playwright E2E tests for the AI chat flow are not added yet; recommended as a follow-up.

Contact
- If anything fails, run the backend tests first, fix errors, then run frontend tests.
