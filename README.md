<div align="center">

# 🤖 SkillSync AI

### *Your AI-Powered Career Intelligence Platform*

**Instantly analyze your skill gaps, build a personalized learning roadmap, and prepare for your dream company's interviews — all powered by GPT-4o.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-19-DD0031?style=for-the-badge&logo=angular)](https://angular.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/atlas)
[![OpenAI](https://img.shields.io/badge/GPT--4o-OpenAI-412991?style=for-the-badge&logo=openai)](https://openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Agents-1C3C3C?style=for-the-badge)](https://python.langchain.com/)

</div>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Tech Stack](#-tech-stack)
5. [Data Models](#-data-models)
6. [API Reference](#-api-reference)
7. [Project Structure](#-project-structure)
8. [Getting Started](#-getting-started)
9. [Environment Variables](#-environment-variables)
10. [User Flow](#-user-flow)
11. [AI Agent Design](#-ai-agent-design)
12. [Frontend Pages](#-frontend-pages)
13. [Known Limitations](#-known-limitations)

---

## 🎯 Project Overview

**SkillSync AI** is a full-stack, AI-native career development platform built for the modern job seeker. It solves a critical problem: **candidates don't know exactly what skills to learn, in what order, or how to prepare for a specific company's interview process.**

SkillSync bridges this gap by:

1. **Parsing** the target Job Description (JD) and the candidate's resume using GPT-4o structured output chains.
2. **Analyzing** the exact skill delta between what the role requires and what the candidate has, producing a scored gap report.
3. **Assessing** the candidate conversationally via a LangChain ReAct agent that asks tailored technical questions.
4. **Generating** a personalized, week-by-week learning plan with curated real-world resources sourced live from the web.
5. **Generating** a company-specific interview preparation guide that outlines every interview round with topics, tips, and practice links.

Everything persists to **MongoDB Atlas**, meaning each assessment session is fully resumable across browser sessions.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📄 **JD Ingestion** | Accept raw text, file upload (PDF/DOCX/TXT), or a public URL (with Tavily-powered extraction) |
| 📑 **Resume Parsing** | Deep extraction of candidate skills, years of experience, and evidence from PDF/DOCX |
| 📊 **Gap Analysis** | Per-skill scoring (0–100) with categories: STRONG / MODERATE / WEAK / MISSING |
| 💬 **Conversational Assessment** | Streaming SSE chat with a LangChain agent that adapts questions to the candidate's proficiency |
| 🗺️ **Learning Plan** | AI-generated curriculum with modules, topics, time estimates, and real resource URLs |
| 🎯 **Interview Prep** | Company-specific round-by-round guide with key topics, tips, and LeetCode/practice links |
| 🔁 **Session Persistence** | Full assessment state stored in MongoDB — resume any session from the sidebar |
| ⚡ **Real-time Streaming** | Server-Sent Events (SSE) for token-by-token AI response streaming in the chat UI |

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BROWSER (Angular 19)                         │
│  Landing → Workspace (Upload + Gap Analysis + Chat) →               │
│           Learning Plan Page → Interview Prep Page                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  HTTP / SSE  (port 4200 → 8000)
┌───────────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend  (port 8000)                      │
│                                                                      │
│   /api/sessions   → Session lifecycle management                     │
│   /api/upload     → JD + Resume ingestion & parsing chains          │
│   /api/analysis   → Gap Analysis LLM chain                          │
│   /api/chat       → LangChain ReAct Agent (SSE stream)              │
│   /api/learning-plan   → Learning Plan generation chain             │
│   /api/interview-prep  → Interview Prep generation chain            │
└──────┬──────────────────────────────────────────┬───────────────────┘
       │                                          │
┌──────▼──────┐                        ┌──────────▼───────────────────┐
│  MongoDB    │                        │  External AI Services        │
│  Atlas      │                        │                              │
│             │                        │  • OpenAI GPT-4o (LLM)       │
│  sessions   │                        │  • Tavily Search API         │
│  message_   │                        │    (Web search + extraction) │
│  store      │                        └──────────────────────────────┘
└─────────────┘
```

### Request Flow for Gap Analysis

```
User clicks "Generate Gap Analysis"
        │
        ▼
POST /api/analysis/generate
        │
        ▼
Load JD + Resume from MongoDB
        │
        ▼
GAP_ANALYZER_PROMPT → GPT-4o (structured JSON output via Pydantic)
        │
        ▼
Save GapAnalysis to session document
        │
        ▼
Return GapAnalysis → Frontend updates Signal state → UI re-renders
```

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Runtime |
| **FastAPI** | 0.115 | Async REST API framework |
| **Uvicorn** | 0.32 | ASGI server |
| **LangChain** | 0.3.28 | LLM orchestration framework |
| **LangChain-OpenAI** | 0.3.18 | GPT-4o integration |
| **LangChain-MongoDB** | 0.3.0 | MongoDB-backed chat message history |
| **Motor** | 3.7.1 | Async MongoDB driver |
| **PyMongo** | 4.10 | MongoDB queries |
| **Tavily Python** | 0.5.0 | AI-native web search & URL extraction |
| **PyPDF** | 5.1.0 | PDF text extraction |
| **Python-DOCX** | 1.1.2 | Word document text extraction |
| **BeautifulSoup4** | 4.12 | HTML parsing |
| **Pydantic** | 2.10 | Data validation & settings |
| **HTTPX** | 0.28 | Async HTTP client |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **Angular** | 19 | SPA framework (standalone components) |
| **TypeScript** | 5.x | Type-safe development |
| **RxJS** | 7.x | Reactive state via Observables |
| **Angular Signals** | 19 | Fine-grained reactive state for chat |
| **SCSS** | — | Glassmorphic design system |
| **Fetch API** | Native | SSE streaming for chat responses |

### Infrastructure

| Service | Purpose |
|---|---|
| **MongoDB Atlas** | Cloud NoSQL database for session persistence |
| **OpenAI API** | GPT-4o for all AI generation tasks |
| **Tavily API** | Real-time web search and URL content extraction |

---

## 📐 Data Models

All session data is stored in a single MongoDB document for efficient retrieval.

### Session Document Structure

```json
{
  "session_id": "uuid-v4",
  "status": "plan_generated",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",

  "jd_data": {
    "company_name": "Google",
    "role_title": "Senior Python Developer",
    "industry": "Technology",
    "experience_required": "5+ years",
    "required_skills": [
      { "name": "FastAPI", "importance": "must_have", "level": "advanced" },
      { "name": "Docker",  "importance": "must_have", "level": "intermediate" }
    ],
    "summary": "..."
  },

  "resume_data": {
    "candidate_name": "Robin",
    "email": "robin@example.com",
    "current_role": "Python Developer",
    "total_experience_years": 3.0,
    "skills": [
      { "name": "Python", "years_of_experience": 3.0, "level": "advanced", "evidence": ["..."] }
    ],
    "education": ["B.Tech Computer Science"],
    "summary": "..."
  },

  "gap_analysis": {
    "overall_match_score": 62,
    "skill_assessments": [
      {
        "skill_name": "FastAPI",
        "score": 15,
        "gap_category": "MISSING",
        "notes": "No evidence of FastAPI usage",
        "is_adjacent": true
      }
    ],
    "strengths": ["Python", "REST APIs"],
    "critical_gaps": ["FastAPI", "Kubernetes"],
    "adjacent_skills": ["Flask → FastAPI", "Docker → Kubernetes"],
    "recommended_focus_order": ["FastAPI", "Docker", "Kubernetes"]
  },

  "learning_plan": {
    "total_estimated_hours": 80,
    "completion_timeline_weeks": 6,
    "courses": [ { "skill_name": "FastAPI", "priority": 1, "modules": [...] } ]
  },

  "interview_prep": {
    "company_name": "Google",
    "role_title": "Senior Python Developer",
    "total_rounds": 5,
    "rounds": [ { "round_type": "System Design", "key_topics": [...], "preparation_tips": [...] } ],
    "general_tips": [...]
  }
}
```

### Session Status Lifecycle

```
created → jd_uploaded → resume_uploaded → analyzed → assessing → plan_generated → completed
```

---

## 🔌 API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

### Sessions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sessions` | Create a new assessment session |
| `GET` | `/sessions/{session_id}` | Get full session data |
| `GET` | `/sessions` | List all sessions |

### Upload

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/upload/jd` | `form-data`: `session_id`, `text` OR `url` OR `file` | Upload & parse Job Description |
| `POST` | `/upload/resume` | `form-data`: `session_id`, `file` (PDF/DOCX/TXT) | Upload & parse Resume |

### Analysis & Generation

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/analysis/generate` | `{ "session_id": "..." }` | Run Gap Analysis chain |
| `POST` | `/learning-plan/generate` | `{ "session_id": "..." }` | Generate personalized learning plan |
| `POST` | `/interview-prep/generate` | `{ "session_id": "..." }` | Generate company interview prep guide |

### Chat (SSE Streaming)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat/stream` | Stream AI assessment response (SSE) |
| `GET` | `/chat/{session_id}/history` | Get full chat message history |
| `DELETE` | `/chat/{session_id}/history` | Clear chat history for a session |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Backend health check |

---

## 📁 Project Structure

```
SkillSync-AI/
├── backend/
│   ├── .env                        # Environment variables (not committed)
│   ├── .env.example                # Template for environment variables
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker container definition
│   └── app/
│       ├── main.py                 # FastAPI app entry point, CORS, router registration
│       ├── config.py               # Pydantic Settings — loads from .env
│       ├── database.py             # Motor async MongoDB connection manager
│       ├── agent/
│       │   ├── skillsync_agent.py  # LangChain ReAct agent & SSE streaming logic
│       │   └── tools.py            # Tavily search + URL scraper tools
│       ├── api/routes/
│       │   ├── session.py          # Session CRUD endpoints
│       │   ├── upload.py           # JD + Resume upload & parsing endpoints
│       │   ├── chat.py             # SSE streaming chat endpoint
│       │   └── results.py          # Learning plan + Interview prep generation
│       ├── chains/
│       │   ├── jd_parser.py        # LLM chain: raw text → JDData (structured)
│       │   ├── resume_parser.py    # LLM chain: raw text → ResumeData (structured)
│       │   ├── gap_analyzer.py     # LLM chain: JD + Resume → GapAnalysis
│       │   ├── learning_plan.py    # LLM chain: Gap + Web search → LearningPlan
│       │   └── interview_prep.py   # LLM chain: Gap + Web search → InterviewPrep
│       ├── models/
│       │   ├── schemas.py          # All Pydantic data models (Session, JD, Gap, Plan...)
│       │   └── prompts.py          # All LLM system prompts
│       └── services/
│           └── file_service.py     # PDF/DOCX parsing + Tavily URL extraction
│
└── frontend/
    ├── package.json
    ├── angular.json
    └── src/
        ├── index.html
        ├── main.ts                 # Angular bootstrap
        ├── styles.scss             # Global glassmorphic design tokens
        └── app/
            ├── app.routes.ts       # SPA routing configuration
            ├── core/
            │   ├── models/
            │   │   └── types.ts    # TypeScript interfaces (Session, ChatMessage...)
            │   └── services/
            │       ├── api.service.ts      # All HTTP calls to the FastAPI backend
            │       └── session.service.ts  # Global session Signal state manager
            ├── pages/
            │   ├── landing/        # Home / hero page
            │   ├── workspace/      # Main assessment page (upload + analysis + chat)
            │   ├── learning-plan/  # Generated learning plan visualization
            │   └── interview-prep/ # Generated interview prep visualization
            └── shared/
                └── components/
                    ├── navbar/     # Top navigation + "New Assessment" button
                    └── sidebar/    # Session history drawer
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and **npm**
- A **MongoDB Atlas** cluster (free tier works)
- An **OpenAI API** key (GPT-4o access required)
- A **Tavily API** key (free tier at [tavily.com](https://tavily.com))

---

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd SkillSync-AI
```

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env with your API keys (see Environment Variables section below)

# Start the development server
venv\Scripts\uvicorn app.main:app --reload
```

The backend will be available at: `http://localhost:8000`
Interactive API docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the Angular dev server
npm start
```

The application will be available at: `http://localhost:4200`

---

### 4. Docker (Optional)

```bash
cd backend
docker build -t skillsync-backend .
docker run -p 8000:8000 --env-file .env skillsync-backend
```

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory based on `.env.example`:

```env
# ── OpenAI ─────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-...              # Your OpenAI API key
OPENAI_MODEL=gpt-4o                # Model to use (gpt-4o recommended)

# ── Tavily Web Search ───────────────────────────────────────────────
TAVILY_API_KEY=tvly-...            # Get free key at https://tavily.com

# ── MongoDB Atlas ───────────────────────────────────────────────────
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=skillsync          # Database name

# ── App Settings ────────────────────────────────────────────────────
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
MAX_UPLOAD_SIZE_MB=10
APP_ENV=development
```

> **Note:** Never commit your `.env` file. It is already in `.gitignore`.

---

## 🔄 User Flow

```
1. LAND
   └─► User visits SkillSync AI landing page

2. NEW ASSESSMENT
   └─► Click "New Assessment" → Creates session in MongoDB → Navigates to Workspace

3. UPLOAD JD
   └─► Paste text, or enter URL (Tavily extracts content), or upload file
   └─► GPT-4o parses → JDData stored in session

4. UPLOAD RESUME
   └─► Upload PDF / DOCX / TXT
   └─► GPT-4o parses → ResumeData stored in session

5. GAP ANALYSIS
   └─► Click "Generate Gap Analysis"
   └─► GPT-4o compares JD requirements vs candidate skills
   └─► Skill scores (0–100), gap categories, and match score displayed
   └─► Agent automatically starts the conversational assessment chat

6. CONVERSATIONAL ASSESSMENT (SSE Chat)
   └─► AI agent asks targeted questions per skill gap
   └─► Responses stream token-by-token via Server-Sent Events
   └─► Chat history persisted in MongoDB (message_store collection)

7. LEARNING PLAN
   └─► Click "View Learning Plan"
   └─► GPT-4o + Tavily web search → Structured curriculum generated
   └─► Modules, topics, time estimates, and real resource URLs displayed

8. INTERVIEW PREP
   └─► Click "View Interview Prep"
   └─► GPT-4o + Tavily research on company's specific interview process
   └─► Round-by-round breakdown with topics, tips, and practice links

9. RESUME SESSION
   └─► Use the sidebar (☰) to switch between past sessions at any time
```

---

## 🤖 AI Agent Design

### LLM Chains (Deterministic)

Used for structured data extraction. Each chain uses GPT-4o with **Pydantic structured output** to guarantee schema-valid JSON responses.

| Chain | Input | Output | Model |
|---|---|---|---|
| `jd_parser` | Raw JD text | `JDData` | GPT-4o |
| `resume_parser` | Raw resume text | `ResumeData` | GPT-4o |
| `gap_analyzer` | `JDData` + `ResumeData` | `GapAnalysis` | GPT-4o |
| `learning_plan` | `GapAnalysis` + Tavily search results | `LearningPlan` | GPT-4o |
| `interview_prep` | `GapAnalysis` + Tavily search results | `InterviewPrep` | GPT-4o |

### Assessment Agent (Agentic / Tool-Calling)

The chat system uses a **LangChain ReAct agent** (`create_openai_functions_agent`) with two tools:

- **`web_search`** — Tavily search for finding learning resources and company interview info.
- **`scrape_url`** — Fetches and parses full content from any URL.

Chat history is stored in **MongoDB** via `MongoDBChatMessageHistory` (LangChain-MongoDB integration), enabling full conversation persistence across browser refreshes.

The agent streams responses token-by-token using LangChain's `astream_events` API with `on_chat_model_stream` events, sent to the browser via **Server-Sent Events (SSE)**.

### Scoring Rubric

| Category | Score Range | Meaning | Study Time |
|---|---|---|---|
| **STRONG** | 80–100 | Candidate meets or exceeds requirement | — |
| **MODERATE** | 50–79 | Partially meets; minor upskilling needed | 1–2 weeks |
| **WEAK** | 25–49 | Basics present; significant gap | 3–4 weeks |
| **MISSING** | 0–24 | No evidence of this skill | 4–8 weeks |

---

## 🖥️ Frontend Pages

### Landing Page (`/`)
Hero section introducing SkillSync AI with feature highlights and a CTA to start an assessment.

### Workspace (`/workspace/:sessionId`)
The core two-panel assessment dashboard:
- **Left Panel:** Step-by-step setup (JD → Resume → Gap Analysis results with skill bars and match score)
- **Right Panel:** Real-time streaming chat with the AI assessment agent

### Learning Plan (`/learning-plan/:sessionId`)
Visual display of the AI-generated curriculum:
- Timeline and total study hours
- Course cards with priority levels
- Expandable modules and topics
- Clickable resource links (YouTube, articles, courses, documentation)

### Interview Prep (`/interview-prep/:sessionId`)
Company-specific interview preparation guide:
- Round-by-round breakdown
- Key topics and preparation tips per round
- Practice resource links

---

## 🎨 Design System

The frontend uses a custom **glassmorphic dark-mode** design system defined in `styles.scss`:

- `--bg-primary` / `--bg-secondary`: Deep dark backgrounds
- `--glass-bg` / `--glass-border`: Frosted glass card effect
- `--accent-primary`: Vibrant violet (`#7c3aed`)
- `--status-strong/moderate/weak/missing`: Skill category color coding
- All components use `backdrop-filter: blur()` for depth

---

## ⚠️ Known Limitations

| Limitation | Detail |
|---|---|
| **Enterprise ATS Job Portals** | Sites like Workday, Oracle Cloud HCM, and Greenhouse use WAF bot-protection. Direct URL extraction will fail for these — paste the JD text manually instead. |
| **Image-Based Resumes** | Resumes that are fully scanned images (no text layer) cannot be parsed. Use a text-based PDF or DOCX. |
| **OpenAI Rate Limits** | Generation chains are synchronous. High traffic may hit OpenAI API rate limits. |
| **Tavily Free Tier** | The Tavily free tier has limited monthly API credits. Monitor usage at [tavily.com](https://tavily.com). |

---

## 📄 License

This project was built for hackathon purposes. All rights reserved.

---

<div align="center">

**Built with ❤️ using FastAPI · LangChain · Angular · MongoDB · OpenAI GPT-4o**

</div>