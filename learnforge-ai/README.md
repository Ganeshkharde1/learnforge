# LearnForge AI — Local Hackathon Edition

LearnForge AI is an intelligent learning companion powered by Gemini 1.5 Pro and Vertex AI. It features an AI tutor, adaptive quizzes, RAG document chat, and asynchronous video generation.

This repository is configured for a **local hackathon setup**. It uses a local JSON file for the database, a local `data/storage/` folder for files/videos, and native Python background tasks for queueing. The only external API requirements are **Google Cloud Vertex AI** (for LLMs) and **Google Cloud Text-to-Speech**.

---

## 📋 Prerequisites

Before running the system, make sure you have installed:
1. **Python 3.10+** (for the FastAPI backend)
2. **Node.js 20+** (for the React Vite frontend)
3. **LibreOffice** and **FFmpeg** (These must be installed and added to your system PATH for the video slide-generation to work).

---

## 🔑 Google Cloud Setup (The `.env` Data)

To use the AI features, you need a Google Cloud Project with the Vertex AI and Cloud TTS APIs enabled.

1. **Create a Google Cloud Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project. Note your **Project ID**.
2. **Enable APIs**: In the search bar, look for and enable:
   - **Vertex AI API**
   - **Cloud Text-to-Speech API**
3. **Create a Service Account Key**:
   - Go to **IAM & Admin > Service Accounts**.
   - Create a new Service Account (e.g., `learnforge-ai`).
   - Grant it these roles: **Vertex AI User** and **Cloud TTS API User**.
   - Click the service account > **Keys** tab > **Add Key** > **Create new key** > **JSON**.
   - Download the file and save it as `service-account.json` in your `backend/` folder (for local development).

---

## ☁️ Deploying to Google Cloud Run (via GitHub)

If you are hosting this on Google Cloud Run via continuous deployment from GitHub, you should not commit your `service-account.json` file. Instead, use Google Cloud Secret Manager:

1. Copy the entire contents of your downloaded `service-account.json` file.
2. In your Google Cloud Console, go to **Secret Manager** and create a new secret named `LEARNFORGE_CREDENTIALS`. Paste the JSON string as the secret value.
3. In your **Cloud Run** service settings:
   - Go to **Variables & Secrets** > **Secrets**.
   - Click **Reference a secret**, select `LEARNFORGE_CREDENTIALS`.
   - Mount it as an **Environment Variable** named `GOOGLE_CREDENTIALS_JSON`.
   
The backend is programmed to automatically detect the `GOOGLE_CREDENTIALS_JSON` environment variable, write it to a secure temporary file in memory, and authenticate Vertex AI and TTS seamlessly.

---

## ⚙️ Backend Setup

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   
   # Activate virtual environment (Windows)
   .\venv\Scripts\activate
   # Or (Mac/Linux)
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example file to create your actual config file:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in:
   - `GCP_PROJECT_ID`: Your Google Cloud Project ID (e.g., `my-hackathon-project-123`).
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your key, e.g., `./service-account.json`.

4. **Run the Backend Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The API will start at `http://localhost:8000`. It will automatically create a `data/` folder to store your database (`learnforge_db.json`) and uploaded files.

---

## 🎨 Frontend Setup

1. **Navigate to the frontend folder** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the Frontend Server**:
   ```bash
   npm run dev
   ```
   The web app will start at `http://localhost:5173`.

---

## 🚀 How to Use the App

1. Open `http://localhost:5173` in your browser.
2. At the login screen, enter **any random text** as your User ID (e.g., `demo-user-1`). We removed Firebase auth to make it easy for hackathon judges — your User ID string acts as your unique account!
3. **Explore the tools**:
   - Go to **Document Chat** and drop a PDF to test the local storage and RAG pipeline.
   - Go to **Video Generator** and type a concept like "Neural Networks". The video will be generated asynchronously in the background. Note: Generating a 5-minute video takes ~3 minutes locally!
