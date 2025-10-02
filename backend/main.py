from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import os
import secrets
from typing import Optional

app = FastAPI()

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strava OAuth configuration
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "your_client_id_here")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "your_client_secret_here")
STRAVA_REDIRECT_URI = "http://localhost:8000/auth/callback"

# In-memory storage for demo (use proper database in production)
user_sessions = {}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/auth/strava")
async def strava_auth():
    """Initiate Strava OAuth flow"""
    state = secrets.token_urlsafe(32)
    
    # Store state for verification
    user_sessions[state] = {"authenticated": False}
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={STRAVA_CLIENT_ID}&"
        f"redirect_uri={STRAVA_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=read&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}

@app.get("/auth/callback")
async def strava_callback(code: str, state: str):
    """Handle Strava OAuth callback"""
    if state not in user_sessions:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": STRAVA_CLIENT_ID,
                "client_secret": STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data["access_token"]
        
        # Get athlete info
        athlete_response = await client.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if athlete_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get athlete info")
        
        athlete_data = athlete_response.json()
        
        # Store user session
        user_sessions[state] = {
            "authenticated": True,
            "access_token": access_token,
            "athlete": athlete_data
        }
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"http://localhost:5173?auth_success=true&state={state}"
        )

@app.get("/user/profile")
async def get_user_profile(state: str):
    """Get authenticated user's profile"""
    if state not in user_sessions or not user_sessions[state]["authenticated"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "username": user_sessions[state]["athlete"]["username"],
        "firstname": user_sessions[state]["athlete"]["firstname"],
        "lastname": user_sessions[state]["athlete"]["lastname"],
        "profile_medium": user_sessions[state]["athlete"]["profile_medium"]
    }
