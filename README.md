# Civic Problem Solver

**Open-source AI concierge for local resource discovery**

Solving civic information fragmentation through intelligent, geo-fenced resource matching. Born from the Peoria AI Collective's December 3rd, 2025 civic problem-solving initiative.

## The Problem

**"Resources exist, people can't find them"** - Top challenge identified by Peoria-area residents

- Fragmented information across multiple websites
- No central hub for local resources  
- People don't know what's available to them
- Complex eligibility requirements hidden in bureaucracy

## The Solution

An AI-powered civic concierge that:
- **Understands your situation** through conversational intake
- **Knows local resources** through geo-fenced intelligence
- **Matches you to programs** based on eligibility criteria
- **Provides actionable next steps** to get help

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone https://github.com/thecuriousnobody/civic-problem-solver.git
cd civic-problem-solver

# Run automated setup
./setup.sh

# Edit .env file with your API keys
# Required: ANTHROPIC_API_KEY from https://console.anthropic.com
# Optional: SERPER_API_KEY from https://serper.dev
```

### Option 2: Manual Setup
```bash
# 1. Environment setup
cp .env.example .env
# Edit .env with your API keys

# 2. Backend
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python civic_api_v2.py

# 3. Frontend  
cd ../frontend
npm install
npm run dev
```

### Configuration

The system is highly configurable via `.env`:

- **MODEL_NAME**: `anthropic/claude-haiku-4-5-20251001` (fast) or `anthropic/claude-sonnet-4-20250514` (more capable)
- **MODEL_TEMPERATURE**: Lower = faster/consistent (0.1-0.3), Higher = creative (0.7-0.9)
- **SERPER_API_KEY**: Optional - enables live web search vs static resource database

## Architecture

```
Civic Resource AI
├── Intake Agent (understands user context)
├── Resource Agent (local knowledge database)  
├── Eligibility Agent (matches user to programs)
└── Action Agent (provides next steps)
```

## Designed for Replication

This is civic infrastructure, not a startup. Fork this repository and localize for your community:

1. **Update resource database** with local programs/services
2. **Configure geographic boundaries** for your area  
3. **Customize agent prompts** for local context
4. **Deploy and share** with your community

## Impact Vision

- **Immediate**: People get help today, not after navigating 15 websites
- **Data-driven**: See exactly where service gaps exist  
- **Scalable**: Template for every mid-size city in America

## Contributing

Built live during Peoria AI Collective meetings. Join us:
- **Slack**: [AI Collective Peoria]
- **Meetings**: Every 1st Wednesday, 6 PM CT
- **Issues**: Critique, add to, and push back on design ideas

---

*This project abstracts successful patterns from the [Distillery Labs Intake AI](https://github.com/thecuriousnobody/distillery-intake-ai) system.*