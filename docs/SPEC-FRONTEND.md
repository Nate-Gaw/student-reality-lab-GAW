🚀 SPEC: Fix Frontend Serving for FastAPI App on Railway
🎯 Objective

Ensure the FastAPI backend correctly serves the built frontend so that the deployed app on Railway responds at / without errors.

🧠 Problem Summary

Current state:

Backend (FastAPI) starts successfully ✅
Railway reports “Application failed to respond” ❌
Root cause: frontend is not being served correctly

Key issue:

The app tries to serve frontend/ instead of the built frontend/dist/
In production, only the built static assets should be served
🛠️ REQUIRED CHANGES
✅ 1. Build the frontend

From the docs/ directory:

npm install
npm run build

This must generate:

docs/frontend/dist/index.html
docs/frontend/dist/assets/...
✅ 2. Ensure build output is committed

Verify that dist/ is NOT ignored in .gitignore.

Required:

docs/frontend/dist/

must exist in the repository pushed to Railway.

✅ 3. Update FastAPI static file serving

Modify docs/backend/app/main.py

🔁 Replace this function:
def _read_frontend_dir() -> Path:
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    if dist_dir.exists():
        return dist_dir
    return PROJECT_ROOT / "frontend"
✅ With this:
def _read_frontend_dir() -> Path:
    return PROJECT_ROOT / "frontend" / "dist"
✅ 4. Ensure frontend is mounted correctly

Confirm this line exists at the VERY END of main.py:

app.mount("/", StaticFiles(directory=str(_read_frontend_dir()), html=True), name="frontend")

This must come AFTER all /api/... routes.

✅ 5. Fix frontend API calls (CRITICAL)

Search frontend code (docs/frontend/) for any of:

http://localhost:8000
http://127.0.0.1
❌ Replace with:
/api/chat
/api/graphs

Use relative paths only.

✅ 6. Add temporary debug route (optional but recommended)

Add this ABOVE app.mount:

@app.get("/debug")
def debug():
    return {"frontend_path": str(_read_frontend_dir())}

Used to verify correct path in production.

✅ 7. Verify project root logic

Ensure this line exists and is unchanged:

PROJECT_ROOT = Path(__file__).resolve().parents[2]

This must resolve to:

docs/
✅ 8. Redeploy on Railway

Trigger a fresh deploy after all changes.

🧪 SUCCESS CRITERIA

After deployment:

✅ Backend

Logs show:

Uvicorn running on http://0.0.0.0:$PORT
Application startup complete
✅ Frontend

Visiting:

https://<your-app>.up.railway.app/

loads the UI (NOT an error page)

✅ API

/api/health returns:

{"ok": true}
✅ No Errors
No “Application failed to respond”
No missing JS/CSS errors in browser console
🚨 FAILURE CONDITIONS

If still broken, check:

dist/ folder missing ❌
frontend not built ❌
wrong path in _read_frontend_dir() ❌
frontend still using localhost ❌
🎯 FINAL RESULT
FastAPI serves API at /api/...
Frontend loads at /
Full-stack app runs entirely on Railway