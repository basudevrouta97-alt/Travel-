# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "openai",
#   "pydantic",
#   "python-dotenv"
# ]
# ///

# =====================================================================
# TRAVELVOICE AI - CORE BACKEND CODE
# =====================================================================

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="TravelVoice AI Backend")

# OpenAI Client Initialize karein
# Make sure aapne .env me ya device me OPENAI_API_KEY set kiya hai
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Data Models (Request aur Response ke liye)
class UserCommand(BaseModel):
    text: str  # User ne jo bola (e.g., "Kolkata se Hyderabad jana hai kal subah")

class TravelDetails(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = None
    stay_required: bool = False
    duration_days: Optional[int] = 1

# --- AI LAYER: User ki baat se Data Extract karna ---
def extract_travel_info(user_text: str) -> TravelDetails:
    prompt = f"""
    You are the AI backend of TravelVoice AI. Extract travel details from this user query.
    Query: "{user_text}"
    
    Extract:
    1. Source city
    2. Destination city
    3. Date of travel
    4. Is a hotel stay required? (True/False)
    """
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract structured travel data from unstructured text."},
                {"role": "user", "content": prompt}
            ],
            response_format=TravelDetails,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Error extracting data: {e}")
        return TravelDetails()

# --- MOCK DATA: Flights aur Hotels ---
def get_mock_flights(source, dest):
    return [
        {"flight_id": "TV-101", "airline": "IndiGo", "departure": "06:45", "arrival": "09:00", "price": 4500},
        {"flight_id": "TV-202", "airline": "Air India", "departure": "10:20", "arrival": "12:45", "price": 5200}
    ]

def get_mock_hotels(city):
    return [
        {"hotel_name": "The Azure Sanctuary", "location": f"Central {city}", "rating": 4.9, "price_per_night": 3500},
        {"hotel_name": "Onyx Garden Hotel", "location": f"Premium District, {city}", "rating": 4.7, "price_per_night": 4200}
    ]

# --- API ENDPOINTS ---

@app.post("/process-voice/")
async def process_voice_command(command: UserCommand):
    if not command.text:
        raise HTTPException(status_code=400, detail="Command text cannot be empty")
    
    # 1. AI se text parsing karwayein
    travel_info = extract_travel_info(command.text)
    
    if not travel_info.destination:
        return {
            "ai_response": "Mujhe aapki destination samajh nahi aayi. Aap kahan jana chahte hain?",
            "action_required": "ask_destination"
        }
    
    # 2. Flight aur Hotel search simulate karein
    flights = get_mock_flights(travel_info.source or "Current Location", travel_info.destination)
    hotels = []
    
    if travel_info.stay_required:
        hotels = get_mock_hotels(travel_info.destination)
        ai_message = f"Maine {travel_info.destination} ke liye flights aur hotels dhoond liye hain. Kya mai booking confirm karu?"
    else:
        ai_message = f"Maine {travel_info.destination} ke liye flights check kar li hain. Dekhiye:"

    # 3. Final Response setup karein (Jaisa aapke UI screens me dikh raha hai)
    return {
        "ai_response": ai_message,
        "extracted_data": travel_info,
        "results": {
            "flights": flights,
            "hotels": hotels
        }
    }

@app.post("/confirm-booking/")
async def confirm_booking():
    return {
        "status": "Success",
        "message": "Aapki booking successfully confirm ho gayi hai! Ticket download karne ke liye niche click karein.",
        "ticket_id": "TICKET123456"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
