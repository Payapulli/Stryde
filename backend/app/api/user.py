from fastapi import APIRouter, HTTPException, Query
from ..api.auth import user_sessions

router = APIRouter()

@router.get("/user/profile")
async def get_user_profile(state: str = Query(...)):
    """Get user profile information"""
    # Check authentication
    if state not in user_sessions or not user_sessions[state]["authenticated"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user session data
    user_session = user_sessions[state]
    athlete = user_session["athlete"]
    
    return {
        "username": athlete.get("username", ""),
        "firstname": athlete.get("firstname", ""),
        "lastname": athlete.get("lastname", ""),
        "profile_medium": athlete.get("profile_medium", "")
    }
