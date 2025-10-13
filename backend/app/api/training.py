from fastapi import APIRouter, HTTPException, Query
from ..api.auth import user_sessions
from ..services.strava import fetch_user_activities
from ..services.analysis import calculate_weekly_volume, calculate_monthly_volume
from ..services.rag import generate_training_recommendations

router = APIRouter()

@router.get("/training/volume")
async def get_training_volume(state: str = Query(...), access_token: str = Query(None)):
    """Get user's training volume analysis (weekly and monthly)"""
    print(f"🔍 DEBUG: Training volume request - state: {state[:10]}..., access_token: {'present' if access_token else 'missing'}")
    print(f"🔍 DEBUG: User sessions count: {len(user_sessions)}")
    print(f"🔍 DEBUG: State in sessions: {state in user_sessions}")
    
    # Check authentication - either from session or direct token
    if access_token:
        # Direct token provided (from URL parameter)
        print(f"DEBUG: Using direct access token")
        token = access_token
    elif state in user_sessions and user_sessions[state]["authenticated"]:
        # Session-based authentication
        print(f"DEBUG: Using session-based token")
        token = user_sessions[state]["access_token"]
    else:
        print(f"DEBUG: Authentication failed - no token or invalid state")
        print(f"DEBUG: Available states: {list(user_sessions.keys())}")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Fetch activities from Strava
    activities = await fetch_user_activities(token)
    running_activities = [act for act in activities if act.get("type") == "Run"]
    
    # Calculate training volume by week and month
    weekly_volume = calculate_weekly_volume(running_activities)
    monthly_volume = calculate_monthly_volume(running_activities)
    
    # Generate personalized training calendar using RAG
    try:
        calendar = await generate_training_recommendations(running_activities)
    except Exception as e:
        print(f"⚠️ DEBUG: AI calendar generation failed: {e}")
        calendar = {"error": "AI service temporarily unavailable", "message": str(e)}
    
    return {
        "total_activities": len(running_activities),
        "weekly_volume": weekly_volume,
        "monthly_volume": monthly_volume,
        "calendar": calendar
    }
