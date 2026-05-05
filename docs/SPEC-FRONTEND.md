🚀 SPEC: Fix Full-Stack Railway Deployment (FastAPI + Static Frontend)
🎯 Objective

Fully repair and validate a full-stack application deployed on Railway where:

FastAPI backend runs correctly
Frontend is served from FastAPI static mount
/ route correctly loads the UI
/api/* routes function normally
No “Application failed to respond” errors occur

The agent must implement, test, and validate all fixes independently.

🧠 CURRENT PROBLEM SUMMARY

The application currently:

Starts successfully with Uvicorn ✔
Fails at runtime when accessed via browser ❌
Likely cause: frontend not being served correctly from frontend/dist
🏗️ PROJECT STRUCTURE (AUTHORITATIVE)
docs/
  backend/
    app/
      main.py   ← FastAPI entrypoint
  frontend/
    dist/       ← REQUIRED production build output
🚨 REQUIRED FIXES
✅ STEP 1 — Fix frontend serving logic

Modify:

docs/backend/app/main.py
Replace function:
def _read_frontend_dir() -> Path:
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    if dist_dir.exists():
        return dist_dir
    return PROJECT_ROOT / "frontend"
With:
def _read_frontend_dir() -> Path:
    return PROJECT_ROOT / "frontend" / "dist"
✅ STEP 2 — Ensure frontend build exists

Run:

cd docs
npm install
npm run build

Validate:

docs/frontend/dist/index.html exists

If missing → build is considered FAILED.

✅ STEP 3 — Ensure static mount is correct

Confirm this exists at end of main.py:

app.mount(
    "/",
    StaticFiles(directory=str(_read_frontend_dir()), html=True),
    name="frontend"
)

This must be the LAST route registered.

✅ STEP 4 — Add diagnostic endpoints

Add BEFORE static mount:

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug/frontend-path")
def debug_frontend():
    return {"path": str(_read_frontend_dir())}
✅ STEP 5 — Validate frontend API usage

Scan frontend code and ensure:

❌ REMOVE:
http://localhost:8000
http://127.0.0.1
✅ REPLACE WITH:
/api/chat
/api/graphs
✅ STEP 6 — Confirm backend start command

Ensure Railway start command is:

uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
🧪 REQUIRED SELF-TESTING (MANDATORY)

After implementing changes, the agent must verify:

✔ Test 1 — Backend health

Request:

GET /health

Expected:

{"status": "ok"}
✔ Test 2 — Frontend mount path

Request:

GET /debug/frontend-path

Expected:

"path": ".../frontend/dist"
✔ Test 3 — Root endpoint

Request:

GET /

Expected:

Returns HTML page (NOT JSON, NOT 404, NOT error page)
✔ Test 4 — API route

Request:

POST /api/chat

Expected:

Valid JSON response OR controlled error (not crash)
🚨 FAILURE CONDITIONS

Mark deployment FAILED if any occur:

/ returns 404 or blank response
frontend directory missing
runtime crash on request
missing dist/ folder
localhost references remain in frontend
uvicorn starts but app is unreachable
🎯 SUCCESS CRITERIA

Deployment is considered SUCCESSFUL only if:

✔ Backend starts without errors
✔ /health returns OK
✔ / serves frontend UI
✔ /api/* endpoints work
✔ No Railway “Application failed to respond” error
✔ Frontend assets load correctly

🧠 AUTONOMOUS REQUIREMENTS

The agent MUST:

Apply fixes without user confirmation
Build frontend if missing
Validate endpoints via HTTP calls
Read logs to confirm runtime behavior
Retry fixes if failure conditions occur
Produce final success/failure report
🚀 FINAL OUTCOME

A fully working full-stack deployment where:

FastAPI handles backend logic
Static frontend is served via /
Railway deployment is stable and production-ready