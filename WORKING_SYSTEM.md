# 🟢 CIVIC PROBLEM SOLVER - WORKING SYSTEM 

**Last Updated: December 2, 2024**

## ✅ CONFIRMED WORKING CONFIGURATION

### Startup Command
```bash
./start-demo.sh
```

### Working Architecture
```
Frontend (Port 3000) ←→ Backend (Port 8001) ←→ CrewAI Agents ←→ Claude Haiku 4.5
     │                         │                      │
   React App           civic_api.py          civic_crewai_system.py
                   (/api/endpoints/)             (/agents/)
```

## 🔑 WORKING FILES

### ✅ Backend API (THE ONLY ONE THAT WORKS)
- **File**: `/api/endpoints/civic_api.py`
- **Port**: 8001
- **Features**: API key validation, debugging, crew integration

### ✅ CrewAI System
- **File**: `/agents/civic_crewai_system.py`
- **Model**: `anthropic/claude-haiku-4-5-20251001`
- **Features**: Verbose output, real web search, resource discovery

### ✅ Frontend
- **Port**: 3000
- **Features**: API key configuration, test button, edit button

### ✅ Individual Agents (Keep for Future)
- `/agents/intake_agent.py` ✅
- `/agents/resource_agent.py` ✅  
- `/agents/eligibility_agent.py` ✅
- `/agents/action_agent.py` ✅

## 🚫 BROKEN FILES (RENAMED TO .BROKEN)

### ❌ DO NOT USE THESE:
- `/api/simple_civic_api.py.BROKEN` - Causes "invalid x-api-key" errors
- `/agents/civic_flow.py.BROKEN` - Flow system issues

## 🔧 Setup Instructions

1. **Start System**: `./start-demo.sh`
2. **Open Browser**: http://localhost:3000
3. **Configure API Key**:
   - Click "EDIT KEYS"
   - Enter Anthropic API key from https://console.anthropic.com
   - Click "Test API Key" ✅
   - Click "Save Configuration"
4. **Test**: "I need food assistance in Peoria"

## 🎯 For AI Collective Demo Tomorrow

**What Works:**
- ✅ Real-time CrewAI agent conversations
- ✅ Live web search with Serper
- ✅ Resource discovery with phone numbers
- ✅ Verbose terminal output showing agent thinking
- ✅ API key testing and validation

**Demo Flow:**
1. Show startup: `./start-demo.sh`
2. Show API key configuration with test button
3. Show chat: "I need emergency housing in Peoria"
4. Show terminal: CrewAI agents searching and thinking
5. Show results: Real resources with phone numbers

**DO NOT TOUCH:**
- The working `civic_api.py` file
- The working `civic_crewai_system.py` file
- The working `start-demo.sh` script

## 📊 System Status

**✅ WORKING**: CrewAI agents, web search, resource discovery
**✅ WORKING**: API key validation and testing  
**✅ WORKING**: Frontend configuration UI
**✅ WORKING**: Verbose terminal output
**❌ BROKEN**: Flow-based systems (renamed to .BROKEN)