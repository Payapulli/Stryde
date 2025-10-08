from fastapi import APIRouter, HTTPException, Query
from ..api.auth import user_sessions
from ..services.strava import fetch_user_activities
from ..services.analysis import calculate_weekly_volume, calculate_monthly_volume
from ..services.rag import generate_training_recommendations

router = APIRouter()

@router.get("/training/volume")
async def get_training_volume(state: str = Query(...)):
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
    
    # Generate personalized training calendar using RAG
    calendar = generate_training_recommendations(running_activities)
    
    return {
        "total_activities": len(running_activities),
        "weekly_volume": weekly_volume,
        "monthly_volume": monthly_volume,
        "calendar": calendar
    }
