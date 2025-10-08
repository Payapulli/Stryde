from pydantic import BaseModel
from typing import Optional, Dict, Any

class UserSession(BaseModel):
    authenticated: bool
    access_token: str
    athlete: Dict[str, Any]

class UserProfile(BaseModel):
    username: str
    firstname: str
    lastname: str
    profile_medium: Optional[str] = None
