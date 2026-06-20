# Deployment Plan: Railway (Backend) & Vercel (Frontend)

This document outlines the steps required to deploy the Fotmob Pulse architecture into production. The system is split into two parts: the FastAPI python backend (deployed on Railway) and the React/Vite frontend (deployed on Vercel).

## Phase 1: Backend Deployment (Railway)

The backend handles the data ingestion, AI clustering (via Groq), and communicating with your MCP Server.

### 1. Preparation
- **Requirements**: Railway automatically detects Python projects using `pyproject.toml` or `requirements.txt`.
- **Start Command**: We need to tell Railway how to start the FastAPI server.
  - Create a `railway.toml` file in the root of your repository with the following content:
    ```toml
    [build]
    builder = "nixpacks"

    [deploy]
    startCommand = "PYTHONPATH=src uvicorn pulse.api:app --host 0.0.0.0 --port $PORT"
    ```

### 2. Deployment Steps
1. Push your latest code to your GitHub repository.
2. Go to your **Railway Dashboard** and click **New Project** -> **Deploy from GitHub repo**.
3. Select the repository containing the Fotmob project.
4. Railway will automatically build the environment.
5. Go to the **Variables** tab for the newly created service and add the following keys from your local `.env`:
   - `GROQ_API_KEY`
   - `MCP_SERVER_URL` (Set to `https://web-production-e9833.up.railway.app`)
   - `MCP_API_KEY`
   - `TARGET_DOC_ID`
   - `TARGET_EMAIL`
6. Go to the **Settings** tab -> **Networking** and generate a Public Domain.
   - *Example: `https://fotmob-backend-production.up.railway.app`*

---

## Phase 2: Code Updates for Frontend 

Currently, the React frontend has the backend URL hardcoded to `http://localhost:8000` in `App.jsx`. Before deploying to Vercel, we must update this to use environment variables.

### Required Changes:
1. **Update `App.jsx`**:
   Replace all instances of `http://localhost:8000` with an environment variable:
   ```javascript
   const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
   
   // Example:
   fetch(`${API_BASE_URL}/api/reports`)
   ```
2. **Commit and Push**: Push these changes to GitHub.

---

## Phase 3: Frontend Deployment (Vercel)

The frontend is a static React application built with Vite, which is perfectly suited for Vercel.

### Deployment Steps
1. Go to the **Vercel Dashboard** and click **Add New** -> **Project**.
2. Import your GitHub repository.
3. In the **Configure Project** step, make the following critical adjustments:
   - **Root Directory**: Click "Edit" and select the `frontend` folder. *(This tells Vercel to ignore the python backend code).*
   - **Framework Preset**: Vercel should auto-detect **Vite**. If not, select it.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand the **Environment Variables** section and add:
   - Name: `VITE_API_URL`
   - Value: The Railway Public Domain you generated in Phase 1 (e.g., `https://fotmob-backend-production.up.railway.app`). **Do not add a trailing slash.**
5. Click **Deploy**.

## Phase 4: Final Verification
1. Visit your Vercel URL (e.g., `https://fotmob-pulse.vercel.app`).
2. Verify that the Dashboard loads the reports successfully (this confirms the Vercel app can talk to the Railway backend).
3. Click the **Create Report** button.
4. Verify that the UI updates, the backend processes the data, and an email/Doc is successfully generated via your existing MCP server.
