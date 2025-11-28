# Civic Problem Solver

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange.svg)](https://crewai.com)

**Open-source AI concierge for local resource discovery with radical transparency**

🔥 **Features:**
- **Streaming AI Transparency** - Watch agents think in real-time
- **2-Agent CrewAI System** - Intake + Resource specialists
- **Dual-Panel UI** - Chat + persistent resource accumulation
- **Local Focus** - Geo-fenced resource matching for your community
- **Production Ready** - Comprehensive testing & monitoring

Born from the Peoria AI Collective's civic problem-solving initiative.

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