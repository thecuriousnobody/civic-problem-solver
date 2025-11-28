#!/usr/bin/env python3
"""
Simple Civic API - Fast CrewAI Flow Implementation
================================================

Quick, demo-ready FastAPI server using CrewAI Flows
for civic resource discovery with user-provided API keys.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from civic_flow import run_civic_flow

app = FastAPI(
    title="Simple Civic Resource API",
    version="1.0.0", 
    description="Fast civic resource discovery using CrewAI Flows"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

# Request/Response Models
class CivicQueryRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None  # {"anthropic": "key", "serper": "key"}

class CivicQueryResponse(BaseModel):
    success: bool
    response: str
    resources: list
    conversation_stage: str
    needs_category: str
    location: str
    urgency_level: str
    response_time_ms: int
    timestamp: str
    session_id: str
    error: Optional[str] = None

class ConfigRequest(BaseModel):
    anthropic_api_key: str
    serper_api_key: Optional[str] = None

# Simple session storage (would use Redis/DB in production)
api_key_storage: Dict[str, Dict[str, str]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simple-civic-api",
        "timestamp": datetime.now().isoformat(),
        "flow_available": True
    }

@app.post("/api/configure")
async def configure_api_keys(request: ConfigRequest):
    """Store API keys for the session"""
    session_id = f"config_{int(datetime.now().timestamp())}"
    
    api_key_storage[session_id] = {
        "anthropic": request.anthropic_api_key,
        "serper": request.serper_api_key or ""
    }
    
    return {
        "session_id": session_id,
        "message": "API keys configured successfully",
        "has_search": bool(request.serper_api_key)
    }

@app.post("/api/query", response_model=CivicQueryResponse)
async def civic_query(request: CivicQueryRequest):
    """Main civic resource query endpoint using CrewAI Flows"""
    
    # Generate session ID if not provided
    session_id = request.session_id or f"civic_{int(datetime.now().timestamp())}"
    
    # Get API keys from request or storage
    api_keys = request.api_keys
    if not api_keys and session_id in api_key_storage:
        api_keys = api_key_storage[session_id]
    
    # Validate we have required API key
    if not api_keys or not api_keys.get('anthropic'):
        raise HTTPException(
            status_code=400, 
            detail="Anthropic API key required. Use /api/configure or include in request."
        )
    
    try:
        # Run the civic flow
        result = run_civic_flow(
            message=request.message,
            session_id=session_id,
            api_keys=api_keys
        )
        
        if result["success"]:
            return CivicQueryResponse(**result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flow execution error: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Get available resource categories"""
    return {
        "categories": [
            {"id": "housing", "name": "Housing", "description": "Affordable housing, emergency shelter, home repairs"},
            {"id": "food", "name": "Food Security", "description": "Food pantries, meal programs, SNAP assistance"},
            {"id": "transportation", "name": "Transportation", "description": "Public transit, paratransit, ride services"},
            {"id": "healthcare", "name": "Healthcare", "description": "Community health centers, free clinics, mental health"},
            {"id": "employment", "name": "Employment", "description": "Job training, career services, unemployment assistance"},
            {"id": "financial", "name": "Financial Aid", "description": "Emergency funds, bill assistance, benefits"},
            {"id": "legal", "name": "Legal Services", "description": "Legal aid, pro bono attorneys, court assistance"},
            {"id": "family_services", "name": "Family Services", "description": "Childcare, family support, parenting resources"},
            {"id": "elderly_services", "name": "Senior Services", "description": "Senior centers, aging services, elder care"}
        ],
        "locations": [
            {"id": "peoria_illinois", "name": "Peoria, IL"},
            {"id": "pekin_illinois", "name": "Pekin, IL"}, 
            {"id": "morton_illinois", "name": "Morton, IL"},
            {"id": "east_peoria_illinois", "name": "East Peoria, IL"},
            {"id": "central_illinois", "name": "Central Illinois"}
        ]
    }

@app.get("/api/demo")
async def demo_query():
    """Demo endpoint with sample data"""
    return {
        "sample_queries": [
            "I need emergency food assistance in Peoria",
            "Looking for affordable housing options", 
            "Need transportation help for medical appointments",
            "Single mom needing childcare resources",
            "Senior citizen looking for social services",
            "Unemployed, need job training programs"
        ],
        "expected_response_time": "2-5 seconds",
        "features": [
            "Real-time resource search",
            "Eligibility assessment", 
            "Contact information",
            "Next steps guidance"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)