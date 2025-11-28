#!/usr/bin/env python3
"""
Civic Problem Solver API - FastAPI endpoint for civic resource discovery
======================================================================

Main API endpoint that orchestrates all civic agents to provide
intelligent resource discovery and assistance.

Patterns from: distillery-intake-ai/api/unified_sarah_api.py
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Import our civic agents
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.intake_agent import CivicIntakeAgent
from agents.resource_agent import CivicResourceAgent
from agents.eligibility_agent import CivicEligibilityAgent
from agents.action_agent import CivicActionAgent

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Civic Problem Solver API", 
    version="1.0.0",
    description="AI-powered civic resource discovery for local communities"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

# Initialize agents
intake_agent = CivicIntakeAgent()
resource_agent = CivicResourceAgent()
eligibility_agent = CivicEligibilityAgent()
action_agent = CivicActionAgent()

# Request/Response Models
class CivicChatRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class CivicChatResponse(BaseModel):
    response: str
    session_id: str
    response_time_ms: int
    timestamp: str
    
    # User assessment
    needs_identified: List[str]
    user_profile: Dict[str, Any]
    follow_up_questions: List[str]
    ready_for_matching: bool
    
    # Resource matching (when ready)
    resources_found: List[Dict[str, Any]] = []
    action_plan: Optional[Dict[str, Any]] = None
    
    # Status indicators
    conversation_stage: str  # "intake", "clarification", "matching", "action_planning"

class ResourceSearchRequest(BaseModel):
    user_profile: Dict[str, Any]
    need_categories: List[str]
    geographic_scope: str = "peoria_illinois"

class ResourceSearchResponse(BaseModel):
    resources: List[Dict[str, Any]]
    total_found: int
    geographic_scope: str

# Session storage (would be replaced with proper database)
conversation_sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "civic-problem-solver",
        "timestamp": datetime.now().isoformat(),
        "agents_loaded": {
            "intake": bool(intake_agent),
            "resource": bool(resource_agent),
            "eligibility": bool(eligibility_agent),
            "action": bool(action_agent)
        }
    }

@app.post("/api/chat", response_model=CivicChatResponse)
async def civic_chat(request: CivicChatRequest):
    """
    Main chat endpoint - orchestrates all agents to provide civic assistance
    """
    start_time = datetime.now()
    
    try:
        # Get or create session
        session_data = conversation_sessions.get(request.session_id, {
            "conversation_history": [],
            "user_profile": {},
            "needs_identified": [],
            "stage": "intake"
        })
        
        # Add current message to history
        session_data["conversation_history"].append({
            "role": "user",
            "content": request.message,
            "timestamp": start_time.isoformat()
        })
        
        # Stage 1: Intake Assessment
        intake_result = intake_agent.assess_user_needs(
            request.message, 
            session_data["conversation_history"]
        )
        
        # Update session with assessment
        session_data["user_profile"].update(intake_result["user_profile"])
        session_data["needs_identified"].extend(intake_result["needs_identified"])
        
        response_text = ""
        resources_found = []
        action_plan = None
        stage = "intake"
        
        # Determine conversation stage and response
        if intake_result["ready_for_matching"]:
            stage = "matching"
            
            # Stage 2: Resource Discovery
            resources = resource_agent.search_resources(
                intake_result["needs_identified"], 
                session_data["user_profile"]
            )
            
            # Stage 3: Eligibility Assessment
            assessed_resources = eligibility_agent.assess_eligibility(
                session_data["user_profile"], 
                resources
            )
            
            # Stage 4: Action Planning
            action_plan = action_agent.generate_action_plan(
                assessed_resources, 
                session_data["user_profile"]
            )
            
            resources_found = assessed_resources
            response_text = action_plan["summary"]
            stage = "action_planning"
            
        else:
            # Continue intake process
            if intake_result["follow_up_questions"]:
                response_text = f"I'd like to understand your situation better. {intake_result['follow_up_questions'][0]}"
            else:
                response_text = "Thank you for sharing that information. What specific type of assistance are you looking for today?"
        
        # Add AI response to history
        session_data["conversation_history"].append({
            "role": "assistant", 
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        session_data["stage"] = stage
        conversation_sessions[request.session_id] = session_data
        
        # Calculate response time
        response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CivicChatResponse(
            response=response_text,
            session_id=request.session_id,
            response_time_ms=response_time_ms,
            timestamp=datetime.now().isoformat(),
            needs_identified=session_data["needs_identified"],
            user_profile=session_data["user_profile"],
            follow_up_questions=intake_result["follow_up_questions"],
            ready_for_matching=intake_result["ready_for_matching"],
            resources_found=resources_found,
            action_plan=action_plan,
            conversation_stage=stage
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/api/search-resources", response_model=ResourceSearchResponse)
async def search_resources(request: ResourceSearchRequest):
    """
    Direct resource search endpoint (for testing/debugging)
    """
    try:
        # Initialize resource agent with specified scope
        scoped_resource_agent = CivicResourceAgent(request.geographic_scope)
        
        # Search for resources
        resources = scoped_resource_agent.search_resources(
            request.need_categories,
            request.user_profile
        )
        
        return ResourceSearchResponse(
            resources=resources,
            total_found=len(resources),
            geographic_scope=request.geographic_scope
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching resources: {str(e)}")

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session data for debugging"""
    session_data = conversation_sessions.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "stage": session_data.get("stage", "unknown"),
        "needs_identified": session_data.get("needs_identified", []),
        "user_profile": session_data.get("user_profile", {}),
        "conversation_length": len(session_data.get("conversation_history", []))
    }

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/resources/categories")
async def get_resource_categories():
    """Get available resource categories"""
    return {
        "categories": [
            "housing",
            "food_security", 
            "transportation",
            "healthcare",
            "employment",
            "financial_assistance",
            "legal_aid",
            "education",
            "elderly_services",
            "family_services"
        ],
        "geographic_scopes": [
            "peoria_illinois",
            "pekin_illinois", 
            "morton_illinois",
            "east_peoria_illinois",
            "central_illinois"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)