from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, user, training

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI()

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
