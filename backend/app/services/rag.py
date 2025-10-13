import os
import json
import httpx
from typing import List, Dict, Any
from openai import OpenAI

# Hugging Face configuration - using a more reliable model
HF_MODEL = "distilbert-base-uncased"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

async def query_huggingface(prompt: str) -> str:
    """Send a prompt to the Hugging Face Inference API."""
    HF_TOKEN = os.getenv("STRYDE_HF_TOKEN")
    if not HF_TOKEN:
        raise RuntimeError("Missing STRYDE_HF_TOKEN environment variable")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(HF_API_URL, headers=headers, json=payload)

    print(f"DEBUG: HF response status: {response.status_code}")
    print(f"DEBUG: HF response headers: {dict(response.headers)}")
    print(f"DEBUG: HF response text: {response.text[:500]}...")

    # Parse response safely
    try:
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        print(f"DEBUG: HF parsed data: {data}")
        
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        elif isinstance(data, dict) and "error" in data:
            raise RuntimeError(f"Hugging Face API error: {data['error']}")
        else:
            return str(data)
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON decode error: {e}")
        print(f"DEBUG: Raw response: {response.text}")
        raise RuntimeError(f"Error parsing Hugging Face response: {e}. Raw response: {response.text}")
    except Exception as e:
        raise RuntimeError(f"Error parsing Hugging Face response: {e}")

def generate_simple_training_plan(avg_distance: float, weekly_volume: float, historical_summary: str) -> dict:
    """Generate a simple training plan without external APIs"""
    # Calculate appropriate distances based on current fitness
    base_distance = max(3.0, avg_distance * 0.8)  # Slightly less than average
    long_run_distance = max(5.0, avg_distance * 1.5)  # Longer than average
    interval_distance = max(2.0, avg_distance * 0.6)  # Shorter, faster
    
    return {
        "week_plan": [
            {"day": "Monday", "workout": "Easy Run", "distance": f"{base_distance:.1f}km", "effort": "Easy", "notes": "Recovery pace"},
            {"day": "Tuesday", "workout": "Interval Training", "distance": f"{interval_distance:.1f}km", "effort": "Hard", "notes": "5x800m at 5K pace"},
            {"day": "Wednesday", "workout": "Rest", "distance": "0km", "effort": "Rest", "notes": "Active recovery or complete rest"},
            {"day": "Thursday", "workout": "Easy Run", "distance": f"{base_distance:.1f}km", "effort": "Easy", "notes": "Conversational pace"},
            {"day": "Friday", "workout": "Tempo Run", "distance": f"{base_distance:.1f}km", "effort": "Moderate", "notes": "20 min at half marathon pace"},
            {"day": "Saturday", "workout": "Long Run", "distance": f"{long_run_distance:.1f}km", "effort": "Easy", "notes": "Build endurance"},
            {"day": "Sunday", "workout": "Easy Run", "distance": f"{base_distance:.1f}km", "effort": "Easy", "notes": "Recovery run"}
        ],
        "weekly_total": f"{weekly_volume:.1f}km",
        "focus": "Building base fitness and endurance",
        "progression": "Gradually increase long run distance by 1-2km weekly",
        "source": "Generated based on your training data"
    }

async def generate_training_recommendations(running_activities: List[Dict[str, Any]]):
    """Generate personalized training calendar using Hugging Face AI"""
    print(f"DEBUG: RAG service called with {len(running_activities)} activities")
    
    if not running_activities:
        print("DEBUG: No running activities provided")
        return {"error": "No training data available"}
    
    try:
        # Analyze recent training patterns (last 2 weeks)
        recent_activities = running_activities[:14]
        
        # Create training summary
        total_distance = sum(act.get("distance", 0) for act in recent_activities) / 1000
        total_time = sum(act.get("moving_time", 0) for act in recent_activities) / 60
        
        # Calculate averages for prompt
        avg_distance = total_distance / len(recent_activities) if recent_activities else 0
        weekly_volume = total_distance / 2  # 2 weeks of data
        
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
        
        # Generate recommendations using Hugging Face (with fallback)
        print(f"DEBUG: Creating Hugging Face prompt...")
        
        prompt = f"""Create a 7-day running training plan for a runner who averages {avg_distance:.1f}km per run and runs {weekly_volume:.1f}km per week. 

Recent training: {historical_summary}

Generate a structured weekly plan with easy runs, intervals, tempo runs, and a long run. Include rest days and progression. Format as JSON with day, workout type, distance, and effort level."""
        
        try:
            print(f"DEBUG: Making API call to Hugging Face...")
            plan_text = await query_huggingface(prompt)
            
            print(f"DEBUG: Hugging Face API call successful!")
            print(f"DEBUG: Response received: {len(plan_text)} characters")
            
            try:
                recommendations = json.loads(plan_text)
                print(f"DEBUG: Successfully parsed JSON response")
                return recommendations
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON parsing failed: {e}")
                return {"error": "Failed to generate recommendations", "raw_response": plan_text}
        except Exception as hf_error:
            print(f"DEBUG: Hugging Face API failed: {hf_error}")
            print(f"DEBUG: Falling back to simple training plan...")
            
            # Fallback: Generate a simple training plan
            return generate_simple_training_plan(avg_distance, weekly_volume, historical_summary)
    
    except Exception as e:
        print(f"DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
        return {"error": f"AI system error: {str(e)}"}
