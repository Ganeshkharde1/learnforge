# Deploying LearnForge AI to Google Cloud Run via GitHub

LearnForge AI is structured as a monorepo containing a FastAPI backend and a React (Vite) frontend. To deploy this to Google Cloud Run via GitHub Continuous Deployment, you will create **two separate Cloud Run services**: one pointing to the `backend/` folder and one pointing to the `frontend/` folder.

Both folders have production-ready `Dockerfile` configurations designed specifically for Cloud Run.

---

## 🏗️ 1. Preparing the Repository

Before deploying, ensure your code is pushed to your GitHub repository.

1. **GitHub Repository**: Push all your LearnForge code to a GitHub repo.
2. **`.gitignore`**: We have already generated a proper `.gitignore` file that excludes `node_modules`, Python caches, and the local `data/` and `service-account.json` files so your repository stays secure and lean.

---

## ⚙️ 2. Deploying the Backend

Deploy the backend first so you have an API URL to give to the frontend.

1. Open the **Google Cloud Console** and navigate to **Cloud Run**.
2. Click **Create Service**.
3. Select **Continuously deploy new revisions from a source repository** and click **Set up with Cloud Build**.
4. Connect your GitHub account and select your LearnForge repository.
5. In the Build Configuration:
   - **Branch**: `main` (or whichever branch you use)
   - **Build Type**: `Dockerfile`
   - **Source location**: `/backend/Dockerfile` *(crucial: specify the backend folder!)*
6. In the **Service Settings**:
   - **Service name**: `learnforge-backend`
   - **Region**: e.g., `us-central1`
   - **Authentication**: Allow unauthenticated invocations (so the frontend can reach it).
7. Under **Container, Connections, Security**:
   - **Variables & Secrets**: Add your environment variables here.
     - Add `GCP_PROJECT_ID`
     - Add `VERTEX_LOCATION`
     - Mount your `LEARNFORGE_CREDENTIALS` secret to `GOOGLE_CREDENTIALS_JSON` (as per the main README).
8. Click **Create**. Wait for the build to finish. Cloud Run will give you a backend URL (e.g., `https://learnforge-backend-xyz.a.run.app`).

---

## 🌐 3. Updating CORS (Code Change Required)

Now that you have your backend deployed, but *before* you deploy the frontend, you must tell the backend to accept requests from your future frontend URL. 

However, since Cloud Run generates the frontend URL *after* deployment, you can either:
A) Use a wildcard `*` for `ALLOWED_ORIGINS` temporarily (easiest for hackathons).
B) Or deploy the frontend once, get the URL, then update the backend `.env` and redeploy.

To use the wildcard (recommended for hackathon speed):
1. Open `backend/app/config.py`.
2. Change the `ALLOWED_ORIGINS` array to: `ALLOWED_ORIGINS: List[str] = ["*"]`.
3. Push to GitHub (Cloud Run will automatically redeploy the backend).

---

## 🎨 4. Deploying the Frontend

The frontend uses a multi-stage Docker build. It first compiles the React app using Node, then serves the static files using Nginx.

1. Go back to **Cloud Run** and click **Create Service** again.
2. Set up continuous deployment from the same GitHub repository.
3. In the Build Configuration:
   - **Branch**: `main`
   - **Build Type**: `Dockerfile`
   - **Source location**: `/frontend/Dockerfile` *(crucial: specify the frontend folder!)*
4. In the **Service Settings**:
   - **Service name**: `learnforge-frontend`
   - **Authentication**: Allow unauthenticated invocations.
5. Under **Variables & Secrets**, you MUST add a Build Variable (not a runtime variable!):
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://learnforge-backend-xyz.a.run.app/api/v1` *(The backend URL you got in Step 2!)*
   - *Note: In Cloud Run, you can set this under "Environment variables" but ensure your Buildpack/Cloud Build passes it as an ARG. If Cloud Run UI strips ARGs, you may need to commit a `.env.production` file to GitHub with `VITE_API_BASE_URL=...` instead.*
6. Click **Create**.

---

## 🐳 About the Dockerfiles

We have custom-tailored the Dockerfiles to ensure they don't fail in production:

### Backend Dockerfile (`backend/Dockerfile`)
- Uses a **Multi-stage build**: Compiles dependencies in a `builder` container, then moves only the execution binaries to the `runtime` container to keep the image small.
- **LibreOffice & FFmpeg**: Installed natively via `apt-get` to support your background video pipeline generation.
- **Non-root user**: Runs the application under a `learnforge` user for strict security.
- **Volume handling**: Specifically `mkdir` and `chown` for `/app/data` to ensure your local SQLite and Storage implementations don't throw permission errors in the container.

### Frontend Dockerfile (`frontend/Dockerfile`)
- Uses a **Multi-stage build**: Uses Node to run `npm run build`, then completely discards Node.
- **Nginx Alpine**: The final image is a tiny, lightning-fast Nginx web server holding your static files.
- **`nginx.conf`**: We wrote a custom Nginx configuration that implements React Router fallback logic (`try_files $uri /index.html`). Without this, refreshing the page on `/dashboard` would cause a 404 error in production! It also enables gzip compression to make your site load significantly faster.
