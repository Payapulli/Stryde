from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import secrets
import os
from ..services.strava import exchange_code_for_token, fetch_strava_user

router = APIRouter()

# In-memory storage for demo (use proper database in production)
user_sessions = {}

def get_strava_redirect_uri():
    """Get Strava redirect URI - use localhost for local development"""
    # Check if we're running locally
    if os.getenv("VERCEL_URL") is None:
        return "http://localhost:8000/auth/callback"
    else:
        # Use the stable production URL
        return "https://backend-beta-ebon-86.vercel.app/auth/callback"

@router.get("/auth/strava")
async def strava_auth():
    """Initiate Strava OAuth flow"""
    state = secrets.token_urlsafe(32)
    user_sessions[state] = {"authenticated": False}
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={os.getenv('STRAVA_CLIENT_ID')}&"
        f"redirect_uri={get_strava_redirect_uri()}&"
        f"response_type=code&"
        f"scope=read,activity:read&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}

@router.get("/auth/callback")
async def strava_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Strava OAuth callback"""
    if state not in user_sessions:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    try:
        # Exchange code for token
        token_data = await exchange_code_for_token(code)
        access_token = token_data["access_token"]
        
        # Fetch user profile
        user_data = await fetch_strava_user(access_token)
        
        # Store user session
        user_sessions[state] = {
            "authenticated": True,
            "access_token": access_token,
            "athlete": user_data
        }
        
        # Redirect to frontend with success
        frontend_url = os.getenv("FRONTEND_URL", "https://frontend-beta-sandy-87.vercel.app")
        return RedirectResponse(url=f"{frontend_url}?auth_success=true&state={state}")
        
    except Exception as e:
        print(f"OAuth error: {e}")
        raise HTTPException(status_code=400, detail="OAuth failed")

@router.get("/oauth/authorize")
async def oauth_authorize(code: str = None, state: str = None):
    """Handle Strava OAuth redirect to /oauth/authorize (incorrect redirect)"""
    if code and state:
        # This is actually a callback, redirect to our callback handler
        return await strava_callback(code, state)
    else:
        # No parameters, redirect to frontend
        return RedirectResponse(url="https://stryde-ochre.vercel.app")
