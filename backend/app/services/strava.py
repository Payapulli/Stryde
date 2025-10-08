import httpx
import os
from typing import List, Dict, Any

async def fetch_user_activities(access_token: str, max_pages: int = 10) -> List[Dict[str, Any]]:
    """Fetch user activities from Strava API"""
    all_activities = []
    page = 1
    per_page = 200
    
    async with httpx.AsyncClient() as client:
        while page <= max_pages:
            print(f"📥 Fetching page {page} of activities...")
            
            response = await client.get(
                "https://www.strava.com/api/v3/athlete/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"page": page, "per_page": per_page}
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch activities: {response.status_code} - {response.text}")
                break
            
            activities_batch = response.json()
            print(f"Got {len(activities_batch)} activities on page {page}")
            if not activities_batch:
                break
                
            all_activities.extend(activities_batch)
            page += 1
    
    return all_activities

async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange Strava authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": os.getenv("STRAVA_CLIENT_ID"),
                "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
                "code": code,
                "grant_type": "authorization_code"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

async def fetch_strava_user(access_token: str) -> Dict[str, Any]:
    """Fetch user profile from Strava API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch user: {response.status_code} - {response.text}")
