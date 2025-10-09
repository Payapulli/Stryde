from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, user, training

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI()

@app.get("/debug/env-vars")
def debug_env_vars():
    return {
        "environment": os.getenv("VERCEL_ENV", "unknown"),
        "project": os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "unknown"),
        "client_id": os.getenv("STRAVA_CLIENT_ID"),
        "client_secret_prefix": os.getenv("STRAVA_CLIENT_SECRET", "")[:5],
        "openai_key_prefix": os.getenv("OPENAI_API_KEY", "")[:5],
    }

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stryde-ochre.vercel.app",
        "https://frontend-beta-sandy-87.vercel.app", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(training.router)

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {"message": "pong"}
