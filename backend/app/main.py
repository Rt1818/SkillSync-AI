from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import connect_db, disconnect_db
from .api.routes import session, upload, chat, results


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()


app = FastAPI(
    title="SkillSync AI",
    description=(
        "AI-Powered Skill Assessment & Personalised Learning Plan Agent. "
        "Upload a JD + Resume, get a conversational skill assessment, "
        "personalized learning plan, and company-specific interview prep."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(session.router,  prefix=API_PREFIX)
app.include_router(upload.router,   prefix=API_PREFIX)
app.include_router(chat.router,     prefix=API_PREFIX)
app.include_router(results.router,  prefix=API_PREFIX)


# ── Health Check ──────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "SkillSync AI Backend"}


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "SkillSync AI",
        "version": "1.0.0",
        "docs": "/docs",
    }
