import os

def get_base_url():
    """Get base URL for the application"""
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}"
    return "http://localhost:8000"
