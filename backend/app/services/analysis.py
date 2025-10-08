from datetime import datetime, timedelta
from typing import List, Dict, Any

def calculate_weekly_volume(running_activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate weekly training volume"""
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

def calculate_monthly_volume(running_activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate monthly training volume"""
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
