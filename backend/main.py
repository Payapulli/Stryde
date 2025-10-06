from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI()

# CORS middleware to allow frontend to communicate with backend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                 # local development
        "https://stryde-ochre.vercel.app",       # your production frontend
        "https://*.vercel.app"                   # allow all preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strava OAuth configuration
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "your_client_id_here")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "your_client_secret_here")

# Dynamic URL based on environment
def get_base_url():
    # Use custom BASE_URL if set, otherwise fall back to VERCEL_URL
    base_url = os.getenv("BASE_URL")
    if base_url:
        return base_url
    
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}"
    return "http://localhost:8000"

def get_strava_redirect_uri():
    """Get Strava redirect URI - use localhost for local dev, production for deployed"""
    # Use BASE_URL if explicitly set, otherwise use localhost for local dev
    if os.getenv("BASE_URL"):
        return f"{BASE_URL}/auth/callback"
    elif os.getenv("VERCEL_URL"):
        return f"https://{os.getenv('VERCEL_URL')}/auth/callback"
    else:
        # Local development - use localhost
        return "http://localhost:8000/auth/callback"

BASE_URL = get_base_url()
STRAVA_REDIRECT_URI = get_strava_redirect_uri()

# In-memory storage for demo (use proper database in production)
user_sessions = {}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/debug-sessions")
async def debug_sessions():
    """Debug endpoint to check sessions"""
    return {"sessions": list(user_sessions.keys()), "count": len(user_sessions)}

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
        f"scope=read,activity:read&"
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
            url=f"{FRONTEND_URL}?auth_success=true&state={state}"
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

@app.get("/training/volume")
async def get_training_volume(state: str):
    """Get user's training volume analysis (weekly and monthly)"""
    # Check authentication
    if state not in user_sessions or not user_sessions[state]["authenticated"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user session data
    user_session = user_sessions[state]
    access_token = user_session["access_token"]
    
    # Fetch activities from Strava
    activities = await fetch_user_activities(access_token)
    running_activities = [act for act in activities if act.get("type") == "Run"]
    
    # Calculate training volume by week and month
    weekly_volume = calculate_weekly_volume(running_activities)
    monthly_volume = calculate_monthly_volume(running_activities)
    
    return {
        "total_activities": len(running_activities),
        "weekly_volume": weekly_volume,
        "monthly_volume": monthly_volume
    }

async def fetch_user_activities(access_token: str, max_pages: int = 10) -> list:
    """Fetch user activities from Strava API"""
    all_activities = []
    page = 1
    per_page = 200
    
    async with httpx.AsyncClient() as client:
        while page <= max_pages:
            print(f"🔍 Fetching page {page} from Strava API...")
            response = await client.get(
                "https://www.strava.com/api/v3/athlete/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"per_page": per_page, "page": page}
            )
            
            print(f"📊 Strava API response: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Strava API error: {response.text}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to fetch activities: {response.status_code} - {response.text}"
                )
            
            activities_batch = response.json()
            print(f"📈 Got {len(activities_batch)} activities on page {page}")
            if not activities_batch:
                break
                
            all_activities.extend(activities_batch)
            page += 1
    
    print(f"✅ Total activities fetched: {len(all_activities)}")
    return all_activities

def calculate_weekly_volume(running_activities: list) -> dict:
    """Calculate weekly training volume"""
    from datetime import datetime, timedelta
    
    weekly_data = {}
    
    for activity in running_activities:
        # Parse activity date
        start_date = datetime.fromisoformat(activity.get("start_date", "").replace("Z", "+00:00"))
        
        # Get week start (Monday)
        week_start = start_date - timedelta(days=start_date.weekday())
        week_key = week_start.strftime("%Y-%m-%d")
        
        if week_key not in weekly_data:
            weekly_data[week_key] = {
                "week_start": week_key,
                "runs": 0,
                "distance_km": 0,
                "time_minutes": 0
            }
        
        weekly_data[week_key]["runs"] += 1
        weekly_data[week_key]["distance_km"] += activity.get("distance", 0) / 1000  # Convert to km
        weekly_data[week_key]["time_minutes"] += activity.get("moving_time", 0) / 60  # Convert to minutes
    
    # Sort by week and return last 8 weeks
    sorted_weeks = sorted(weekly_data.items(), key=lambda x: x[0], reverse=True)[:8]
    return [week_data for week_key, week_data in sorted_weeks]

def calculate_monthly_volume(running_activities: list) -> dict:
    """Calculate monthly training volume"""
    from datetime import datetime
    
    monthly_data = {}
    
    for activity in running_activities:
        # Parse activity date
        start_date = datetime.fromisoformat(activity.get("start_date", "").replace("Z", "+00:00"))
        
        # Get month key
        month_key = start_date.strftime("%Y-%m")
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_key,
                "runs": 0,
                "distance_km": 0,
                "time_minutes": 0
            }
        
        monthly_data[month_key]["runs"] += 1
        monthly_data[month_key]["distance_km"] += activity.get("distance", 0) / 1000  # Convert to km
        monthly_data[month_key]["time_minutes"] += activity.get("moving_time", 0) / 60  # Convert to minutes
    
    # Sort by month and return last 6 months
    sorted_months = sorted(monthly_data.items(), key=lambda x: x[0], reverse=True)[:6]
    return [month_data for month_key, month_data in sorted_months]

def calculate_best_efforts(running_activities: list) -> dict:
    """Calculate best efforts for target distances"""
    target_distances = [1609, 5000, 10000, 15000, 21097.5, 42195]
    best_efforts = {}
    
    for distance in target_distances:
        best_time = None
        best_activity = None
        
        # Check activities for close distances (±10%)
        for activity in running_activities:
            activity_distance = activity.get("distance", 0)
            moving_time = activity.get("moving_time", 0)
            
            if abs(activity_distance - distance) / distance <= 0.10:
                if best_time is None or moving_time < best_time:
                    best_time = moving_time
                    best_activity = activity
        
        # Check segment efforts for exact distances
        for activity in running_activities:
            segment_efforts = activity.get("segment_efforts", [])
            for segment_effort in segment_efforts:
                segment = segment_effort.get("segment", {})
                segment_distance = segment.get("distance", 0)
                elapsed_time = segment_effort.get("elapsed_time", 0)
                
                if segment_distance == distance:
                    if best_time is None or elapsed_time < best_time:
                        best_time = elapsed_time
                        best_activity = activity
        
        if best_time and best_activity:
            best_efforts[distance] = {
                "time_minutes": round(best_time / 60, 2),
                "elapsed_time": best_time,
                "distance": distance,
                "name": f"Best {distance}m",
                "start_date": best_activity.get("start_date", "")
            }
    
    return best_efforts
