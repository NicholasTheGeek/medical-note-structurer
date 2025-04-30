from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import time
import requests
import logging
import json
from datetime import datetime, timezone
from typing import Optional

# Configure logging for monitoring API activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Medical Notes API",
    description="API for structuring medical notes using LLM",
    version="1.0.0",
)

# CORS Configuration
origins = [
    "http://localhost:8501",  # Streamlit default port
    "http://localhost:3000",
    "http://127.0.0.1:8501",
]

# Middleware to handle CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model for incoming medical note
class MedicalNote(BaseModel):
    note: str = Field(..., description="The medical note to be processed")

# Define response model for structured medical information
class StructuredNote(BaseModel):
    symptoms: list[str] = Field(default_factory=list)  # List of symptoms
    diagnosis: str = Field(default="Unknown Diagnosis")  # Default diagnosis to avoid validation errors
    medication: list[str] = Field(default_factory=list)  # List of prescribed medications
    follow_up: str = Field(default="No follow-up required")  # Default follow-up instructions
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Define error response model
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Environment variables for the LLM configuration
LLAMA_URL = "http://localhost:11434/api/generate"
LLAMA_MODEL = "llama2"

def query_llama_with_retry(prompt: str, retries=3, delay=5) -> str:
    """
    Query the Llama model with retry logic to handle transient failures.
    """
    for attempt in range(retries):
        try:
            logger.info("Sending request to Llama API")
            response = requests.post(
                LLAMA_URL,
                json={
                    "model": LLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            
            if not result:
                logger.error("LLM returned an empty response")
                raise ValueError("Empty response from LLM")

            logger.info("Successfully received response from Llama API")
            return result
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Retry {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
    raise HTTPException(status_code=503, detail="Repeated LLM failures")

def parse_llm_response(response: str) -> dict:
    """
    Parses the JSON response from the LLM.
    Raises an error if the response is invalid.
    """
    try:
        structured_data = json.loads(response.strip())  # Convert response to JSON
        return structured_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        raise HTTPException(
            status_code=422,  # Unprocessable Entity error
            detail="Invalid JSON returned by LLM"
        )

@app.post("/extract/", response_model=StructuredNote)
async def extract_medical_info(note_data: MedicalNote):
    """
    Extracts structured information from a medical note using the LLM.
    """
    prompt = f"""
    You are a medical assistant extracting structured information. Read the medical note and return a valid JSON object with:
    - symptoms: List of all mentioned symptoms
    - diagnosis: Primary diagnosis or condition
    - medication: List of prescribed medications
    - follow_up: Any follow-up instructions or advice.

    Example input:
    "Patient complains of fatigue and joint pain. Diagnosed with rheumatoid arthritis. Prescribed methotrexate. Follow-up in 2 weeks."

    Example output:
    {{
        "symptoms": ["fatigue", "joint pain"],
        "diagnosis": "rheumatoid arthritis",
        "medication": ["methotrexate"],
        "follow_up": "Follow-up in 2 weeks"
    }}

    Medical note:
    \"\"\"{note_data.note}\"\"\"

    ONLY return the JSON object.
    """
    try:
        llm_response = query_llama_with_retry(prompt)  # Fetch response with retry logic
        structured_data = parse_llm_response(llm_response)  # Parse the response

        # Create response with validated data
        response = StructuredNote(
            symptoms=structured_data.get("symptoms", []),
            diagnosis=structured_data.get("diagnosis", "") or "Unknown Diagnosis",
            medication=structured_data.get("medication", []),
            follow_up=structured_data.get("follow_up", "") or "No follow-up required",
            processed_at=datetime.now(timezone.utc)
        )
        return response
    except HTTPException as http_exc:
        raise http_exc  # Reraise HTTP-specific exceptions
    except Exception as e:
        logger.error(f"Unexpected error: {e}")  # Log unexpected error
        raise HTTPException(
            status_code=500,  # Internal Server Error
            detail="Internal server error"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions and returns structured error responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handles unexpected exceptions and provides detailed error messages.
    """
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.get("/health")
async def health_check():
    """
    Returns the health status of the API.
    """
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run the app on port 8000