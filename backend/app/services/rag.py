import os
import json
from typing import List, Dict, Any
from openai import OpenAI

def generate_training_recommendations(running_activities: List[Dict[str, Any]]):
    """Generate personalized training calendar using simplified AI analysis"""
    if not running_activities:
        return {"error": "No training data available"}
    
    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        return {
            "error": "OpenAI API key not configured",
            "message": "Calendar generation requires OpenAI API key"
        }
    
    try:
        # Analyze recent training patterns (last 2 weeks)
        recent_activities = running_activities[:14]
        
        # Create training summary
        total_distance = sum(act.get("distance", 0) for act in recent_activities) / 1000
        total_time = sum(act.get("moving_time", 0) for act in recent_activities) / 60
        
        # Create historical context from all activities
        historical_summary = f"Total activities: {len(running_activities)} runs\n"
        historical_summary += (f"Recent 2 weeks: {len(recent_activities)} runs, "
                               f"{total_distance:.1f}km, {total_time:.1f} minutes\n")
        
        # Add pace analysis
        paces = [act.get("moving_time", 0) / (act.get("distance", 1) / 1000)
                 for act in recent_activities if act.get("distance", 0) > 0]
        if paces:
            avg_pace_min_km = sum(paces) / len(paces)
            historical_summary += f"Average pace: {avg_pace_min_km:.1f} min/km\n"
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""
        Based on this runner's training data, generate a personalized weekly training calendar.
        
        Training Summary:
        {historical_summary}
        
        Generate a 7-day calendar with specific workout recommendations. Consider:
        - Recovery needs based on their training load
        - Intensity balance (easy vs hard runs)
        - Volume progression
        - Training consistency
        
        Return as JSON with this structure:
        {{
            "week_of": "2024-10-07",
            "days": [
                {{
                    "day": "Monday",
                    "date": "2024-10-07",
                    "workout": "Rest Day",
                    "reason": "Based on your recent high volume, you need recovery"
                }},
                {{
                    "day": "Tuesday",
                    "date": "2024-10-08",
                    "workout": "Easy Run - 5K at conversational pace",
                    "reason": "Focus on aerobic base building"
                }},
                {{
                    "day": "Wednesday",
                    "date": "2024-10-09",
                    "workout": "Rest Day",
                    "reason": "Recovery between training days"
                }},
                {{
                    "day": "Thursday",
                    "date": "2024-10-10",
                    "workout": "Tempo Run - 1K warmup, 3K at 5K pace, 1K cooldown",
                    "reason": "Structured speed work for improvement"
                }},
                {{
                    "day": "Friday",
                    "date": "2024-10-11",
                    "workout": "Rest Day",
                    "reason": "Recovery before weekend long run"
                }},
                {{
                    "day": "Saturday",
                    "date": "2024-10-12",
                    "workout": "Long Run - 10K at easy pace",
                    "reason": "Build endurance and aerobic capacity"
                }},
                {{
                    "day": "Sunday",
                    "date": "2024-10-13",
                    "workout": "Easy Run - 3K recovery pace",
                    "reason": "Active recovery after long run"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        try:
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
        except json.JSONDecodeError:
            return {"error": "Failed to generate recommendations"}
    
    except Exception as e:
        return {"error": f"AI system error: {str(e)}"}
