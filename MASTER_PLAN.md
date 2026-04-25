# 🧠 LearnForge AI — Intelligent Learning Companion
## Master Engineering & Architecture Plan
### Google PromptWars Hackathon — GCP + Gemini Stack

> **Vertical:** AI-Powered Adaptive Education Platform  
> **Stack Paradigm:** Vibe-coded, agentic, RAG-first, GCP-native  
> **Author Note:** This document is the single source of truth. Hand it to any AI coding agent (Claude Code, Antigravity) and it will produce a complete, working system.

---

## Table of Contents

1. [Vision & Problem Statement](#1-vision--problem-statement)
2. [Feature Inventory](#2-feature-inventory)
3. [AI Features Deep Dive](#3-ai-features-deep-dive)
4. [System Architecture](#4-system-architecture)
5. [Tech Stack](#5-tech-stack)
6. [Repository Structure](#6-repository-structure)
7. [Module-by-Module Build Plan](#7-module-by-module-build-plan)
8. [Database Schema](#8-database-schema)
9. [API Contract](#9-api-contract)
10. [Prompt Engineering Library](#10-prompt-engineering-library)
11. [GCP Services Integration](#11-gcp-services-integration)
12. [Security & Access Control](#12-security--access-control)
13. [Testing Strategy](#13-testing-strategy)
14. [Accessibility Standards](#14-accessibility-standards)
15. [README Template](#15-readme-template)
16. [Vibe-Coding Instructions](#16-vibe-coding-instructions)
17. [Evaluation Checklist](#17-evaluation-checklist)

---

## 1. Vision & Problem Statement

### The Problem
Learning is broken. Users:
- Dump into generic YouTube videos or static docs.
- Have no adaptive path — a beginner and expert see the same content.
- Can't ask questions about *their own* documents mid-session.
- Get bored because nothing is personalized or interactive.
- Have no AI tutor available 24/7 at their pace.

### The Solution: LearnForge AI
An intelligent, agent-driven learning platform where:
- **You describe what you want to learn** → AI generates a structured learning plan.
- **You upload your own files/docs** → AI learns from them and tutors you using your context.
- **An AI tutor converses with you**, quizzes you, adjusts difficulty in real-time.
- **AI generates concept explainer videos** on demand.
- **Progress is tracked and visualized** adaptively.
- Everything is powered by **Gemini API**, built on **GCP**, and runs in a clean **React + FastAPI** monorepo.

---

## 2. Feature Inventory

### 2.1 Core Learning Features

| # | Feature | Description |
|---|---------|-------------|
| F1 | **AI Learning Plan Generator** | User enters a topic → AI Agent generates a week-by-week, module-by-module structured learning plan with milestones |
| F2 | **Adaptive AI Tutor Chat** | Conversational tutor using Gemini with memory, context awareness, difficulty adaptation |
| F3 | **Upload Your Context (RAG)** | Upload PDFs, DOCX, TXT, URLs → system chunks, embeds, stores in FAISS → Gemini answers from YOUR docs |
| F4 | **AI Quiz & Assessment Engine** | Auto-generates MCQs, short answers, fill-in-the-blanks from any topic or uploaded doc |
| F5 | **Concept Video Generator** | AI generates a narrated explainer video (slides + voiceover) for any concept on demand |
| F6 | **Smart Flashcard System** | AI generates spaced-repetition flashcards from any module; tracks confidence levels | use the gemini nano-banana API key for this feature, because it is free and fast|
| F7 | **Progress Dashboard** | Visual learning graph, completion %, weak areas heatmap, streak tracker |
| F8 | **AI Summarizer** | Paste any text/URL → get a structured summary with key concepts, definitions, analogies |
| F9 | **Concept Mind Map** | AI generates an interactive visual mind map for any topic |
| F10 | **Study Session Planner** | AI schedules optimal daily study sessions based on user's pace and available time |

### 2.2 AI Agent Features

| # | Agent | Role |
|---|-------|------|
| A1 | **Planner Agent** | Decomposes any learning goal into a structured plan with prerequisites, milestones, resources |
| A2 | **Tutor Agent** | Conversational, memory-aware, adapts difficulty, uses Socratic method |
| A3 | **RAG Agent** | Retrieves from FAISS vector store, synthesizes answers with Gemini, cites sources |
| A4 | **Assessment Agent** | Designs quizzes, evaluates answers, identifies knowledge gaps |
| A5 | **Content Agent** | Generates slides, video scripts, flashcards, summaries on demand |
| A6 | **Orchestrator Agent** | Routes user intent to the right sub-agent; manages session state |

### 2.3 GCP-Specific Features

| # | Feature | GCP Service |
|---|---------|-------------|
| G1 | Authentication | Firebase Auth |
| G2 | File Storage | Google Cloud Storage |
| G3 | Vector Embeddings | Gemini Embedding API (`text-embedding-004`) |
| G4 | LLM | Gemini 2.5 Pro / Flash |
| G5 | Video Generation | Gemini + Cloud Text-to-Speech + Cloud Run |
| G6 | Backend Hosting | Cloud Run (containerized FastAPI) |
| G7 | Frontend Hosting | cloud run Hosting |
| G8 | Async Jobs | Cloud Tasks / Pub/Sub |
| G9 | Monitoring | Cloud Logging + Cloud Monitoring |

---

## 3. AI Features Deep Dive

### 3.1 RAG Pipeline (Retrieval Augmented Generation)

```
User uploads file
      ↓
[Cloud Storage] stores raw file
      ↓
[Document Processor] chunks text (LangChain RecursiveCharacterTextSplitter)
      ↓
[Gemini Embedding API] embeds each chunk → vector
      ↓
[FAISS Index] stores vectors locally (persisted to Cloud Storage as .faiss file)
      ↓
User asks question
      ↓
[Query Embedding] → similarity search → top-k chunks
      ↓
[Gemini Pro] answers using retrieved chunks as context
      ↓
Response with source citations
```

**Config:**
- Chunk size: 512 tokens, overlap: 64
- Top-k retrieval: 5 chunks
- Embedding model: `models/text-embedding-004`
- LLM: `gemini-1.5-pro-latest`
- FAISS index type: `IndexFlatIP` (inner product / cosine similarity)

---

### 3.2 AI Learning Plan Generator

**Agent Flow:**
```
User input: "I want to learn Kubernetes in 3 weeks, I know Docker basics"
      ↓
Planner Agent → Gemini with structured JSON output schema
      ↓
Output:
{
  "goal": "...",
  "duration_weeks": 3,
  "prerequisites": [...],
  "modules": [
    {
      "week": 1,
      "title": "Core Concepts",
      "topics": [...],
      "resources": [...],
      "milestones": [...],
      "estimated_hours": 8
    }
  ],
  "assessment_checkpoints": [...],
  "final_project": {...}
}
      ↓
Frontend renders interactive plan with progress tracking
```

---

### 3.3 AI Concept Video Generator

**Pipeline:**
```
User: "Generate a video explaining Transformers architecture"
      ↓
Content Agent → Gemini generates:
  - Script (narration text)
  - Slide content (title, bullets, code, diagrams per slide)
      ↓
[Python-pptx OR Reveal.js] generates slides
      ↓
[Google Cloud Text-to-Speech] generates audio narration (WaveNet voice)
      ↓
[MoviePy / FFmpeg on Cloud Run] stitches slides + audio → MP4
      ↓
Video stored in Cloud Storage → served via signed URL
      ↓
User watches in-browser video player
```

**Note:** This is the killer differentiator feature. Keep it as a background async job (Cloud Tasks). Notify user via Firestore real-time listener when ready.

---

### 3.4 Adaptive Tutor Agent

**Memory Strategy:**
- Short-term: In-session conversation history (last 20 messages passed to Gemini)
- Long-term: Firestore stores user's mastered topics, weak areas, quiz scores
- Adaptation: System prompt dynamically updated based on user's profile

**Difficulty Adaptation Algorithm:**
```
If quiz_score >= 80%: increase difficulty, skip basics
If quiz_score 50-80%: maintain current level
If quiz_score < 50%: simplify explanations, add more analogies, re-quiz
```

**Socratic Mode:** Tutor asks guiding questions instead of direct answers when user seems close to understanding.

---

### 3.5 AI Quiz Engine

**Question Types Generated:**
1. Multiple Choice (4 options)
2. True/False with explanation
3. Fill in the blank (code or text)
4. Short answer (evaluated by Gemini)
5. Code completion (for programming topics)

**Evaluation Flow:**
```
User submits answer
→ For MCQ/TF: rule-based check
→ For short answer: Gemini evaluates semantic correctness
→ Score stored in Firestore
→ Weak topics flagged for follow-up
→ Spaced repetition schedule updated
```

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│   React 18 + Vite  │  Firebase Hosting  │  TailwindCSS      │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────────────────────┐
│                       API GATEWAY LAYER                      │
│              FastAPI on Cloud Run (Containerized)            │
│   /api/v1/learn  /api/v1/rag  /api/v1/plan  /api/v1/video  │
└────────────┬──────────────┬──────────────┬───────────────────┘
             │              │              │
    ┌────────▼───┐  ┌───────▼──────┐  ┌───▼──────────────┐
    │ Orchestrator│  │  RAG Service │  │  Video Gen Service│
    │   Agent     │  │ FAISS+Gemini │  │  Cloud Run Job   │
    └────────┬───┘  └───────┬──────┘  └───┬──────────────┘
             │              │              │
    ┌────────▼──────────────▼──────────────▼──────────────┐
    │                    GCP SERVICES                      │
    │  Gemini API │ Firestore │ GCS │ Cloud TTS │ Pub/Sub  │
    └─────────────────────────────────────────────────────┘
    
    ┌──────────────────────────────────────────────────────┐
    │              AUTHENTICATION LAYER                    │
    │         Firebase Auth (Google OAuth + Email)         │
    └──────────────────────────────────────────────────────┘
```

### Data Flow Summary
1. User authenticates → Firebase Auth → JWT token
2. Frontend calls FastAPI with Bearer token
3. FastAPI validates token with Firebase Admin SDK
4. Request routed to appropriate agent/service
5. Agent calls Gemini API (all agents use same Gemini client, different prompts)
6. Responses stored in Firestore, files in GCS
7. Real-time updates via Firestore listeners (video ready, plan updated)

---

## 5. Tech Stack

### Frontend
```
Framework:        React 18 + Vite
Language:         TypeScript
Styling:          TailwindCSS + shadcn/ui components
State:            Zustand (lightweight, simple)
Routing:          React Router v6
Data Fetching:    TanStack Query (React Query)
Rich Text:        TipTap editor
Charts:           Recharts
Mind Maps:        React Flow
Video Player:     React Player
Animations:       Framer Motion
File Upload:      react-dropzone
Markdown:         react-markdown + remark-gfm + rehype-highlight
Auth:             Firebase JS SDK
Real-time:        Firestore onSnapshot
```

### Backend
```
Framework:        FastAPI (Python 3.11)
Language:         Python
Server:           Uvicorn
Auth Middleware:  Firebase Admin SDK
LLM:              google-generativeai (Gemini SDK)
RAG:              LangChain + FAISS + google-generativeai
Embeddings:       Gemini text-embedding-004
Document Parsing: pypdf, python-docx, BeautifulSoup4
Video Generation: moviepy, gTTS / Google Cloud TTS, python-pptx
Task Queue:       Google Cloud Tasks
Storage:          google-cloud-storage
Database:         google-cloud-firestore
Containerization: Docker
```

### GCP Services
```
Compute:          Cloud Run (backend API + video gen worker)
Storage:          Google Cloud Storage (files, FAISS indexes, videos)
Database:         Firestore (user data, sessions, plans, progress)
AI/ML:            Gemini 1.5 Pro, Gemini Flash, Gemini Embeddings, Cloud TTS
Auth:             Firebase Authentication
Hosting:          Firebase Hosting (frontend)
Async:            Cloud Tasks (video generation jobs)
Monitoring:       Cloud Logging, Cloud Monitoring
CI/CD:            Cloud Build + Cloud Run deployment
```

### Dev Tools
```
Monorepo:         Single repo, /frontend + /backend folders
Linting:          ESLint (frontend), Ruff (backend)
Formatting:       Prettier (frontend), Black (backend)
Testing:          Vitest (frontend), pytest (backend)
API Docs:         FastAPI auto-docs (/docs)
Env Management:   python-dotenv + Vite env
Containerization: Docker + docker-compose (local dev)
```

---

## 6. Repository Structure

```
learnforge-ai/
├── README.md                          # Project overview (see Section 15)
├── docker-compose.yml                 # Local dev orchestration
├── .github/
│   └── workflows/
│       └── deploy.yml                 # Cloud Build CI/CD
│
├── frontend/                          # React + Vite app
│   ├── public/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── firebase.ts                # Firebase init
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── AppShell.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── TypingIndicator.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── plan/
│   │   │   │   ├── LearningPlanCard.tsx
│   │   │   │   ├── ModuleAccordion.tsx
│   │   │   │   └── MilestoneTracker.tsx
│   │   │   ├── quiz/
│   │   │   │   ├── QuizCard.tsx
│   │   │   │   ├── QuestionRenderer.tsx
│   │   │   │   └── ScoreBoard.tsx
│   │   │   ├── rag/
│   │   │   │   ├── FileUploadZone.tsx
│   │   │   │   ├── DocumentList.tsx
│   │   │   │   └── CitationPanel.tsx
│   │   │   ├── video/
│   │   │   │   ├── VideoGeneratorForm.tsx
│   │   │   │   ├── VideoPlayer.tsx
│   │   │   │   └── VideoStatusTracker.tsx
│   │   │   ├── flashcards/
│   │   │   │   ├── FlashcardDeck.tsx
│   │   │   │   └── FlashcardFlip.tsx
│   │   │   ├── mindmap/
│   │   │   │   └── MindMapViewer.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── ProgressChart.tsx
│   │   │   │   ├── WeakAreasHeatmap.tsx
│   │   │   │   └── StreakTracker.tsx
│   │   │   └── ui/                    # shadcn components
│   │   ├── pages/
│   │   │   ├── Home.tsx               # Landing page
│   │   │   ├── Dashboard.tsx          # User dashboard
│   │   │   ├── Learn.tsx              # Main chat/tutor interface
│   │   │   ├── PlanGenerator.tsx      # Generate learning plan
│   │   │   ├── RAGChat.tsx            # Chat with your docs
│   │   │   ├── Quiz.tsx               # Quiz mode
│   │   │   ├── VideoGen.tsx           # Video generator
│   │   │   ├── Flashcards.tsx         # Flashcard review
│   │   │   ├── Summarizer.tsx         # Text summarizer
│   │   │   ├── MindMap.tsx            # Mind map generator
│   │   │   └── Auth.tsx               # Login/Signup
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useChat.ts
│   │   │   ├── useRAG.ts
│   │   │   └── useProgress.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── chatStore.ts
│   │   │   └── planStore.ts
│   │   ├── api/
│   │   │   ├── client.ts              # Axios instance + interceptors
│   │   │   ├── learn.ts
│   │   │   ├── plan.ts
│   │   │   ├── rag.ts
│   │   │   ├── quiz.ts
│   │   │   └── video.ts
│   │   ├── types/
│   │   │   └── index.ts               # All TypeScript types
│   │   └── utils/
│   │       ├── markdown.ts
│   │       └── formatters.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                           # FastAPI app
│   ├── main.py                        # FastAPI app entry point
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                  # Settings, env vars
│   │   ├── auth/
│   │   │   ├── firebase_auth.py       # Token validation middleware
│   │   │   └── dependencies.py        # FastAPI auth dependencies
│   │   ├── routers/
│   │   │   ├── learn.py               # /api/v1/learn (tutor chat)
│   │   │   ├── plan.py                # /api/v1/plan (learning plan)
│   │   │   ├── rag.py                 # /api/v1/rag (upload + query)
│   │   │   ├── quiz.py                # /api/v1/quiz
│   │   │   ├── video.py               # /api/v1/video
│   │   │   ├── flashcards.py          # /api/v1/flashcards
│   │   │   ├── summary.py             # /api/v1/summary
│   │   │   ├── mindmap.py             # /api/v1/mindmap
│   │   │   └── progress.py            # /api/v1/progress
│   │   ├── agents/
│   │   │   ├── base_agent.py          # Abstract base with Gemini client
│   │   │   ├── orchestrator.py        # Routes to sub-agents
│   │   │   ├── planner_agent.py       # Learning plan generation
│   │   │   ├── tutor_agent.py         # Conversational tutor
│   │   │   ├── rag_agent.py           # RAG retrieval + answer
│   │   │   ├── assessment_agent.py    # Quiz generation + eval
│   │   │   └── content_agent.py       # Video, flashcards, summaries
│   │   ├── rag/
│   │   │   ├── document_processor.py  # Chunking, parsing
│   │   │   ├── embedder.py            # Gemini embedding calls
│   │   │   ├── vector_store.py        # FAISS CRUD operations
│   │   │   └── retriever.py           # Query → top-k chunks
│   │   ├── video/
│   │   │   ├── script_generator.py    # Gemini → video script
│   │   │   ├── slide_builder.py       # Script → slides (python-pptx)
│   │   │   ├── tts_service.py         # GCP TTS → audio files
│   │   │   └── video_compiler.py      # MoviePy → final MP4
│   │   ├── services/
│   │   │   ├── gcs_service.py         # Google Cloud Storage ops
│   │   │   ├── firestore_service.py   # Firestore CRUD
│   │   │   ├── tasks_service.py       # Cloud Tasks enqueue
│   │   │   └── gemini_client.py       # Centralized Gemini SDK client
│   │   ├── models/
│   │   │   ├── user.py                # Pydantic models
│   │   │   ├── plan.py
│   │   │   ├── chat.py
│   │   │   ├── quiz.py
│   │   │   └── video.py
│   │   └── utils/
│   │       ├── prompts.py             # All prompt templates
│   │       ├── validators.py
│   │       └── helpers.py
│   └── tests/
│       ├── test_agents.py
│       ├── test_rag.py
│       ├── test_routers.py
│       └── conftest.py
│
├── infra/                             # IaC (optional for hackathon)
│   ├── cloudbuild.yaml
│   └── firestore.rules
│
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── screenshots/
```

---

## 7. Module-by-Module Build Plan

> Build in this order. Each module is independently testable.

### Phase 1: Foundation (Day 1)
**Goal:** Auth + skeleton running on GCP

**Tasks:**
1. Set up Firebase project → enable Auth (Google + Email/Password)
2. Set up Firestore database (native mode)
3. Set up GCS bucket for file storage
4. Enable Gemini API, get API key → store in GCP Secret Manager
5. Create FastAPI skeleton with health endpoint
6. Add Firebase Auth middleware to FastAPI
7. Create React app with Vite + TailwindCSS
8. Implement login/logout page (Firebase Auth)
9. Set up Axios client with Firebase token injection
10. Deploy FastAPI to Cloud Run, React to Firebase Hosting
11. Write `docker-compose.yml` for local dev

**Files to create:** `backend/main.py`, `backend/app/auth/`, `frontend/src/firebase.ts`, `frontend/src/pages/Auth.tsx`

---

### Phase 2: RAG System (Day 1-2)
**Goal:** Upload docs, chat with them

**Tasks:**
1. Create `document_processor.py`:
   - Support PDF (pypdf), DOCX (python-docx), TXT, URLs (BeautifulSoup)
   - RecursiveCharacterTextSplitter: chunk_size=512, overlap=64
2. Create `embedder.py`:
   - Use `genai.embed_content(model='models/text-embedding-004', content=chunk)`
   - Batch embed all chunks
3. Create `vector_store.py`:
   - FAISS IndexFlatIP
   - Save/load index from GCS (per user namespace: `user_id/index.faiss`, `user_id/metadata.json`)
   - metadata.json: `[{chunk_id, source_file, page_num, text}, ...]`
4. Create `retriever.py`:
   - Embed query → search FAISS → return top-5 chunks + metadata
5. Create `rag_agent.py`:
   - System prompt: "You are a tutor answering from provided context only"
   - Build prompt: `context_chunks + user_question`
   - Call Gemini 1.5 Pro
   - Return answer + source citations
6. Create `/api/v1/rag` router:
   - `POST /upload`: receive file → GCS → process → embed → store FAISS
   - `POST /query`: question → retrieve → answer
   - `GET /documents`: list user's uploaded docs
   - `DELETE /documents/{doc_id}`: remove doc from index
7. Frontend: `FileUploadZone.tsx` + `RAGChat.tsx`

---

### Phase 3: AI Tutor Chat (Day 2)
**Goal:** Conversational AI tutor with session memory

**Tasks:**
1. Create `tutor_agent.py`:
   - Accept: topic, user_message, conversation_history, user_profile (skill level, mastered topics)
   - System prompt: adaptive tutor (see Section 10)
   - Use Gemini `start_chat()` for multi-turn or manual history passing
   - Return: response_text, detected_difficulty, suggested_followup
2. Firestore session management:
   - `sessions/{user_id}/{session_id}` → stores message history
   - `users/{user_id}/profile` → skill level, weak topics
3. Create `/api/v1/learn` router:
   - `POST /chat`: send message, get tutor response (streaming preferred)
   - `GET /sessions`: list user sessions
   - `DELETE /sessions/{id}`: clear session
4. Frontend: `ChatWindow.tsx` with streaming text support, markdown rendering

**Streaming:** Use FastAPI `StreamingResponse` + Gemini `stream=True` → SSE to frontend

---

### Phase 4: Learning Plan Generator (Day 2)
**Goal:** AI generates structured, actionable learning plans

**Tasks:**
1. Create `planner_agent.py`:
   - Input: goal, current_level, available_hours_per_week, duration_weeks
   - Force JSON output using Gemini structured output / response_schema
   - Output schema: see Section 3.2
2. Store plan in Firestore: `plans/{user_id}/{plan_id}`
3. Create `/api/v1/plan` router:
   - `POST /generate`: generate plan
   - `GET /`: list user plans
   - `PATCH /{plan_id}/progress`: update module completion
4. Frontend: `PlanGenerator.tsx` form + `LearningPlanCard.tsx` with progress tracking

---

### Phase 5: Quiz & Assessment Engine (Day 3)
**Goal:** AI-generated quizzes, evaluated answers, gap analysis

**Tasks:**
1. Create `assessment_agent.py`:
   - `generate_quiz(topic, num_questions, difficulty, question_types)` → JSON quiz
   - `evaluate_answer(question, correct_answer, user_answer)` → score + feedback (Gemini)
2. Firestore: `quizzes/{user_id}/{quiz_id}` → store attempts, scores
3. `/api/v1/quiz` router:
   - `POST /generate`: generate quiz from topic or RAG context
   - `POST /submit`: evaluate answers
   - `GET /history`: past quiz scores
4. Frontend: `QuizCard.tsx` with animated answer reveal, scoring

---

### Phase 6: AI Video Generator (Day 3-4)
**Goal:** Async video generation from concept → MP4

**Tasks:**
1. `script_generator.py`:
   - Gemini generates: `{slides: [{title, narration, bullet_points, code?}]}`
   - 5-8 slides per video, ~3 min target
2. `slide_builder.py`:
   - python-pptx: create PPTX from slide data
   - Export each slide as PNG via LibreOffice CLI (Cloud Run)
3. `tts_service.py`:
   - Google Cloud TTS: `texttospeech.SynthesizeSpeechRequest`
   - WaveNet voice, one audio file per slide narration
4. `video_compiler.py`:
   - MoviePy: stitch slide PNGs + audio → MP4
   - Add fade transitions, title card
5. Full async flow:
   - `POST /api/v1/video/generate` → enqueues Cloud Task → returns `job_id`
   - Cloud Task worker calls `/internal/video/process/{job_id}`
   - Worker generates video → uploads to GCS → updates Firestore `job status = ready`
   - Frontend polls Firestore via `onSnapshot` → shows player when ready
6. Frontend: `VideoGeneratorForm.tsx` + polling status + `VideoPlayer.tsx`

---

### Phase 7: Flashcards + Summarizer + Mind Map (Day 4)
**Goal:** Remaining AI features

**Flashcards:**
1. `content_agent.py → generate_flashcards(topic, num=20)` → `[{front, back, difficulty}]`
2. Spaced repetition logic: Leitner system (boxes 1-5, review schedule based on last_reviewed + box)
3. Frontend: `FlashcardFlip.tsx` with flip animation, confidence rating buttons

**Summarizer:**
1. `content_agent.py → summarize(text)` → `{summary, key_concepts, definitions, analogies}`
2. Support URL input: BeautifulSoup scrape → summarize
3. Frontend: simple textarea input + structured output display

**Mind Map:**
1. `content_agent.py → generate_mindmap(topic)` → JSON node-edge graph
2. Output: `{nodes: [{id, label, level}], edges: [{source, target}]}`
3. Frontend: React Flow renders interactive mind map

---

### Phase 8: Dashboard + Progress (Day 4-5)
**Goal:** User sees all their progress visually

**Tasks:**
1. Aggregate from Firestore:
   - `users/{user_id}/profile`: total sessions, topics covered, avg quiz score
   - `quizzes/{user_id}`: per-topic scores → weak areas
   - `plans/{user_id}`: module completion %
2. `/api/v1/progress`:
   - `GET /overview`: aggregated stats
   - `GET /weak-areas`: topics with score < 60%
3. Frontend: `Dashboard.tsx` with:
   - Weekly activity chart (Recharts BarChart)
   - Topic mastery radar chart
   - Streak calendar (GitHub-style contribution grid)
   - Weak areas list with "Re-study" CTA

---

### Phase 9: Polish + Testing + Deploy (Day 5)
**Goal:** Production-ready, tested, deployed

**Tasks:**
1. Write pytest tests for all agents and routers
2. Write Vitest tests for key React components
3. Add rate limiting (FastAPI `slowapi` + Redis or in-memory)
4. Add error boundaries in React
5. Add loading skeletons everywhere
6. Accessibility audit: ARIA labels, keyboard nav, color contrast
7. Write README (see Section 15)
8. Final Cloud Run + Firebase Hosting deployment
9. Record demo video

---

## 8. Database Schema

### Firestore Collections

```
users/
  {user_id}/
    email: string
    display_name: string
    created_at: timestamp
    profile/
      skill_level: "beginner" | "intermediate" | "advanced"
      mastered_topics: string[]
      weak_topics: string[]
      total_sessions: number
      study_streak: number
      last_active: timestamp

plans/
  {user_id}/
    {plan_id}/
      goal: string
      duration_weeks: number
      created_at: timestamp
      status: "active" | "completed" | "paused"
      modules: [
        {
          week: number,
          title: string,
          topics: string[],
          completed: boolean,
          completed_at?: timestamp
        }
      ]

sessions/
  {user_id}/
    {session_id}/
      created_at: timestamp
      topic: string
      messages: [
        {role: "user"|"model", content: string, timestamp: timestamp}
      ]

quizzes/
  {user_id}/
    {quiz_id}/
      topic: string
      created_at: timestamp
      score: number
      total_questions: number
      answers: [{question, user_answer, correct, feedback}]

documents/
  {user_id}/
    {doc_id}/
      filename: string
      gcs_path: string
      faiss_index_path: string
      uploaded_at: timestamp
      chunk_count: number
      status: "processing" | "ready" | "error"

video_jobs/
  {user_id}/
    {job_id}/
      concept: string
      status: "queued" | "generating" | "ready" | "error"
      video_url?: string
      created_at: timestamp
      completed_at?: timestamp

flashcards/
  {user_id}/
    {deck_id}/
      topic: string
      cards: [{front, back, difficulty, box, last_reviewed}]

```

---

## 9. API Contract

### Base URL: `/api/v1`

#### Auth: All endpoints require `Authorization: Bearer {firebase_token}`

---

#### Learn (Tutor Chat)
```
POST /learn/chat
Body: {session_id: string, message: string, topic?: string}
Response: SSE stream of text chunks

GET /learn/sessions
Response: [{session_id, topic, created_at, message_count}]

DELETE /learn/sessions/{session_id}
Response: {deleted: true}
```

#### Plan
```
POST /plan/generate
Body: {goal: string, current_level: string, hours_per_week: number, duration_weeks: number}
Response: {plan_id: string, plan: PlanObject}

GET /plan/
Response: [PlanObject]

PATCH /plan/{plan_id}/progress
Body: {module_index: number, completed: boolean}
Response: {updated: true}
```

#### RAG
```
POST /rag/upload
Body: multipart/form-data (file)
Response: {doc_id: string, status: "processing"}

POST /rag/query
Body: {question: string, doc_ids?: string[]}
Response: {answer: string, citations: [{doc_id, filename, chunk_text, page}]}

GET /rag/documents
Response: [{doc_id, filename, status, uploaded_at, chunk_count}]

DELETE /rag/documents/{doc_id}
Response: {deleted: true}
```

#### Quiz
```
POST /quiz/generate
Body: {topic: string, num_questions: number, difficulty: string, types: string[]}
Response: {quiz_id: string, questions: QuizQuestion[]}

POST /quiz/submit
Body: {quiz_id: string, answers: [{question_id: string, answer: string}]}
Response: {score: number, feedback: [{question_id, correct, explanation}], weak_areas: string[]}

GET /quiz/history
Response: [{quiz_id, topic, score, created_at}]
```

#### Video
```
POST /video/generate
Body: {concept: string, depth: "brief"|"detailed"}
Response: {job_id: string, status: "queued"}

GET /video/status/{job_id}
Response: {status: string, video_url?: string, progress?: number}

GET /video/library
Response: [{job_id, concept, video_url, created_at}]
```

#### Flashcards
```
POST /flashcards/generate
Body: {topic: string, num_cards: number}
Response: {deck_id: string, cards: Flashcard[]}

PATCH /flashcards/{deck_id}/review
Body: {card_id: string, confidence: 1|2|3|4|5}
Response: {next_review: timestamp}
```

#### Summary
```
POST /summary/text
Body: {text: string}
Response: {summary: string, key_concepts: string[], definitions: {term: string, definition: string}[], analogies: string[]}

POST /summary/url
Body: {url: string}
Response: same as above
```

#### Mind Map
```
POST /mindmap/generate
Body: {topic: string, depth: number}
Response: {nodes: Node[], edges: Edge[]}
```

#### Progress
```
GET /progress/overview
Response: {total_sessions, topics_covered, avg_quiz_score, study_streak, plans_active}

GET /progress/weak-areas
Response: [{topic, avg_score, last_tested, recommended_resources}]
```

---

## 10. Prompt Engineering Library

> All prompts live in `backend/app/utils/prompts.py`. Use these exactly.

### 10.1 Tutor Agent System Prompt
```python
TUTOR_SYSTEM_PROMPT = """
You are LearnForge, an expert AI tutor. Your teaching philosophy:

1. ADAPT: You detect the user's level from their messages and adjust your explanation depth accordingly.
   - Beginner: Use analogies, avoid jargon, explain step by step.
   - Intermediate: Introduce technical terms, assume basic knowledge.
   - Advanced: Peer-level discussion, discuss trade-offs, edge cases.

2. SOCRATIC: When the user is close to understanding, ask guiding questions instead of explaining directly.

3. STRUCTURED: Always structure your responses:
   - Core concept (1-2 sentences)
   - Explanation with example
   - Code snippet (if technical, always in markdown code blocks)
   - Check-in question ("Does that make sense? Want to go deeper on X?")

4. CONCISE: Avoid walls of text. Use bullet points, headers, code blocks.

5. ENCOURAGING: Never make the user feel dumb. Celebrate progress.

Current user level: {skill_level}
Current topic: {topic}
User's weak areas: {weak_areas}

Conversation history: {conversation_history}
"""
```

### 10.2 Planner Agent Prompt
```python
PLANNER_PROMPT = """
You are a senior learning architect. Generate a structured learning plan.

User goal: {goal}
Current level: {current_level}
Available hours per week: {hours_per_week}
Duration: {duration_weeks} weeks

Return a JSON object ONLY (no markdown, no explanation) with this exact schema:
{
  "goal": "string",
  "summary": "2-sentence overview",
  "prerequisites": ["list of assumed prior knowledge"],
  "duration_weeks": number,
  "modules": [
    {
      "week": number,
      "title": "string",
      "description": "string",
      "topics": ["specific topic 1", "specific topic 2"],
      "resources": [{"type": "article|video|book|practice", "title": "string", "url_hint": "string"}],
      "milestones": ["what user will be able to do after this week"],
      "estimated_hours": number,
      "hands_on_project": "string or null"
    }
  ],
  "assessment_checkpoints": [{"after_week": number, "assessment_type": "quiz|project|review"}],
  "final_project": {"title": "string", "description": "string"}
}
"""
```

### 10.3 Quiz Generator Prompt
```python
QUIZ_GENERATOR_PROMPT = """
Generate a quiz on the topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}
Question types: {question_types}

Return JSON ONLY:
{
  "quiz_title": "string",
  "questions": [
    {
      "id": "q1",
      "type": "mcq|true_false|short_answer|fill_blank|code_complete",
      "question": "string",
      "options": ["A", "B", "C", "D"],  // for MCQ only
      "correct_answer": "string",
      "explanation": "why this is the answer",
      "difficulty": "easy|medium|hard"
    }
  ]
}
"""
```

### 10.4 Video Script Prompt
```python
VIDEO_SCRIPT_PROMPT = """
Create a video script for an educational explainer on: {concept}
Target audience: {level}
Target duration: ~{duration_minutes} minutes

Return JSON ONLY:
{
  "title": "string",
  "total_duration_seconds": number,
  "slides": [
    {
      "slide_number": number,
      "slide_type": "title|concept|example|code|summary",
      "title": "string",
      "narration": "exact text to be spoken for this slide",
      "bullet_points": ["string"],
      "code_snippet": "string or null",
      "visual_description": "what should be on screen (for image generation hint)",
      "duration_seconds": number
    }
  ]
}

Rules:
- 5-8 slides total
- narration should be natural, conversational speech
- include at least 1 code slide if technical topic
- last slide = summary + next steps
"""
```

### 10.5 RAG System Prompt
```python
RAG_SYSTEM_PROMPT = """
You are a precise document assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
1. Base your answer strictly on the provided context. Do not use outside knowledge.
2. If the context doesn't contain the answer, say "I couldn't find this in your uploaded documents."
3. Always cite which document/section your answer comes from.
4. Format your answer clearly with headers if complex.

Context chunks from user's documents:
{context}

User question: {question}
"""
```

### 10.6 Mind Map Prompt
```python
MINDMAP_PROMPT = """
Generate a mind map for: {topic}
Depth: {depth} levels (1=core concept only, 2=subtopics, 3=detailed)

Return JSON ONLY:
{
  "nodes": [
    {"id": "1", "label": "Core Topic", "level": 0},
    {"id": "2", "label": "Subtopic A", "level": 1},
    {"id": "3", "label": "Detail A1", "level": 2}
  ],
  "edges": [
    {"source": "1", "target": "2"},
    {"source": "2", "target": "3"}
  ]
}
"""
```

### 10.7 Flashcard Prompt
```python
FLASHCARD_PROMPT = """
Generate {num_cards} flashcards for learning: {topic}

Return JSON ONLY:
{
  "deck_title": "string",
  "cards": [
    {
      "id": "string",
      "front": "Question or term",
      "back": "Answer or definition (concise, max 3 sentences)",
      "difficulty": "easy|medium|hard",
      "tags": ["string"]
    }
  ]
}
"""
```

---

## 11. GCP Services Integration

### 11.1 Gemini API Usage

```python
# backend/app/services/gemini_client.py
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

# LLM for text generation
llm = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        max_output_tokens=8192,
    ),
    safety_settings=[...]  # Configure appropriate safety settings
)

# For JSON output (plans, quizzes, etc.)
llm_json = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=genai.GenerationConfig(
        temperature=0.3,  # lower for structured output
        response_mime_type="application/json"  # Force JSON
    )
)

# Embeddings
def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]
```

### 11.2 Firebase Auth Middleware

```python
# backend/app/auth/firebase_auth.py
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header

cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

async def verify_token(authorization: str = Header(...)) -> dict:
    token = authorization.replace("Bearer ", "")
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 11.3 GCS Operations

```python
# backend/app/services/gcs_service.py
from google.cloud import storage

class GCSService:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def upload_file(self, source_path: str, dest_blob: str) -> str:
        blob = self.bucket.blob(dest_blob)
        blob.upload_from_filename(source_path)
        return blob.public_url
    
    def upload_bytes(self, data: bytes, dest_blob: str, content_type: str) -> str:
        blob = self.bucket.blob(dest_blob)
        blob.upload_from_string(data, content_type=content_type)
        return blob.generate_signed_url(expiration=3600 * 24 * 7)  # 7 days
    
    def download_bytes(self, blob_name: str) -> bytes:
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()
```

### 11.4 Cloud Tasks (Async Video Jobs)

```python
# backend/app/services/tasks_service.py
from google.cloud import tasks_v2
import json

def enqueue_video_job(job_id: str, user_id: str, concept: str):
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(PROJECT_ID, REGION, "video-generation")
    
    task = {
        "http_request": {
            "url": f"{BACKEND_URL}/internal/video/process/{job_id}",
            "http_method": tasks_v2.HttpMethod.POST,
            "body": json.dumps({"user_id": user_id, "concept": concept}).encode(),
            "headers": {"Content-Type": "application/json"},
            "oidc_token": {"service_account_email": SERVICE_ACCOUNT_EMAIL}
        }
    }
    client.create_task(parent=parent, task=task)
```

### 11.5 Cloud TTS

```python
# backend/app/video/tts_service.py
from google.cloud import texttospeech

def synthesize_speech(text: str, output_path: str):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(output_path, "wb") as f:
        f.write(response.audio_content)
```

---

## 12. Security & Access Control

### 12.1 Authentication
- All API endpoints protected by Firebase Auth middleware
- Token validated server-side on every request
- No sensitive data returned without valid token

### 12.2 Data Isolation
- All Firestore queries scoped to `user_id` (from verified token)
- All GCS paths prefixed with `user_id/`
- FAISS indexes isolated per user: `user_id/index.faiss`
- Users cannot access other users' data by any means

### 12.3 File Upload Security
- File type validation: whitelist only PDF, DOCX, TXT, MD
- File size limit: 20MB max
- Virus/malware scanning: use GCS Object Lifecycle + Cloud Security Scanner (optional)
- File names sanitized before storage (UUID-based naming)

### 12.4 Rate Limiting
```python
# using slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("30/minute")  # 30 messages per minute
async def chat(...):
    ...

@router.post("/video/generate")
@limiter.limit("5/hour")   # expensive operation
async def generate_video(...):
    ...
```

### 12.5 API Key Security
- Gemini API key stored in GCP Secret Manager
- Accessed via `google-cloud-secret-manager` SDK at runtime
- Never committed to repository (`.env.example` only)
- Firebase service account JSON stored as Cloud Run secret

### 12.6 Content Safety
- Gemini safety settings configured to block harmful content
- User-uploaded content processed server-side only
- Video generation includes content moderation check before rendering

### 12.7 CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-firebase-app.web.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 12.8 Firestore Security Rules
```
// infra/firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /plans/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    // Same pattern for all collections
  }
}
```

---

## 13. Testing Strategy

### 13.1 Backend Tests (pytest)

```python
# tests/test_rag.py
import pytest
from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import VectorStore

def test_chunk_pdf(sample_pdf_path):
    processor = DocumentProcessor()
    chunks = processor.process_pdf(sample_pdf_path)
    assert len(chunks) > 0
    assert all(len(c.text) <= 600 for c in chunks)

def test_embed_and_retrieve(mock_gemini_client):
    store = VectorStore(user_id="test_user")
    chunks = [{"text": "Python is a programming language", "source": "test.pdf"}]
    store.add_chunks(chunks)
    results = store.search("What is Python?", top_k=1)
    assert len(results) == 1

# tests/test_agents.py
def test_planner_agent_returns_valid_plan(mock_gemini_client):
    from app.agents.planner_agent import PlannerAgent
    agent = PlannerAgent()
    plan = agent.generate(goal="Learn React", level="beginner", hours=10, weeks=4)
    assert "modules" in plan
    assert len(plan["modules"]) == 4

def test_quiz_agent_generates_questions(mock_gemini_client):
    from app.agents.assessment_agent import AssessmentAgent
    agent = AssessmentAgent()
    quiz = agent.generate_quiz(topic="Python basics", num_questions=5)
    assert len(quiz["questions"]) == 5
```

### 13.2 Frontend Tests (Vitest)

```typescript
// src/components/quiz/QuizCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { QuizCard } from './QuizCard'

test('shows options and highlights correct answer on submit', () => {
  const question = {
    id: 'q1', type: 'mcq',
    question: 'What is Python?',
    options: ['A language', 'A snake', 'A framework', 'A database'],
    correct_answer: 'A language'
  }
  render(<QuizCard question={question} onAnswer={jest.fn()} />)
  fireEvent.click(screen.getByText('A language'))
  fireEvent.click(screen.getByText('Submit'))
  expect(screen.getByText('Correct!')).toBeInTheDocument()
})
```

### 13.3 Integration Tests
- Test full RAG pipeline: upload file → query → verify citation
- Test chat session persistence across requests
- Test video job creation → Cloud Task enqueue → status polling

### 13.4 Test Commands
```bash
# Backend
cd backend && pytest tests/ -v --cov=app --cov-report=html

# Frontend
cd frontend && npm run test -- --coverage
```

---

## 14. Accessibility Standards

### WCAG 2.1 AA Compliance

1. **Color Contrast:** All text meets 4.5:1 contrast ratio (use Tailwind `slate` palette with proper dark/light)
2. **Keyboard Navigation:** All interactive elements reachable via Tab, Enter, Space
3. **Screen Reader:** All images have `alt` text; icons have `aria-label`; status updates announced via `aria-live`
4. **Focus Indicators:** Visible focus rings on all interactive elements (`focus-visible:ring-2`)
5. **Semantic HTML:** Use `<main>`, `<nav>`, `<section>`, `<article>`, `<header>`; headings in order (h1→h2→h3)
6. **Form Labels:** All inputs have associated `<label>` or `aria-label`
7. **Error Messages:** Form errors announced to screen readers via `aria-describedby`
8. **Responsive:** Works on 320px to 2560px viewport widths
9. **Motion:** Respect `prefers-reduced-motion` → disable Framer Motion animations
10. **Loading States:** Skeleton screens with `aria-busy="true"` + `role="status"` announcements

```tsx
// Example accessible component pattern
<button
  aria-label="Generate learning plan"
  aria-busy={isLoading}
  disabled={isLoading}
  className="focus-visible:ring-2 focus-visible:ring-blue-500 ..."
>
  {isLoading ? <Spinner aria-hidden /> : "Generate Plan"}
</button>
```

---

## 15. README Template

```markdown
# LearnForge AI — Intelligent Learning Companion

> AI-powered adaptive education platform built on Google Cloud + Gemini API

## Chosen Vertical
**Education & Adaptive Learning** — Helping users learn any skill efficiently through personalized AI tutoring, RAG-powered document chat, auto-generated learning plans, and AI video explainers.

## Approach & Logic
LearnForge uses a multi-agent architecture:
- **Orchestrator Agent** routes user intent to specialized sub-agents
- **Tutor Agent** delivers Socratic, adaptive conversational teaching via Gemini 1.5 Pro
- **RAG Agent** enables users to upload their own documents and ask questions using FAISS vector search + Gemini
- **Planner Agent** decomposes any learning goal into a structured week-by-week plan
- **Content Agent** generates flashcards, summaries, mind maps, and video scripts on demand

## How It Works
1. User signs in via Firebase Auth (Google OAuth)
2. User describes learning goal → AI generates a personalized plan
3. User uploads study materials (PDF, DOCX) → system chunks + embeds + stores in FAISS
4. User chats with AI tutor, which uses their documents as context
5. AI generates quizzes, flashcards, and concept explainer videos
6. Progress tracked in Firestore, visualized in dashboard

## Tech Stack
- **Frontend:** React 18, TypeScript, TailwindCSS, Vite
- **Backend:** FastAPI (Python), Cloud Run
- **LLM:** Gemini 1.5 Pro / Flash (google-generativeai SDK)
- **Embeddings:** Gemini text-embedding-004
- **Vector DB:** FAISS (persisted to GCS)
- **Database:** Firestore
- **Auth:** Firebase Authentication
- **Storage:** Google Cloud Storage
- **TTS:** Google Cloud Text-to-Speech
- **Async Jobs:** Cloud Tasks
- **Hosting:** Firebase Hosting + Cloud Run

## Google Services Used
| Service | Usage |
|---------|-------|
| Gemini 1.5 Pro | Tutoring, plan generation, quiz creation |
| Gemini Flash | Flashcards, summaries, mind maps (speed-optimized) |
| Gemini Embeddings | Document vectorization for RAG |
| Firebase Auth | User authentication |
| Firestore | All user data, sessions, progress |
| Google Cloud Storage | Files, FAISS indexes, generated videos |
| Cloud Run | Backend API + video generation workers |
| Firebase Hosting | React frontend |
| Cloud Tasks | Async video generation queue |
| Cloud TTS | AI-narrated video voiceover |
| Cloud Logging | Centralized backend logs |

## Assumptions
- Users have a Google account for sign-in
- File uploads are limited to 20MB (educational materials are typically small)
- Video generation is async and may take 2-5 minutes
- FAISS indexes are per-user and stored in GCS (not a managed vector DB, for hackathon simplicity)

## Setup Instructions
[See SETUP.md]

## Architecture Diagram
[See docs/architecture.md]
```

---

## 16. Vibe-Coding Instructions

> Hand these instructions verbatim to Claude Code or Antigravity to start coding.

### Instruction Set A — Backend Foundation

```
Build a FastAPI backend for LearnForge AI following the structure in MASTER_PLAN.md Section 6.

Start with:
1. `backend/main.py` with CORS, health endpoint, all routers mounted
2. `backend/app/config.py` — Settings class reading from env vars: GEMINI_API_KEY, GCS_BUCKET, FIREBASE_PROJECT_ID, ENVIRONMENT
3. `backend/app/auth/firebase_auth.py` — Firebase Admin SDK token verification FastAPI dependency
4. `backend/app/services/gemini_client.py` — Centralized Gemini SDK client with llm, llm_json, embed_text
5. `backend/app/services/gcs_service.py` — GCS upload, download, signed URL methods
6. `backend/app/services/firestore_service.py` — Generic CRUD for all collections
7. `backend/Dockerfile` — Multi-stage, Python 3.11, non-root user
8. `backend/requirements.txt`
9. `docker-compose.yml` for local dev (backend + frontend)

Use pydantic-settings for config. All env vars have defaults for local dev. No hardcoded secrets.
```

### Instruction Set B — RAG Pipeline

```
Build the RAG pipeline for LearnForge AI:

Files to create:
1. backend/app/rag/document_processor.py — Process PDF/DOCX/TXT into chunks using LangChain RecursiveCharacterTextSplitter (chunk_size=512, overlap=64). Return list of {text, source, page_num}
2. backend/app/rag/embedder.py — Batch embed chunks using Gemini text-embedding-004
3. backend/app/rag/vector_store.py — FAISS IndexFlatIP. Methods: add_chunks, search, save_to_gcs, load_from_gcs
4. backend/app/rag/retriever.py — Query → embed → search FAISS → return top_k chunks
5. backend/app/agents/rag_agent.py — Takes question + retrieved chunks → Gemini answer + citations
6. backend/app/routers/rag.py — POST /upload (multipart), POST /query, GET /documents, DELETE /documents/{id}

All operations scoped to user_id. FAISS index saved as {user_id}/index.faiss in GCS. Metadata as {user_id}/metadata.json.
```

### Instruction Set C — AI Agents

```
Build all AI agents for LearnForge AI using the prompts in MASTER_PLAN.md Section 10:

1. backend/app/agents/base_agent.py — Abstract base class, Gemini client, error handling
2. backend/app/agents/planner_agent.py — generate(goal, level, hours, weeks) → LearningPlan JSON
3. backend/app/agents/tutor_agent.py — chat(message, history, user_profile, topic) → StreamingResponse
4. backend/app/agents/assessment_agent.py — generate_quiz(topic, num, difficulty) → Quiz JSON; evaluate_answer(q, user_ans, correct_ans) → score + feedback
5. backend/app/agents/content_agent.py — summarize(text), generate_flashcards(topic, num), generate_mindmap(topic), generate_video_script(concept, level)
6. backend/app/agents/orchestrator.py — classify intent from message → route to correct agent

Use Gemini response_mime_type="application/json" for all structured outputs. Streaming for tutor chat. All agents take user_id for Firestore read/write.
```

### Instruction Set D — Frontend

```
Build the React frontend for LearnForge AI:

Design direction: Dark theme, editorial/technical aesthetic. Primary color: electric blue (#3B82F6). Background: near-black (#0A0A0F). Card backgrounds: (#111827). Typography: 'IBM Plex Mono' for headings (code-like), 'Inter' for body. Clean, data-dense, developer-tool feel.

Pages to build (all behind auth):
1. Auth.tsx — Google OAuth sign-in, centered card, brand logo
2. Dashboard.tsx — Stats overview, recent sessions, weak areas, streak
3. PlanGenerator.tsx — Form (goal, level, hours, weeks) → animated plan reveal
4. Learn.tsx — Chat interface, streaming text, markdown rendering, session history sidebar
5. RAGChat.tsx — File upload zone + chat interface side by side, citation panel
6. Quiz.tsx — Full-screen quiz card with progress bar, animated feedback
7. VideoGen.tsx — Concept input, async job status, video player
8. Flashcards.tsx — 3D flip card animation, confidence rating
9. Summarizer.tsx — Textarea input + structured output
10. MindMap.tsx — React Flow interactive graph

Global: AppShell with collapsible sidebar, all pages use TanStack Query for data fetching, Zustand for auth state, streaming SSE for tutor chat.
```

### Instruction Set E — Video Generation

```
Build the async video generation pipeline:

1. backend/app/video/script_generator.py — Gemini generates video script JSON (see Section 10.4 prompt)
2. backend/app/video/slide_builder.py — python-pptx builds slides from script, exports each slide as PNG using subprocess LibreOffice CLI
3. backend/app/video/tts_service.py — Google Cloud TTS synthesizes narration per slide → MP3 files
4. backend/app/video/video_compiler.py — MoviePy: load PNG + MP3 per slide, add fade transition, concat → MP4
5. backend/app/routers/video.py — POST /generate (enqueue Cloud Task), GET /status/{job_id}, GET /library
6. backend/internal/video_worker.py — Internal route called by Cloud Task, runs full pipeline, uploads to GCS, updates Firestore

Full async flow: generate endpoint → Cloud Task → worker → GCS → Firestore update → frontend polling via onSnapshot.
```

---

## 17. Evaluation Checklist

### Code Quality ✅
- [ ] Consistent code style (Ruff/Black backend, ESLint/Prettier frontend)
- [ ] Type hints everywhere (Python) and TypeScript throughout
- [ ] No dead code, no commented-out blocks
- [ ] Meaningful variable/function names
- [ ] DRY: no copy-pasted logic
- [ ] Clear separation of concerns (agents/routers/services/models)
- [ ] FastAPI auto-docs working at `/docs`

### Security ✅
- [ ] Firebase Auth on all endpoints
- [ ] All queries scoped to authenticated user_id
- [ ] No API keys in code
- [ ] File upload validation (type + size)
- [ ] CORS properly configured
- [ ] Firestore security rules deployed
- [ ] Rate limiting on expensive endpoints

### Efficiency ✅
- [ ] Gemini Flash for fast/cheap operations (flashcards, summary, mindmap)
- [ ] Gemini Pro for complex reasoning (tutor, plan, quiz evaluation)
- [ ] FAISS for fast vector similarity (no network overhead vs managed DBs)
- [ ] Streaming responses for tutor chat (TTFB < 1s)
- [ ] Batch embedding for document uploads
- [ ] Video generation async (never blocks the API)
- [ ] TanStack Query caching on frontend

### Testing ✅
- [ ] pytest tests for all agents
- [ ] pytest tests for all routers (with mock Gemini client)
- [ ] FAISS pipeline integration test
- [ ] Frontend component tests (Vitest)
- [ ] Coverage > 70%
- [ ] All tests pass in CI

### Accessibility ✅
- [ ] WCAG 2.1 AA contrast ratios
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels on icons, buttons, status elements
- [ ] Semantic HTML structure
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive 320px → 2560px
- [ ] Screen reader tested (basic pass)

### Google Services ✅
- [ ] Gemini 1.5 Pro (tutor, planner, quiz eval)
- [ ] Gemini Flash (flashcards, summary, mindmap)
- [ ] Gemini Embeddings (RAG)
- [ ] Firebase Auth (authentication)
- [ ] Firestore (all user data)
- [ ] Cloud Storage (files, videos, FAISS)
- [ ] Cloud Run (backend)
- [ ] Firebase Hosting (frontend)
- [ ] Cloud Tasks (async video jobs)
- [ ] Cloud TTS (video narration)
- [ ] Cloud Logging (monitoring)

---

## Appendix: Environment Variables

```bash
# backend/.env.example

# GCP / Gemini
GEMINI_API_KEY=your_gemini_api_key
GCP_PROJECT_ID=your_gcp_project_id
GCS_BUCKET_NAME=learnforge-files

# Firebase
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json

# Cloud Run / Tasks
BACKEND_URL=https://your-cloud-run-url.run.app
CLOUD_TASKS_QUEUE=video-generation
CLOUD_TASKS_LOCATION=us-central1

# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# App
ENVIRONMENT=development
MAX_FILE_SIZE_MB=20
FAISS_TOP_K=5
```

```bash
# frontend/.env.example

VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_FIREBASE_API_KEY=xxx
VITE_FIREBASE_AUTH_DOMAIN=xxx.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=xxx
VITE_FIREBASE_STORAGE_BUCKET=xxx.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=xxx
VITE_FIREBASE_APP_ID=xxx
```

---

*Document Version: 1.0 | Prepared for Google PromptWars Hackathon | LearnForge AI*
