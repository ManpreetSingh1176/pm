# Project Plan for Project Management MVP

## Overview
This plan describes the work needed to build the MVP end-to-end, from Docker and backend scaffolding through frontend integration, authentication, persistence, and AI chat. Each part includes substeps, tests, and success criteria.

## Part 1: Plan and Approval

- [ ] Review the existing frontend demo and current repo structure.
- [ ] Document the detailed implementation plan in `docs/PLAN.md`.
- [ ] Keep the root `AGENTS.md` as the authoritative project specification.
- [ ] Confirm that columns are fixed and only rename support is required.
- [ ] Confirm AI chat is implemented as part of the backend/API phase.
- [ ] Confirm local Docker target can use any sensible port and entrypoint.

### Success Criteria
- `docs/PLAN.md` contains a complete implementation roadmap.
- The plan is approved by the user before coding begins.

## Part 2: Scaffolding

- [ ] Create `backend/` with a minimal FastAPI application.
- [ ] Add backend dependency management using `uv` and a `pyproject.toml` or `requirements.txt`.
- [ ] Add `Dockerfile` and supporting container setup in the repo root.
- [ ] Add start/stop helper scripts in `scripts/` for macOS/Linux/Windows.
- [ ] Configure FastAPI to serve static files from the frontend build output at `/`.
- [ ] Add a backend route at `/api/ping` that returns simple JSON.
- [ ] Test building and running the container locally.

### Tests
- Backend unit test verifying `/api/ping` returns expected JSON.
- Manual or automated Docker smoke test confirming static site is served and the API route works.

### Success Criteria
- Container builds successfully.
- `http://localhost:<port>/api/ping` returns a working response.
- `http://localhost:<port>/` serves a placeholder static page.

## Part 3: Frontend Static Build

- [ ] Ensure `frontend/` builds a static Next.js app.
- [ ] Configure Next.js output for static export or compatible build artifacts.
- [ ] Add build scripts in `frontend/package.json` if missing.
- [ ] Confirm the existing Kanban board demo renders correctly from the static build.
- [ ] Add frontend tests for board rendering.

### Tests
- React component tests for `KanbanBoard`, `KanbanColumn`, and `KanbanCard`.
- Integration test verifying the main page renders the board with column headings.

### Success Criteria
- `npm run build` in `frontend/` succeeds.
- Static build artifacts are served by the backend at `/`.
- The demo Kanban board is visible in the browser.

## Part 4: Fake User Sign-In

- [ ] Add a login page or modal to the frontend.
- [ ] Require hardcoded credentials: `user` / `password`.
- [ ] Add logout support.
- [ ] Ensure the Kanban board is only visible after successful login.
- [ ] Keep authentication simple and local.

### Tests
- Unit tests for the login form and auth state logic.
- Integration test verifying unauthenticated users see login.
- Frontend test verifying logout returns to login.

### Success Criteria
- Login works with the hardcoded credentials.
- Invalid credentials fail cleanly.
- Logout returns the user to the login experience.

## Part 5: Database Modeling

- [ ] Propose a simple SQLite schema for user and Kanban storage.
- [ ] Store the Kanban board as JSON in a text or JSON-compatible column.
- [ ] Support a single Kanban board per user.
- [ ] Document the schema and sample data format.
- [ ] Add documentation in `docs/` describing the schema.

### Tests
- Validate schema design with backend tests using SQLite in-memory mode.
- Confirm JSON serialization and deserialization for Kanban state.

### Success Criteria
- A documented schema exists.
- The database is created automatically if missing.
- The schema supports user-specific Kanban persistence.

## Part 6: Backend API Routes

- [ ] Add REST endpoints for Kanban and auth.
  - `POST /api/auth/login` — validates hardcoded credentials and returns session state.
  - `POST /api/auth/logout` — clears auth state.
  - `GET /api/kanban` — returns the current user’s Kanban board.
  - `POST /api/kanban` — updates the current user’s Kanban board.
- [ ] Implement minimal dummy session auth.
- [ ] Persist Kanban payloads to SQLite.
- [ ] Initialize default board data for new users.

### Tests
- Backend unit tests for auth and Kanban routes.
- DB tests confirming read/write of Kanban JSON.
- Integration tests for unauthorized access handling.

### Success Criteria
- Backend supports reading and updating Kanban data.
- DB file is created if absent.
- Dummy auth blocks unauthorized access.

## Part 7: Frontend + Backend Integration

- [ ] Connect the frontend to backend APIs for login and Kanban data.
- [ ] Replace local seed state with API-backed board state.
- [ ] Ensure column rename and card edit persist to backend.
- [ ] Add user-friendly error handling for API failures.

### Tests
- Frontend tests mocking API responses.
- End-to-end test verifying login, board load, edit, and persist flows.
- Backend test confirming saved data is returned after refresh.

### Success Criteria
- The board loads from the backend after login.
- User changes persist across refreshes.
- Errors render clearly to the user.

## Part 8: AI Connectivity

- [ ] Add backend OpenRouter integration.
- [ ] Read `OPENROUTER_API_KEY` from `.env`.
- [ ] Add a route for AI connectivity tests, such as `POST /api/ai/ping`.
- [ ] Validate with a simple prompt like `2+2`.
- [ ] Keep call logic separate from Kanban state logic.

### Tests
- Backend test verifying OpenRouter connectivity.
- Smoke test for a simple model response.

### Success Criteria
- Backend can successfully call OpenRouter.
- AI returns a response to a simple health check.

## Part 9: Structured AI Chat with Board Context

- [ ] Send current Kanban JSON and user question to the AI.
- [ ] Include optional conversation history in the request.
- [ ] Expect Structured Outputs from the model containing:
  - `userMessage`: natural language reply.
  - `kanbanUpdate` (optional): board modifications.
- [ ] Parse the response and apply updates if present.
- [ ] Return the AI message and board changes to the frontend.

### Tests
- Unit tests for AI request building and response parsing.
- Integration test for the AI chat route with mocked OpenRouter.
- Validation that valid structured updates are merged into Kanban state.

### Success Criteria
- AI chat receives board state and prompt correctly.
- Structured updates are applied when provided.
- Backend returns both reply text and optional updates.

## Part 10: AI Chat Sidebar and UI

- [ ] Build a sidebar chat widget in the frontend.
- [ ] Allow users to submit questions and view AI replies.
- [ ] Display any board updates from the AI.
- [ ] Refresh the Kanban board automatically when updates occur.
- [ ] Keep the UI clean and aligned with MVP styling.

### Tests
- Component tests for the chat widget.
- Integration test for send question → backend call → board update.
- Flow test verifying AI reply and board refresh.

### Success Criteria
- The sidebar chat is visible and usable.
- AI replies display clearly.
- Board updates from AI refresh the UI automatically.

## Approval Checklist

- [ ] User approves this plan before implementation begins.
- [ ] After approval, create `frontend/AGENTS.md` documenting the existing frontend code.
- [ ] Track progress by checking off each part in this plan.
