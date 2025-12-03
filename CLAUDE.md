# Civic Problem Solver - Working System Documentation

## ✅ CONFIRMED WORKING FILES (December 2024)

This is the **ONLY** configuration that works reliably:

### Backend API (Port 8001)
**File**: `/api/endpoints/civic_api.py`
- FastAPI server with streaming support
- API key validation and testing
- Health checks and error handling
- **Command**: Runs automatically via `./start-demo.sh`

### CrewAI Agents (Optimized System)
**File**: `/agents/civic_crewai_system.py` 
- 2-agent system: Intake Agent + Resource Agent
- **OPTIMIZED**: Exactly 3 targeted searches (was 15-16)
- **OPTIMIZED**: Direct output from resource agent (bypassed 4th agent)
- Model: `anthropic/claude-haiku-4-5-20251001`
- PostgreSQL conversation memory with fallback

### Frontend (Port 3000)
**File**: `/frontend/src/CivicResourceAgent.tsx`
- React interface with real-time streaming
- API key configuration and testing
- Split-panel UI (chat + resources)

### Startup Script
**File**: `./start-demo.sh`
- Starts backend on port 8001
- Starts frontend on port 3000
- **Usage**: `./start-demo.sh`

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd civic-problem-solver

# 2. Start the system
./start-demo.sh

# 3. Open browser
http://localhost:3000

# 4. Configure API keys (click "EDIT KEYS")
# Get from: https://console.anthropic.com

# 5. Test with: "I need food assistance in Peoria"
```

## 🔧 System Architecture

```
Frontend (3000) ←→ Backend (8001) ←→ CrewAI Agents ←→ Claude Haiku 4.5
     │                    │               │
   React UI         civic_api.py    civic_crewai_system.py
```

## ⚡ Recent Optimizations

1. **5x Faster**: Reduced from 15-16 searches to exactly 3 targeted searches
2. **Better Results**: Bypassed 4th agent that was discarding detailed search results
3. **Clean Codebase**: Removed broken/experimental files

## 🎯 For Development

**Key Files to Modify:**
- `civic_crewai_system.py` - Agent logic and search optimization
- `civic_api.py` - API endpoints and streaming
- `CivicResourceAgent.tsx` - UI and user experience

**Environment Variables:**
- `ANTHROPIC_API_KEY` - Required for CrewAI agents
- `SERPER_API_KEY` - Optional for web search
- `PORT` - Backend port (defaults to 8001)

**Dependencies:**
- `crewai[anthropic]` - Multi-agent framework
- `fastapi` - Backend API
- `react` - Frontend framework

## 📝 Notes

- System typically responds in 5-15 seconds
- PostgreSQL memory maintains conversation context
- Geographic focus: Central Illinois/Peoria
- Built for community replication and localization