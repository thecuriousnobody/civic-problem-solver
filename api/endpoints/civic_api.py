#!/usr/bin/env python3
"""
Civic Resource API v2 - Sarah Martinez Pattern
==============================================

Simple FastAPI server using the new 2-agent CrewAI system with PostgreSQL memory.

Features:
- 2-agent system (Intake + Resource agents)
- PostgreSQL conversation memory
- Smart search decision making
- User-configurable API keys
- Health checks and CORS

Usage:
    python civic_api_v2.py
"""

import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

import sys
import os
# Add the agents directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
from civic_crewai_system import run_civic_chat, run_civic_chat_streaming

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CivicRequest(BaseModel):
    message: str
    session_id: str
    api_keys: Optional[Dict[str, str]] = None

class CivicResponse(BaseModel):
    success: bool
    response: str
    resources: List[Dict[str, Any]]
    session_id: str
    search_performed: bool
    need_category: Optional[str] = None
    urgency_level: Optional[str] = None
    response_source: Optional[str] = None
    timestamp: str
    error: Optional[str] = None

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Civic Resource API v2")
    logger.info("📊 Using 2-agent CrewAI system with PostgreSQL memory")
    yield
    logger.info("📴 Shutting down Civic Resource API v2")

app = FastAPI(
    title="Civic Resource API v2",
    description="2-agent CrewAI system for civic resource discovery with PostgreSQL memory",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "civic-resource-api-v2",
        "version": "2.0.0",
        "system": "2-agent-crewai-postgresql"
    }

@app.post("/api/test-key")
async def test_api_key(request: dict):
    """Test if Anthropic API key is valid"""
    try:
        import anthropic
        
        api_key = request.get('anthropic_key')
        if not api_key:
            return {"valid": False, "error": "No API key provided"}
        
        logger.info(f"Testing API key: {api_key[:15]}...")
        
        # Test with a simple completion
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'test'"}]
        )
        
        logger.info("✅ API key validation successful")
        return {"valid": True, "message": "API key works!"}
        
    except Exception as e:
        logger.error(f"❌ API key validation failed: {e}")
        return {"valid": False, "error": str(e)}

@app.post("/api/query", response_model=CivicResponse)
async def civic_query(request: CivicRequest):
    """
    Main endpoint for civic resource queries
    
    Handles:
    - Greetings and conversation
    - Specific civic resource needs
    - Context preservation across conversation
    - Smart search decision making
    """
    
    try:
        # Debug: Log what API keys we received
        logger.info(f"API keys received: {bool(request.api_keys)}")
        if request.api_keys:
            anthropic_key = request.api_keys.get('anthropic', '')
            logger.info(f"Anthropic key length: {len(anthropic_key)}")
            logger.info(f"Anthropic key preview: {anthropic_key[:15]}..." if anthropic_key else "No anthropic key")
        
        # Set API keys if provided
        if request.api_keys:
            if request.api_keys.get('anthropic'):
                os.environ['ANTHROPIC_API_KEY'] = request.api_keys['anthropic']
                logger.info("✅ Set ANTHROPIC_API_KEY from request")
            if request.api_keys.get('serper'):
                os.environ['SERPER_API_KEY'] = request.api_keys['serper']
                logger.info("✅ Set SERPER_API_KEY from request")
        
        # Check required API key
        current_key = os.getenv('ANTHROPIC_API_KEY', '')
        logger.info(f"Current ANTHROPIC_API_KEY length: {len(current_key)}")
        if not current_key:
            raise HTTPException(status_code=400, detail="Anthropic API key required")
        
        # Run civic chat
        result = await run_civic_chat(
            message=request.message,
            session_id=request.session_id
        )
        
        # Return structured response
        from datetime import datetime
        
        return CivicResponse(
            success=result['success'],
            response=result['response'],
            resources=result['resources'],
            session_id=result['session_id'],
            search_performed=result['search_performed'],
            need_category=result.get('need_category'),
            urgency_level=result.get('urgency_level'),
            response_source=result.get('response_source'),
            timestamp=datetime.now().isoformat(),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}", exc_info=True)
        
        return CivicResponse(
            success=False,
            response="I'm having trouble right now. For immediate help, call 211 - available 24/7.",
            resources=[],
            session_id=request.session_id,
            search_performed=False,
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@app.post("/api/query/stream") 
async def query_stream(request: CivicRequest):
    """Stream conversation progress with real-time updates"""
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Set API keys if provided
    if request.api_keys:
        if request.api_keys.get("anthropic"):
            os.environ["ANTHROPIC_API_KEY"] = request.api_keys["anthropic"]
        if request.api_keys.get("serper"):
            os.environ["SERPER_API_KEY"] = request.api_keys["serper"]
    
    async def generate_stream():
        """Generate Server-Sent Events stream"""
        
        # Track streaming events
        events = []
        
        def stream_callback(message: str):
            """Callback to capture streaming events"""
            event_data = {
                "type": "progress",
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            events.append(event_data)
            return f"data: {json.dumps(event_data)}\n\n"
        
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting civic resource search...'})}\n\n"
            
            # Execute streaming conversation
            result = await run_civic_chat_streaming(
                message=request.message,
                session_id=request.session_id,
                stream_callback=lambda msg: events.append({
                    "type": "progress", 
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                })
            )
            
            # Send progress events as they were captured
            for event in events:
                yield f"data: {json.dumps(event)}\n\n"
            
            # Send final result
            final_event = {
                "type": "complete",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(final_event)}\n\n"
            
        except Exception as e:
            logger.error(f"❌ Streaming failed: {e}")
            error_event = {
                "type": "error",
                "message": f"Error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/api/stats")
async def get_stats():
    """Get system statistics (optional - for monitoring)"""
    return {
        "system": "2-agent-crewai",
        "agents": {
            "intake_agent": "Conversation and decision making",
            "resource_agent": "Search and resource assembly"  
        },
        "memory": "PostgreSQL conversation history",
        "search": "Serper API integration",
        "status": "operational"
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "Please try again or call 211 for immediate assistance"
        }
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default
    port = int(os.getenv("PORT", 8001))
    
    logger.info(f"🌟 Starting Civic Resource API v2 on port {port}")
    logger.info(f"🔗 Health check: http://localhost:{port}/health")
    logger.info(f"📚 API docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )