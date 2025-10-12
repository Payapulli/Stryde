from fastapi import APIRouter, HTTPException, Query
from ..api.auth import user_sessions
from ..services.strava import fetch_user_activities
from ..services.analysis import calculate_weekly_volume, calculate_monthly_volume
from ..services.rag import generate_training_recommendations

router = APIRouter()

@router.get("/training/volume")
async def get_training_volume(state: str = Query(...), access_token: str = Query(None)):
    """Get user's training volume analysis (weekly and monthly)"""
    # Check authentication - either from session or direct token
    if access_token:
        # Direct token provided (from URL parameter)
        token = access_token
    elif state in user_sessions and user_sessions[state]["authenticated"]:
        # Session-based authentication
        token = user_sessions[state]["access_token"]
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Fetch activities from Strava
    activities = await fetch_user_activities(token)
    running_activities = [act for act in activities if act.get("type") == "Run"]
    
    # Calculate training volume by week and month
    weekly_volume = calculate_weekly_volume(running_activities)
    monthly_volume = calculate_monthly_volume(running_activities)
    
    # Generate personalized training calendar using RAG
    calendar = generate_training_recommendations(running_activities)
    
    return {
        "total_activities": len(running_activities),
        "weekly_volume": weekly_volume,
        "monthly_volume": monthly_volume,
        "calendar": calendar
    }
