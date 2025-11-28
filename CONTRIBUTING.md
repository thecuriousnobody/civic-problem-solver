# Contributing to Civic Problem Solver

## Vision

We're building civic infrastructure, not a startup. Every mid-size city deserves intelligent resource discovery for their residents.

## Ways to Contribute

### 🏛️ Civic Infrastructure
- **Localize for your city**: Fork and adapt resource databases
- **Share implementation stories**: Document your deployment experience  
- **Cross-city collaboration**: Help standardize resource data formats

### 🤖 AI & Technical Improvements
- **Better resource matching**: Improve eligibility algorithms
- **Multi-language support**: Make this accessible to diverse communities
- **Real-time data integration**: Connect to government API feeds
- **Mobile optimization**: Ensure accessibility on all devices

### 📊 Data & Research
- **Resource database expansion**: Add comprehensive local program data
- **Effectiveness tracking**: Build analytics to measure impact
- **Gap analysis**: Identify underserved populations and missing services
- **Privacy-first design**: Ensure user data protection

## Development Process

### 1. Local Development Setup
```bash
git clone https://github.com/thecuriousnobody/civic-problem-solver.git
cd civic-problem-solver

# Follow SETUP.md for complete instructions
cp .env.example .env
# Add your ANTHROPIC_API_KEY
```

### 2. Making Changes

#### For Resource Data Updates:
- Edit `agents/resource_agent.py` 
- Test with `python api/civic_chat_api.py`
- Submit PR with description of resources added/updated

#### For Code Changes:
- Create feature branch: `git checkout -b feature/your-improvement`
- Follow existing code patterns (see agents/ for examples)
- Test thoroughly with diverse user scenarios
- Update documentation if needed

#### For New City Implementations:
- Create city-specific fork or branch
- Update geographic configurations
- Document your resource collection process
- Share learnings back to main repository

### 3. Testing Your Changes

#### Manual Testing Scenarios
- **Crisis situations**: "I'm being evicted tomorrow"
- **Multiple needs**: "Need food, transportation, and job training"  
- **Specific demographics**: "Senior citizen", "disabled", "non-English speaker"
- **Geographic boundaries**: Test edge cases of service areas

#### Automated Testing
```bash
# Backend API tests
cd api
python -m pytest tests/

# Frontend component tests  
cd frontend
npm test
```

## Code Standards

### Agent Design Principles
- **Single Responsibility**: Each agent has one clear function
- **Conversational**: Natural language interactions, not forms
- **Accessible**: Work for users with varying tech literacy
- **Privacy-First**: Minimal data collection, local processing when possible

### Resource Data Standards
```python
{
    "name": "Program Name",
    "type": "Service Category", 
    "services": ["Specific", "Service", "List"],
    "contact": {"phone": "(xxx) xxx-xxxx", "website": "https://..."},
    "eligibility": "Clear, human-readable requirements",
    "geographic_area": "standardized_location_code"
}
```

### Frontend Accessibility
- **Keyboard navigation**: All interactions work without mouse
- **Screen reader friendly**: Proper ARIA labels and semantic HTML
- **Mobile responsive**: Touch-friendly interface
- **High contrast**: Readable for vision impairments

## Community Principles

### Open Source Civic Tech
- **Radical transparency**: All code, data sources, and decisions public
- **Community ownership**: Local implementations belong to their communities  
- **Shared learning**: Document failures and successes equally
- **Sustainable funding**: Design for long-term community maintenance

### Inclusive Development
- **Multiple perspectives**: Include diverse community voices in design
- **Cultural competency**: Respect local community differences
- **Language access**: Support non-English speakers
- **Digital equity**: Work on low-end devices and slow connections

## Current Priorities

### High Priority
1. **Resource database expansion**: More comprehensive local data
2. **Eligibility accuracy**: Better matching algorithms
3. **Mobile experience**: Optimize for phone usage
4. **Performance**: Sub-2-second response times

### Medium Priority  
1. **Multi-language support**: Spanish, other local languages
2. **Integration APIs**: Connect to existing civic tech tools
3. **Analytics dashboard**: Track usage and resource gaps
4. **Voice interface**: Accessibility for various abilities

### Future Vision
1. **Federated network**: City-to-city resource sharing
2. **Real-time updates**: Live program availability
3. **Predictive routing**: Anticipate user needs
4. **Impact measurement**: Quantify lives improved

## Getting Started

### First-Time Contributors
1. **Join community discussions**: Use GitHub Issues/Discussions
2. **Attend virtual meetups**: Monthly contributor calls
3. **Start small**: Fix documentation, update contact info
4. **Shadow deployments**: Help other cities implement

### Experienced Developers  
1. **Architecture reviews**: Help improve agent design
2. **Performance optimization**: Speed up resource matching
3. **Security audits**: Protect user privacy
4. **Scaling solutions**: Support high-traffic deployments

## Recognition

Contributors are acknowledged in:
- **Repository credits**: Listed in README
- **Community showcases**: Featured in meetup presentations  
- **Research papers**: Co-authored publications on civic AI
- **Conference talks**: Speaking opportunities at civic tech events

---

*This project was born from Peoria AI Collective meetings. Join us in building civic infrastructure that serves every community.*

## Contact

- **GitHub Issues**: Technical discussions and bug reports
- **Discussions**: Implementation questions and community chat
- **Email**: [civic-tech@example.org] for sensitive coordination
- **Slack**: [Join AI Collective Peoria] for real-time chat