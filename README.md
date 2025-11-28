# 🏛️ Civic Problem Solver

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange.svg)](https://crewai.com)

**AI-powered assistant that connects people to local civic resources using intelligent search and real-time transparency**

## 🎯 What This Is

This tool demonstrates how AI can solve civic problems by:
- **Connecting people to real local resources** with phone numbers they can actually call
- **Providing radical transparency** into AI decision-making through real-time tool usage visibility  
- **Extending to solve almost any civic problem** through modular agent design

**The Goal**: Create a foundation that communities can adapt to solve their specific civic challenges.

## ✨ Current Capabilities

✅ **Real-Time Streaming Interface** - Live progress updates as AI processes requests  
✅ **Tool Usage Transparency** - Infrastructure ready to show AI search activity  
✅ **2-Agent CrewAI System** - Intelligent intake + resource discovery  
✅ **Emergency Resource Discovery** - Actual phone numbers and addresses  
✅ **PostgreSQL Memory** - Maintains conversation context  
✅ **Production-Ready API** - FastAPI with streaming Server-Sent Events

Born from the Peoria AI Collective's civic problem-solving initiative.

## 🔧 Open Technical Challenges

*Perfect opportunities for community collaboration:*

### 1. **Search Tool Usage** 🎯 *High Priority*
- **Issue**: Agents use internal knowledge instead of live web search
- **Impact**: Missing real-time accuracy and search transparency  
- **What You'd See**: Tool events like "🔍 Searching: emergency housing Peoria Illinois"
- **Current**: Event listeners work, agents just need to use the search tool

### 2. **Resource Link Verification** 
- **Issue**: Some generated links may be inaccurate or outdated
- **Impact**: Users might get broken links or wrong phone numbers
- **Opportunity**: Implement link validation and phone number verification

### 3. **4-Agent System Integration** 🔧 *Architecture Enhancement*
- **Current**: Simplified 2-agent system in production 
- **Opportunity**: Integrate full 4-agent pipeline for better accuracy
- **Components Ready**: Individual agents exist, need orchestration layer
- **Benefit**: More nuanced eligibility assessment and action guidance

### 4. **Geographic Expansion**
- **Current**: Focused on Central Illinois/Peoria area
- **Opportunity**: Make location detection more robust for any city
- **Challenge**: How to verify local accuracy across different regions?

## 🌟 Why This Matters

This is **civic infrastructure**, not a startup. The pattern here can extend to:
- 🏥 **Healthcare Navigation**: "I need low-cost diabetes care"  
- ⚖️ **Legal Resource Finding**: "I'm facing eviction and need legal help"
- 👥 **Senior Services**: "My elderly parent needs home care assistance"
- 🌐 **Immigration Aid**: "I need help with citizenship application"

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
python endpoints/civic_api.py

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

## 🛠️ Architecture

```
frontend/                    # React UI with real-time streaming
├── src/CivicResourceAgent.tsx  # Main interface with tool transparency
└── ...

agents/                      # 4-Agent Modular System
├── intake_agent.py             # 🎯 User context & needs analysis
├── resource_agent.py           # 🗂️ Local knowledge & search  
├── eligibility_agent.py        # ✅ Program matching logic
├── action_agent.py             # 📋 Next steps & guidance
├── civic_crewai_system.py      # 🔧 Current 2-agent implementation
└── civic_flow.py               # 🌊 CrewAI Flow alternative

api/endpoints/               # Web API layer
├── civic_api.py               # FastAPI server with streaming
└── civic_chat_api.py          # Alternative endpoint

api/                        # Supporting infrastructure
├── requirements.txt           # Python dependencies  
└── config/                     # Agent configurations
```

### 4-Agent Modular Architecture

The system uses specialized agents working together:

#### 🎯 **Intake Agent** (`agents/intake_agent.py`)
- **Role**: Understands user context and civic needs
- **Function**: Conversational analysis to gather user information
- **Output**: Structured user profile and need categorization

#### 🗂️ **Resource Agent** (`agents/resource_agent.py`)
- **Role**: Local knowledge database and search
- **Function**: Knows programs, services, and organizations in the community
- **Output**: Relevant resource matches with contact information

#### ✅ **Eligibility Agent** (`agents/eligibility_agent.py`)
- **Role**: Program matching logic and qualification assessment
- **Function**: Determines user eligibility based on profile and program requirements
- **Output**: Filtered resources user actually qualifies for

#### 📋 **Action Agent** (`agents/action_agent.py`)
- **Role**: Next steps guidance and actionable advice
- **Function**: Provides clear, step-by-step instructions to access resources
- **Output**: Prioritized action plan with phone numbers and addresses

#### 🔧 **Current Implementation**
- **Active System**: `civic_crewai_system.py` (2-agent simplified version)
- **Alternative**: `civic_flow.py` (CrewAI Flow-based approach)
- **Ready for Expansion**: Individual agent modules can be combined for full 4-agent system

### Technical Foundation
- **Real-Time Streaming**: Server-Sent Events for live progress updates
- **Tool Event Listeners**: Infrastructure ready to show search tool usage 
- **PostgreSQL Memory**: Conversation context across sessions
- **Geographic Focus**: Central Illinois/Peoria (expandable template)

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

We welcome contributions! This project is designed to be replicated and adapted for communities worldwide.

### How to Contribute:
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and test thoroughly
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Ways to Help:
- 🐛 **Bug reports** - Found something broken? Let us know!
- ✨ **Feature requests** - Ideas for improvements
- 📖 **Documentation** - Help others understand and use the system
- 🌍 **Localization** - Adapt for your community's resources
- 🧪 **Testing** - Help ensure quality across different environments

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Community

Built live during Peoria AI Collective meetings. Join the conversation:
- **Slack**: [AI Collective Peoria](https://the-aicollective.slack.com)
- **Meetings**: Every 1st Wednesday, 6 PM CT
- **Issues**: [GitHub Issues](https://github.com/thecuriousnobody/civic-problem-solver/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Peoria AI Collective** - Community-driven civic innovation
- **CrewAI** - Multi-agent framework powering the system
- **Distillery Labs** - UI patterns and inspiration for transparency

---

**🌟 Star this repo if it helps your community!**

*Built with ❤️ for civic good. Made to be replicated, not monetized.*