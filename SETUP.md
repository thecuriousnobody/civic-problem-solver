# Civic Problem Solver - Setup Guide

## Quick Start (5 minutes)

### 1. Clone & Environment Setup
```bash
git clone https://github.com/thecuriousnobody/civic-problem-solver.git
cd civic-problem-solver
cp .env.example .env
```

### 2. Get API Keys
- **Anthropic API Key**: Visit [console.anthropic.com](https://console.anthropic.com)
- Add your key to `.env`: `ANTHROPIC_API_KEY=your_key_here`

### 3. Start Backend
```bash
cd api
pip install -r requirements.txt
python civic_chat_api.py
```

### 4. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### 5. Test It Out
- Open http://localhost:3000
- Try: *"I need help with food assistance in Peoria"*

## Customization for Your Community

### Update Resource Database
Edit `agents/resource_agent.py`:

```python
# Replace Peoria resources with your local programs
"housing": [
    {
        "name": "Your Local Housing Authority",
        "type": "Housing Assistance",
        "services": ["Affordable housing", "Housing vouchers"],
        "contact": {"phone": "(xxx) xxx-xxxx", "website": "https://..."},
        "eligibility": "Income limits apply",
        "geographic_area": "your_city"
    }
]
```

### Configure Geographic Areas
1. Update `DEFAULT_GEOGRAPHIC_SCOPE` in `.env`
2. Modify geographic logic in `agents/resource_agent.py`
3. Update location keywords in `agents/intake_agent.py`

## Advanced Setup

### Database Integration
Replace the in-memory resource database with:
- **Local**: SQLite with local government data
- **Cloud**: PostgreSQL with real-time API feeds
- **Hybrid**: Airtable/Notion for easy community updates

### AI Enhancement
- **Web Search**: Add `SERPER_API_KEY` for real-time resource discovery
- **Better Matching**: Implement vector similarity for resource matching
- **Multi-language**: Add translation support for diverse communities

### Production Deployment

#### Option 1: Railway (Recommended)
```bash
# Backend
railway login
railway link
railway up

# Frontend  
npm run build
railway deploy
```

#### Option 2: Vercel + Railway
- Frontend: Deploy to Vercel
- Backend: Deploy to Railway
- Update frontend API endpoint

## Testing

### Manual Testing Scenarios
1. **Housing Crisis**: "I'm about to be evicted and need emergency housing help"
2. **Food Insecurity**: "Single mom, need food assistance for my kids"
3. **Transportation**: "Disabled, need accessible transportation options"
4. **Employment**: "Recently unemployed, looking for job training programs"

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Chat test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need housing help", "session_id": "test_123"}'

# Resource search test  
curl -X POST http://localhost:8000/api/search-resources \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {"geographic_area": "peoria_illinois", "income_level": "low"}, 
    "need_categories": ["housing", "food_security"]
  }'
```

## Community Integration

### Data Sources to Integrate
- **Government**: City/county service directories
- **Nonprofits**: United Way, community foundations
- **Health**: FQHC directories, mental health resources  
- **Transportation**: Transit authorities, ride services
- **Legal**: Legal aid societies, pro bono directories

### Ongoing Maintenance
- **Monthly**: Update contact information and eligibility criteria
- **Quarterly**: Review and add new programs
- **Annually**: Assess effectiveness and expand coverage

## Troubleshooting

### Common Issues
- **"No resources found"**: Check geographic scope configuration
- **"API key error"**: Verify Anthropic API key in `.env`
- **Frontend won't load**: Ensure backend is running on port 8000

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/thecuriousnobody/civic-problem-solver/issues)
- **Community**: Join your local AI/civic tech meetup
- **Discussions**: Use GitHub Discussions for implementation questions

---

*Built during Peoria AI Collective meetings - fork and localize for your community!*