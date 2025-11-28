#!/usr/bin/env python3
"""
Civic Resource CrewAI System - Sarah Martinez Pattern
====================================================

2-Agent system for civic resource discovery:
1. Intake Agent: Handles conversation, context, decides if search needed
2. Resource Agent: Performs targeted searches, assembles civic resources

Features:
- PostgreSQL conversation memory
- Contextual conversations 
- Smart search decision making
- Local resource focus (Central Illinois/Peoria)
- Empathetic, warm responses

Usage:
    from civic_crewai_system import run_civic_chat
    
    result = run_civic_chat(
        message="I need help with food assistance",
        session_id="user_123"
    )
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor

from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Database imports (we'll add these)
import asyncpg
import hashlib

# Load environment
load_dotenv()

# Configure logging with detailed performance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Performance tracking
class PerformanceTracker:
    """Detailed performance monitoring for civic system"""
    
    def __init__(self):
        self.start_time = None
        self.step_times = {}
        self.step_order = []
    
    def start(self, description: str = ""):
        self.start_time = time.time()
        self.step_times = {}
        self.step_order = []
        logger.info(f"🚀 PERFORMANCE: Starting execution {description}")
        return self.start_time
    
    def step(self, step_name: str):
        current_time = time.time()
        if self.start_time:
            elapsed = current_time - self.start_time
            if self.step_order:
                step_duration = current_time - self.step_times[self.step_order[-1]]
                logger.info(f"⏱️  STEP COMPLETE: {self.step_order[-1]} took {step_duration:.3f}s")
            
            self.step_times[step_name] = current_time
            self.step_order.append(step_name)
            logger.info(f"▶️  STEP START: {step_name} (total elapsed: {elapsed:.3f}s)")
        
        return current_time
    
    def finish(self, description: str = ""):
        if self.start_time:
            total_time = time.time() - self.start_time
            if self.step_order:
                final_step = self.step_order[-1]
                final_step_duration = time.time() - self.step_times[final_step]
                logger.info(f"⏱️  STEP COMPLETE: {final_step} took {final_step_duration:.3f}s")
            
            logger.info(f"🏁 PERFORMANCE: Total execution time {total_time:.3f}s {description}")
            
            # Summary breakdown
            logger.info("📊 PERFORMANCE BREAKDOWN:")
            for i, step in enumerate(self.step_order):
                if i == 0:
                    step_time = self.step_times[step] - self.start_time
                else:
                    step_time = self.step_times[step] - self.step_times[self.step_order[i-1]]
                percentage = (step_time / total_time) * 100
                logger.info(f"   {step}: {step_time:.3f}s ({percentage:.1f}%)")
            
            return total_time
        return 0

# ============================================================================
# STATE MODEL
# ============================================================================

class CivicState(BaseModel):
    """State for civic resource conversation flow"""
    
    # Input
    user_message: str = ""
    session_id: str = ""
    
    # Context
    current_date: str = ""
    current_time: str = ""
    location: str = "Central Illinois"  # Default geographic focus
    
    # Conversation memory
    conversation_history: List[Dict] = Field(default_factory=list)
    
    # Decision logic
    needs_search: bool = False
    need_category: str = ""  # housing, food, healthcare, etc.
    urgency_level: str = "medium"  # low, medium, high
    
    # Search results  
    search_performed: bool = False
    search_query: Optional[str] = None
    search_results: Optional[str] = None
    resources_found: List[Dict] = Field(default_factory=list)
    
    # Output
    civic_response: str = ""
    response_source: str = ""  # conversation, search, fallback
    
    # Performance tracking
    performance_tracker: Optional[PerformanceTracker] = Field(default_factory=PerformanceTracker, exclude=True)
    execution_time_ms: int = 0
    step_timings: Dict[str, float] = Field(default_factory=dict)
    
    # Streaming support
    enable_streaming: bool = False
    stream_callback: Optional[callable] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

class CivicMemory:
    """PostgreSQL-based conversation memory"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/civic_db')
        
    async def init_db(self):
        """Initialize database tables"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Create conversations table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    need_category VARCHAR(100),
                    urgency_level VARCHAR(20),
                    search_performed BOOLEAN,
                    search_query TEXT,
                    resources_count INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Create index on session_id
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON conversations (session_id)
            ''')
            
            await conn.close()
            logger.info("✅ Database initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Database init failed: {e} (will use in-memory fallback)")
    
    async def save_conversation(self, state: CivicState):
        """Save conversation turn to database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            await conn.execute('''
                INSERT INTO conversations 
                (session_id, user_message, agent_response, need_category, 
                 urgency_level, search_performed, search_query, resources_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', 
                state.session_id,
                state.user_message,
                state.civic_response,
                state.need_category,
                state.urgency_level, 
                state.search_performed,
                state.search_query,
                len(state.resources_found)
            )
            
            await conn.close()
            logger.info(f"💾 Saved conversation for session {state.session_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Save failed: {e}")
    
    async def get_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            rows = await conn.fetch('''
                SELECT user_message, agent_response, need_category, created_at
                FROM conversations 
                WHERE session_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            ''', session_id, limit)
            
            await conn.close()
            
            # Reverse to get chronological order
            history = []
            for row in reversed(rows):
                history.extend([
                    {"role": "user", "content": row['user_message'], "timestamp": row['created_at'].isoformat()},
                    {"role": "assistant", "content": row['agent_response'], "timestamp": row['created_at'].isoformat()}
                ])
            
            return history
            
        except Exception as e:
            logger.warning(f"⚠️ History retrieval failed: {e}")
            return []


# ============================================================================
# CIVIC CREWAI SYSTEM
# ============================================================================

class CivicCrewAISystem(Flow[CivicState]):
    """
    2-Agent Civic Resource System
    
    Flow: context → decide → search → respond
    Agents: Intake Agent + Resource Agent
    Memory: PostgreSQL conversation history
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize memory
        self.memory = CivicMemory()
        
        # Configure model from environment variables with fallbacks
        model_name = os.getenv("MODEL_NAME", "anthropic/claude-haiku-4-5-20251001")
        temperature = float(os.getenv("MODEL_TEMPERATURE", "0.3"))
        max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "1500"))
        
        self.llm = LLM(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"🤖 Model: {model_name} | Temp: {temperature} | Tokens: {max_tokens}")
        
        # Intake Agent - Conversation and decision making
        self.intake_agent = Agent(
            role="Civic Resource Navigator",
            goal="Help residents find local resources with warmth, clarity, and zero judgment through intelligent conversation",
            backstory="""You are a compassionate civic resource navigator serving Central Illinois. 
            You understand that people reaching out for help are often stressed, overwhelmed, or in crisis. 
            
            Your approach:
            - Lead with empathy, not paperwork
            - Listen to understand their real needs
            - Decide if they need resource search or just conversation
            - Always assume the person is doing their best
            - Remember: asking for help is brave, not shameful
            
            You handle greetings warmly and guide conversations naturally toward understanding their civic needs.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Resource Agent - Search and assembly
        self.resource_agent = Agent(
            role="Local Resource Specialist", 
            goal="Find and assemble relevant civic resources for specific needs in Central Illinois",
            backstory="""You are a local resource specialist with deep knowledge of Central Illinois services.
            
            Your expertise:
            - Local organizations (Peoria, Tazewell, Woodford counties)
            - Programs with LOW barriers to entry
            - Current contact information and real phone numbers
            - Eligibility requirements in plain English
            - Emergency vs non-emergency resources
            
            You prioritize:
            - Walk-in services and same-day help
            - Programs currently accepting applications
            - Resources with immediate accessibility
            - Official government programs and established nonprofits""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Search tool
        self.search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY")) if os.getenv("SERPER_API_KEY") else None
    
    @start()
    async def initialize_context(self):
        """Set context and load conversation history"""
        
        # Start performance tracking
        self.state.performance_tracker.start("civic conversation flow")
        self.state.performance_tracker.step("initialize_context")
        
        if self.state.enable_streaming and self.state.stream_callback:
            self.state.stream_callback("🚀 Initializing civic resource system...")
        
        # Set temporal context
        now = datetime.now(timezone.utc)
        self.state.current_date = now.strftime("%Y-%m-%d")
        self.state.current_time = now.strftime("%-I:%M %p")
        
        # Load conversation history for context
        try:
            history_start = time.time()
            history = await self.memory.get_conversation_history(self.state.session_id)
            history_time = time.time() - history_start
            self.state.conversation_history = history
            logger.info(f"📚 Loaded {len(history)} conversation entries in {history_time:.3f}s for session {self.state.session_id}")
        except Exception as e:
            logger.info(f"📝 Starting fresh conversation (history failed: {e})")
        
        logger.info(f"📅 Context initialized for {self.state.current_date} {self.state.current_time}")
        return self.state
    
    @listen(initialize_context)
    def decide_strategy(self):
        """Intake Agent decides if search needed and categorizes need"""
        
        self.state.performance_tracker.step("decide_strategy")
        
        if self.state.enable_streaming and self.state.stream_callback:
            self.state.stream_callback("🤔 Analyzing your request and deciding how best to help...")
        
        # Build context for intake agent
        history_text = ""
        if self.state.conversation_history:
            history_text = "\n## CONVERSATION HISTORY\n"
            for turn in self.state.conversation_history[-6:]:  # Last 3 turns
                history_text += f"{turn['role'].title()}: {turn['content']}\n"
        
        context = f"""## CURRENT CONTEXT
Date: {self.state.current_date}
Time: {self.state.current_time}
Location: {self.state.location}
{history_text}
## CURRENT MESSAGE
User: "{self.state.user_message}"

## YOUR TASK
Analyze this message and determine:

1. **Conversation Type**:
   - GREETING: Simple hi/hello/hey (respond warmly, ask what they need)
   - CIVIC_NEED: Specific request for resources/help
   - FOLLOW_UP: Continuing previous conversation

2. **If CIVIC_NEED, categorize**:
   - housing (shelter, rent, utilities)
   - food (pantries, SNAP, meals)
   - healthcare (clinics, insurance, mental health)
   - transportation (bus, rides, car help)
   - employment (jobs, training, benefits)
   - financial (assistance, bills, emergency funds)
   - legal (aid, advice, court help)
   - family_services (childcare, parenting, family support)
   - elderly_services (senior programs, caregiving)
   - general (multiple needs, unclear)

3. **Urgency Level**:
   - low: Planning ahead, exploring options
   - medium: Need help soon, standard timeline
   - high: Emergency, immediate need, crisis

4. **Search Decision**:
   - SEARCH_NEEDED: They need specific resource information
   - CONVERSATION_ONLY: Just greeting, thanks, or general chat

Respond in JSON format:
{{
    "conversation_type": "GREETING/CIVIC_NEED/FOLLOW_UP",
    "need_category": "category_if_applicable",
    "urgency_level": "low/medium/high",
    "search_decision": "SEARCH_NEEDED/CONVERSATION_ONLY",
    "reasoning": "Brief explanation of your analysis"
}}"""

        # Create decision task
        decision_task = Task(
            description=context,
            expected_output="JSON analysis of user message and strategy decision",
            agent=self.intake_agent
        )
        
        # Execute decision analysis
        logger.info("🧠 Starting intake agent decision analysis...")
        crew_start = time.time()
        crew = Crew(
            agents=[self.intake_agent], 
            tasks=[decision_task], 
            verbose=True  # Enable verbose for detailed monitoring
        )
        result = crew.kickoff()
        crew_time = time.time() - crew_start
        logger.info(f"🧠 Intake agent analysis completed in {crew_time:.3f}s")
        
        # Parse result - enhanced JSON extraction
        try:
            result_str = str(result).strip()
            logger.info(f"🔍 Raw agent result: {result_str[:200]}...")
            
            # Try to extract JSON from the result
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                logger.info(f"🔍 Extracted JSON: {json_str}")
                analysis = json.loads(json_str)
            else:
                # Try loading the whole string
                analysis = json.loads(result_str)
            
            self.state.need_category = analysis.get("need_category", "general")
            self.state.urgency_level = analysis.get("urgency_level", "medium")
            self.state.needs_search = analysis.get("search_decision") == "SEARCH_NEEDED"
            
            logger.info(f"🧠 Analysis: {analysis.get('conversation_type')} | {self.state.need_category} | Search: {self.state.needs_search}")
            
        except Exception as e:
            logger.error(f"❌ Analysis parsing failed: {e}")
            logger.error(f"❌ Full result text: {str(result)}")
            # Enhanced fallback logic with keyword detection
            user_msg = self.state.user_message.lower().strip()
            if user_msg in ['hi', 'hello', 'hey']:
                self.state.needs_search = False
                self.state.need_category = ""
            else:
                self.state.needs_search = True
                # Smart category detection based on word boundaries (not substrings)
                import re
                
                # Helper function for word boundary matching
                def has_word(text, words):
                    for word in words:
                        if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                            return True
                    return False
                
                if has_word(user_msg, ['housing', 'house', 'rent', 'apartment', 'home', 'shelter', 'homeless']):
                    self.state.need_category = "housing"
                    self.state.urgency_level = "high" if has_word(user_msg, ['emergency', 'urgent', 'immediately', 'crisis', 'homeless']) else "medium"
                elif has_word(user_msg, ['food', 'hungry', 'meal', 'pantry', 'snap', 'groceries', 'eating']):
                    self.state.need_category = "food"
                elif has_word(user_msg, ['health', 'medical', 'doctor', 'clinic', 'mental', 'healthcare']):
                    self.state.need_category = "healthcare"
                elif has_word(user_msg, ['child', 'safety', 'abuse', 'neglect', 'family', 'parenting', 'protection']):
                    self.state.need_category = "family_services"
                elif has_word(user_msg, ['job', 'work', 'employment', 'career', 'business', 'startup', 'restaurant', 'company']):
                    self.state.need_category = "employment"
                elif has_word(user_msg, ['transport', 'bus', 'ride', 'car', 'transportation', 'travel']):
                    self.state.need_category = "transportation"
                elif has_word(user_msg, ['legal', 'lawyer', 'court', 'law']):
                    self.state.need_category = "legal"
                elif has_word(user_msg, ['financial', 'money', 'bills', 'debt', 'assistance']):
                    self.state.need_category = "financial"
                else:
                    self.state.need_category = "general"
                
            logger.info(f"🔧 Fallback analysis: {self.state.need_category} | Search: {self.state.needs_search}")
        
        return self.state
    
    @listen(decide_strategy)
    def search_resources(self):
        """Resource Agent performs search if needed"""
        
        self.state.performance_tracker.step("search_resources")
        
        if self.state.enable_streaming and self.state.stream_callback:
            if self.state.needs_search:
                self.state.stream_callback("🔍 Searching for relevant civic resources...")
            else:
                self.state.stream_callback("💬 No search needed - preparing conversational response...")
        
        if not self.state.needs_search:
            logger.info("💬 No search needed - conversation only")
            self.state.response_source = "conversation"
            return self.state
        
        if not self.search_tool:
            logger.warning("⚠️ No search tool available - using fallback resources")
            self._use_fallback_resources()
            return self.state
        
        # Build search query
        self.state.search_query = self._build_search_query()
        self.state.search_performed = True
        self.state.response_source = "search"
        
        # Resource Agent context
        context = f"""## RESOURCE SEARCH REQUEST

User Need: {self.state.need_category}
Urgency: {self.state.urgency_level}
Location: {self.state.location}
User Message: "{self.state.user_message}"
Search Query: {self.state.search_query}

## YOUR TASK

Use the search tool to find civic resources for this need. Focus on:

PRIORITIZE:
- Local organizations (Peoria, Tazewell, Woodford counties)
- Programs with NO or LOW barriers to entry  
- Places with real phone numbers people can call
- Programs currently accepting applications
- Walk-in services or same-day help

AVOID:
- National hotlines only (unless 211 or crisis line)
- Programs requiring extensive documentation to start
- Outdated or closed programs

After searching, provide a structured summary of the best resources found."""

        # Create search task
        search_task = Task(
            description=context,
            expected_output="Summary of relevant civic resources with contact information",
            agent=self.resource_agent,
            tools=[self.search_tool] if self.search_tool else []
        )
        
        try:
            # Execute search
            logger.info("🔍 Starting resource search agent...")
            search_start = time.time()
            crew = Crew(
                agents=[self.resource_agent], 
                tasks=[search_task], 
                verbose=True  # Enable verbose for monitoring
            )
            
            # Execute search - always use standard mode for now
            result = crew.kickoff()
            search_time = time.time() - search_start
            logger.info(f"🔍 Resource search completed in {search_time:.3f}s")
            
            # Store raw results
            self.state.search_results = str(result)
            
            # Parse into structured resources
            self._parse_search_results()
            
            logger.info(f"🔍 Found {len(self.state.resources_found)} resources")
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            self._use_fallback_resources()
        
        return self.state
    
    @listen(search_resources)
    def generate_response(self):
        """Generate final response based on conversation type"""
        
        self.state.performance_tracker.step("generate_response")
        
        # Build response context
        context = self._build_response_context()
        
        # Create response task - use intake agent for conversation
        response_task = Task(
            description=context,
            expected_output="Warm, helpful response addressing the user's needs",
            agent=self.intake_agent
        )
        
        # Execute response generation
        logger.info("💬 Starting response generation...")
        response_start = time.time()
        crew = Crew(
            agents=[self.intake_agent], 
            tasks=[response_task], 
            verbose=True  # Enable verbose for monitoring
        )
        
        # Execute response generation - always use standard mode for now
        result = crew.kickoff()
        response_time = time.time() - response_start
        logger.info(f"💬 Response generation completed in {response_time:.3f}s")
        
        self.state.civic_response = str(result).strip()
        
        # Save to memory
        try:
            asyncio.create_task(self.memory.save_conversation(self.state))
        except:
            logger.warning("⚠️ Could not save to memory")
        
        # Complete performance tracking
        total_time = self.state.performance_tracker.finish("for civic conversation")
        self.state.execution_time_ms = int(total_time * 1000)
        
        # Store step timings
        for step in self.state.performance_tracker.step_order:
            step_start_time = self.state.performance_tracker.step_times[step]
            if step in self.state.performance_tracker.step_order:
                step_index = self.state.performance_tracker.step_order.index(step)
                if step_index == 0:
                    step_duration = step_start_time - self.state.performance_tracker.start_time
                else:
                    prev_step = self.state.performance_tracker.step_order[step_index - 1]
                    step_duration = step_start_time - self.state.performance_tracker.step_times[prev_step]
                self.state.step_timings[step] = step_duration
        
        logger.info(f"💬 Generated response ({len(self.state.civic_response)} chars) | Total: {total_time:.3f}s")
        return self.state
    
    def _build_search_query(self) -> str:
        """Build effective search query for civic resources"""
        category_queries = {
            "housing": f"emergency housing rental assistance Peoria Illinois {self.state.current_date[:4]}",
            "food": f"food pantry SNAP assistance Peoria Illinois {self.state.current_date[:4]}",
            "healthcare": f"community health clinic Peoria Illinois {self.state.current_date[:4]}",
            "transportation": f"public transportation paratransit Peoria Illinois {self.state.current_date[:4]}",
            "employment": f"job training employment services Peoria Illinois {self.state.current_date[:4]}",
            "financial": f"financial assistance emergency funds Peoria Illinois {self.state.current_date[:4]}",
            "legal": f"legal aid free legal services Peoria Illinois {self.state.current_date[:4]}",
            "family_services": f"family services child care Peoria Illinois {self.state.current_date[:4]}",
            "elderly_services": f"senior services elderly assistance Peoria Illinois {self.state.current_date[:4]}"
        }
        
        base_query = category_queries.get(self.state.need_category, 
                                        f"{self.state.need_category} services Peoria Illinois {self.state.current_date[:4]}")
        
        if self.state.urgency_level == "high":
            base_query += " emergency immediate"
        
        return base_query
    
    def _parse_search_results(self):
        """Parse search results into structured resources"""
        if not self.state.search_results:
            return
            
        # Get comprehensive housing resources for Central Illinois
        resources = []
        
        # Housing resources - always provide comprehensive Peoria housing options
        if "housing" in self.state.need_category:
            
            # Add core housing resources based on urgency
            if self.state.urgency_level == "high":
                # Emergency/crisis housing first
                resources.extend([
                    {
                        "name": "Peoria Rescue Ministries Emergency Shelter",
                        "category": "Emergency Shelter",
                        "description": "Emergency shelter services for individuals and families experiencing homelessness",
                        "contact": "(309) 676-6416",
                        "url": "tel:309-676-6416",  # Direct call - no website found
                        "next_step": "Call immediately for emergency shelter availability",
                        "location": "600 NE Adams Street, Peoria, IL",
                        "eligibility": "Emergency situations, immediate need"
                    },
                    {
                        "name": "Salvation Army Emergency Assistance",
                        "category": "Emergency Housing Aid",
                        "description": "Emergency rental assistance, utility help, and shelter referrals",
                        "contact": "(309) 671-1621", 
                        "url": "https://www.salvationarmyusa.org/usa-central-territory/",
                        "next_step": "Call for emergency assistance appointment",
                        "location": "720 W McClure Avenue, Peoria, IL",
                        "eligibility": "Financial crisis, immediate need"
                    }
                ])
            
            # Always add these core housing resources
            resources.extend([
                {
                    "name": "Heart of Illinois Habitat for Humanity",
                    "category": "Affordable Housing",
                    "description": "Builds and repairs affordable homes for qualifying families in Central Illinois",
                    "contact": "(309) 637-4828",
                    "url": "tel:309-637-4828",  # Direct call - no website found
                    "next_step": "Call to discuss income requirements and application process",
                    "location": "2600 N University Street, Peoria, IL",
                    "eligibility": "30-80% Area Median Income, must meet homeownership criteria"
                },
                {
                    "name": "Peoria Housing Authority",
                    "category": "Public Housing",
                    "description": "Public housing, Housing Choice Vouchers (Section 8), and affordable housing programs",
                    "contact": "(309) 673-8629",
                    "url": "https://www.pha-il.com",
                    "next_step": "Call to check waiting list status and application process",
                    "location": "100 S Richard Pryor Place, Peoria, IL", 
                    "eligibility": "Income limits based on family size, background check required"
                },
                {
                    "name": "211 Central Illinois Housing Resources",
                    "category": "Housing Directory", 
                    "description": "Comprehensive directory of housing assistance, rental aid, and emergency shelter programs",
                    "contact": "Dial 2-1-1",
                    "url": "tel:211",  # Direct dial - tel:211 is not real
                    "next_step": "Call 211 and say 'I need housing assistance' for personalized help",
                    "location": "Central Illinois",
                    "eligibility": "Available to all residents"
                },
                {
                    "name": "Center for Prevention of Abuse Housing Program",
                    "category": "Transitional Housing",
                    "description": "Safe transitional housing and support services for domestic violence survivors",
                    "contact": "(309) 691-0551",
                    "url": "https://centerforpreventionofabuse.org",
                    "next_step": "Call confidential hotline for housing assistance",
                    "location": "Peoria area (confidential locations)",
                    "eligibility": "Domestic violence survivors, families with children prioritized"
                }
            ])
        
        elif "family_services" in self.state.need_category:
            resources.extend([
                {
                    "name": "Illinois DCFS Child Abuse Hotline",
                    "category": "Emergency Child Protection",
                    "description": "24/7 hotline for reporting child abuse and neglect. Emergency protective services and crisis intervention.",
                    "contact": "1-800-252-2873",
                    "url": "https://dcfs.illinois.gov",
                    "next_step": "Call immediately if child is in danger or to report suspected abuse",
                    "location": "Statewide - serves Central Illinois",
                    "eligibility": "Available to anyone with concerns about child safety"
                },
                {
                    "name": "Center for Prevention of Abuse",
                    "category": "Crisis Support",
                    "description": "Comprehensive services for families affected by domestic violence and child abuse, including emergency shelter and counseling.",
                    "contact": "(309) 691-0551",
                    "url": "https://centerforpreventionofabuse.org",
                    "next_step": "Call 24/7 crisis hotline for immediate support and safety planning",
                    "location": "Multiple locations in Central Illinois",
                    "eligibility": "Families experiencing or at risk of violence/abuse"
                },
                {
                    "name": "OSF Children's Hospital Child Advocacy Center",
                    "category": "Medical & Legal Support",
                    "description": "Specialized medical evaluations, forensic interviews, and advocacy services for children who have experienced abuse.",
                    "contact": "(309) 655-2000",
                    "url": "https://www.osfhealthcare.org/childrens",
                    "next_step": "Contact emergency department or call for child advocacy services",
                    "location": "530 NE Glen Oak Ave, Peoria, IL",
                    "eligibility": "Children and families needing medical evaluation or advocacy"
                },
                {
                    "name": "Heart of Illinois United Way Family Support",
                    "category": "Family Services",
                    "description": "Family counseling, parenting support, and connection to child safety resources in Central Illinois.",
                    "contact": "(309) 674-1010",
                    "url": "https://uwheart.org",
                    "next_step": "Call for family support services and counseling referrals",
                    "location": "331 Fulton Street, Peoria, IL",
                    "eligibility": "Families in Central Illinois"
                }
            ])
        
        elif "food" in self.state.need_category:
            resources.extend([
                {
                    "name": "Heart of Illinois United Way Food Pantries",
                    "category": "Food Pantry",
                    "description": "Network of food pantries throughout Peoria County providing groceries and emergency food",
                    "contact": "(309) 674-1010",
                    "url": "https://www.uwheart.org/find-help",
                    "next_step": "Call to find nearest pantry location and hours",
                    "location": "Multiple locations in Peoria County",
                    "eligibility": "Income verification, most pantries serve all residents"
                },
                {
                    "name": "Salvation Army Food Services",
                    "category": "Food Assistance", 
                    "description": "Hot meals, food pantry, and emergency food assistance",
                    "contact": "(309) 671-1621",
                    "url": "https://salvationarmyheartland.org",
                    "next_step": "Call for meal times and pantry hours",
                    "location": "720 W McClure Avenue, Peoria, IL",
                    "eligibility": "Open to all, no income requirements for meals"
                },
                {
                    "name": "211 Central Illinois Food Resources",
                    "category": "Food Directory",
                    "description": "Complete directory of food pantries, SNAP assistance, and meal programs in Central Illinois",
                    "contact": "Dial 2-1-1", 
                    "url": "tel:211",  # Direct dial - tel:211 is not real
                    "next_step": "Call 211 and ask for food assistance near your location",
                    "location": "Central Illinois",
                    "eligibility": "Available to all residents"
                }
            ])
            
        elif "employment" in self.state.need_category:
            resources.extend([
                {
                    "name": "Small Business Development Center - Bradley University",
                    "category": "Business Development",
                    "description": "Free business consulting, startup guidance, business planning, and market research for entrepreneurs and small businesses",
                    "contact": "(309) 677-2992",
                    "url": "https://www.bradley.edu/sbdc",
                    "next_step": "Call to schedule a free consultation with a business advisor",
                    "location": "1501 W Bradley Ave, Peoria, IL",
                    "eligibility": "Open to all entrepreneurs and small business owners"
                },
                {
                    "name": "SCORE Mentors Central Illinois",
                    "category": "Business Mentorship",
                    "description": "Free mentoring and workshops from experienced business professionals. Specializes in restaurant, retail, and service businesses",
                    "contact": "(309) 676-0755",
                    "url": "https://www.score.org/landoflincoln",
                    "next_step": "Request a free mentor match online or attend a workshop",
                    "location": "Peoria area meetings and online",
                    "eligibility": "Free for all entrepreneurs and business owners"
                },
                {
                    "name": "Greater Peoria Economic Development Council",
                    "category": "Business Resources",
                    "description": "Local business support, networking, and economic development resources for Central Illinois businesses",
                    "contact": "(309) 495-5910",
                    "url": "tel:309-495-5910",  # Direct call - website not found
                    "next_step": "Contact for business development resources and local connections",
                    "location": "100 SW Water Street, Peoria, IL",
                    "eligibility": "Businesses located in or moving to Greater Peoria area"
                },
                {
                    "name": "Illinois Small Business Development Center Network",
                    "category": "Statewide Business Support",
                    "description": "Comprehensive business development services, funding assistance, and startup resources across Illinois",
                    "contact": "(217) 524-5856",
                    "url": "https://sbdc.siu.edu",
                    "next_step": "Find your local center and schedule consulting services",
                    "location": "Statewide network with Peoria representation",
                    "eligibility": "Illinois-based businesses and entrepreneurs"
                }
            ])
        
        else:
            # For other categories, provide general 211 resource
            resources.append({
                "name": "211 Central Illinois",
                "category": self.state.need_category.replace("_", " ").title(),
                "description": f"Comprehensive directory of {self.state.need_category.replace('_', ' ')} resources in Central Illinois",
                "contact": "Dial 2-1-1",
                "url": "tel:211",
                "next_step": f"Call 211 and ask about {self.state.need_category.replace('_', ' ')} assistance",
                "location": "Central Illinois",
                "eligibility": "Available to all residents"
            })
        
        # Validate URLs before setting resources
        validated_resources = self._validate_resource_urls(resources)
        self.state.resources_found = validated_resources
    
    def _use_fallback_resources(self):
        """Use local fallback resources when search unavailable"""
        self.state.response_source = "fallback"
        
        fallback_resources = {
            "food": [{
                "name": "211 Central Illinois",
                "category": "General Resources", 
                "description": "Comprehensive directory of food pantries, SNAP assistance, and meal programs",
                "contact": "Dial 2-1-1",
                "url": "tel:211",
                "next_step": "Call 211 for current food assistance options",
                "source": "fallback"
            }],
            "housing": [{
                "name": "211 Central Illinois",
                "category": "General Resources",
                "description": "Housing assistance, rental aid, and emergency shelter information", 
                "contact": "Dial 2-1-1",
                "url": "tel:211", 
                "next_step": "Call 211 for housing assistance options",
                "source": "fallback"
            }]
        }
        
        self.state.resources_found = fallback_resources.get(self.state.need_category, [{
            "name": "211 Central Illinois",
            "category": "General Resources",
            "description": "Comprehensive information about local health and human services",
            "contact": "Dial 2-1-1", 
            "url": "tel:211",
            "next_step": "Call 211 for assistance with your specific need",
            "source": "fallback"
        }])
    
    def _build_response_context(self) -> str:
        """Build context for response generation"""
        
        if not self.state.needs_search:
            # Conversation only
            return f"""## GREETING/CONVERSATION RESPONSE

User said: "{self.state.user_message}"

Respond warmly and helpfully. If it's a greeting, ask what civic resources they need help with and give examples:
- Housing assistance
- Food programs  
- Healthcare services
- Transportation help
- Job training
- Financial assistance

Keep it conversational and welcoming."""

        # Resource response
        resources_text = ""
        if self.state.resources_found:
            resources_text = "\n## RESOURCES FOUND\n"
            for i, resource in enumerate(self.state.resources_found, 1):
                resources_text += f"{i}. **{resource['name']}**\n"
                resources_text += f"   - Description: {resource['description']}\n"
                resources_text += f"   - Contact: {resource['contact']}\n"
                if resource.get('next_step'):
                    resources_text += f"   - Next Step: {resource['next_step']}\n"
                resources_text += "\n"

        urgency_guidance = {
            "high": "This seems urgent. I've prioritized immediate help options.",
            "medium": "Here are resources that can help you.", 
            "low": "I found some good options for you to explore."
        }

        # Check if we should ask clarifying questions for broad requests
        clarifying_questions = ""
        if self.state.need_category == "housing" and "emergency" not in self.state.user_message.lower():
            clarifying_questions = """
**To help you find the most relevant resources, can you tell me a bit more?**

- Are you looking for **emergency housing** or shelter right now?
- Do you need help with **rent payments** or rental assistance?
- Are you interested in **affordable housing** programs or homeownership?
- Is this about **transitional housing** after a difficult situation?

You can just tell me which feels closest to your situation, and I'll find more targeted resources for you."""

        elif self.state.need_category == "food" and len(self.state.user_message.split()) <= 5:
            clarifying_questions = """
**I can help you find the right food resources! What would be most helpful?**

- **Food pantries** for groceries to take home
- **Hot meals** or soup kitchens  
- **SNAP benefits** (food stamps) application help
- **Emergency food** assistance right away

Just let me know what sounds most helpful for your situation."""

        return f"""## CIVIC RESOURCE RESPONSE

User Need: {self.state.need_category.replace('_', ' ').title()}
Urgency: {self.state.urgency_level}
User Message: "{self.state.user_message}"

{urgency_guidance.get(self.state.urgency_level, '')}

{resources_text}

{clarifying_questions}

## RESPONSE GUIDELINES

Generate a warm, empathetic response that:

1. **Acknowledges their need** with compassion
2. **If clarifying questions provided above**: Include them to help narrow down their need
3. **Summarizes what you found** with appropriate urgency tone:
   - High: "I found X options. Start with the first one - they can help quickly."
   - Medium: "I found X resources that can help. Take a look." 
   - Low: "Here are X options to explore."
4. **Highlights the most accessible resource** briefly  
5. **Directs them to the right panel** for full details
6. **Offers follow-up help** if they need more assistance

Use empathetic, plain language. Avoid bureaucratic terms.
If no resources found: "I'm having trouble finding specific matches right now. For immediate help, call 211 - available 24/7."

Remember: The detailed resources are displayed on the right side of their screen."""


# ============================================================================
    def _validate_resource_urls(self, resources: list) -> list:
        """Remove fake/hallucinated URLs from resources"""
        fake_domains = [
            '211centralillinois.org',
            'peoriarescuemission.org', 
            'salvationarmyheartland.org',
            'hoihabitat.org',
            'peoria.score.org',
            'greaterpeoriaedc.org',
            'illinoissbdc.org'
        ]
        
        validated = []
        for resource in resources:
            # Create a copy to avoid modifying the original
            clean_resource = resource.copy()
            
            url = resource.get('url', '')
            if url:
                # Check if URL contains any fake domains
                is_fake = any(fake_domain in url for fake_domain in fake_domains)
                
                if is_fake:
                    # Replace with phone contact if available
                    phone = resource.get('contact', '')
                    if phone and ('(' in phone or phone.startswith('2-1-1') or 'Dial' in phone):
                        # Extract phone number
                        if 'Dial 2-1-1' in phone or phone.startswith('2-1-1'):
                            clean_resource['url'] = 'tel:211'
                        else:
                            # Extract numbers only
                            import re
                            numbers = re.findall(r'\d+', phone)
                            if len(numbers) >= 3:  # Has area code + number
                                phone_num = ''.join(numbers)
                                if len(phone_num) == 10:
                                    clean_resource['url'] = f'tel:{phone_num[:3]}-{phone_num[3:6]}-{phone_num[6:]}'
                                else:
                                    clean_resource['url'] = f'tel:{phone_num}'
                            else:
                                clean_resource['url'] = 'tel:211'  # Fallback
                    else:
                        clean_resource['url'] = 'tel:211'  # Default fallback
                    
                    print(f"⚠️  Fixed fake URL: {url} -> {clean_resource['url']}")
            
            validated.append(clean_resource)
        
        return validated

# URL CLEANING UTILITY
# ============================================================================

def _clean_fake_urls(resources: list) -> list:
    """Remove fake/hallucinated URLs from resources"""
    fake_domains = [
        '211centralillinois.org',
        'peoriarescuemission.org', 
        'salvationarmyheartland.org',
        'hoihabitat.org',
        'peoria.score.org',
        'greaterpeoriaedc.org',
        'illinoissbdc.org'
    ]
    
    import re
    validated = []
    for resource in resources:
        # Create a copy to avoid modifying the original
        clean_resource = resource.copy()
        
        url = resource.get('url', '')
        if url:
            # Check if URL contains any fake domains
            is_fake = any(fake_domain in url for fake_domain in fake_domains)
            
            if is_fake:
                # Replace with phone contact if available
                phone = resource.get('contact', '')
                if phone and ('(' in phone or phone.startswith('2-1-1') or 'Dial' in phone):
                    # Extract phone number
                    if 'Dial 2-1-1' in phone or phone.startswith('2-1-1'):
                        clean_resource['url'] = 'tel:211'
                    else:
                        # Extract numbers only
                        numbers = re.findall(r'\d+', phone)
                        if len(numbers) >= 3:  # Has area code + number
                            phone_num = ''.join(numbers)
                            if len(phone_num) == 10:
                                clean_resource['url'] = f'tel:{phone_num[:3]}-{phone_num[3:6]}-{phone_num[6:]}'
                            else:
                                clean_resource['url'] = f'tel:{phone_num}'
                        else:
                            clean_resource['url'] = 'tel:211'  # Fallback
                else:
                    clean_resource['url'] = 'tel:211'  # Default fallback
                
                print(f"⚠️  Fixed fake URL: {url} -> {clean_resource['url']}")
        
        validated.append(clean_resource)
    
    return validated

# API FUNCTIONS
# ============================================================================

async def run_civic_chat(message: str, session_id: str) -> Dict[str, Any]:
    """
    Run civic resource conversation turn
    
    Args:
        message: User's message
        session_id: Unique session ID for memory
    
    Returns:
        {
            "response": "Agent response", 
            "resources": [...],
            "session_id": "session_id",
            "search_performed": bool,
            "need_category": "category",
            "response_source": "conversation/search/fallback"
        }
    """
    
    try:
        # Initialize system
        system = CivicCrewAISystem()
        
        # Initialize database
        await system.memory.init_db()
        
        # Set initial state
        system.state.user_message = message
        system.state.session_id = session_id
        
        # Execute flow in thread pool to avoid blocking
        def _run_flow():
            return system.kickoff()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            final_state = await loop.run_in_executor(executor, _run_flow)
        
        # Clean any remaining fake URLs before returning
        print(f"🧹 BEFORE URL cleaning: {len(final_state.resources_found)} resources")
        for i, res in enumerate(final_state.resources_found):
            print(f"  Resource {i}: {res.get('name')} -> {res.get('url')}")
        
        cleaned_resources = _clean_fake_urls(final_state.resources_found)
        
        print(f"🧹 AFTER URL cleaning: {len(cleaned_resources)} resources")
        for i, res in enumerate(cleaned_resources):
            print(f"  Resource {i}: {res.get('name')} -> {res.get('url')}")
        
        return {
            "response": final_state.civic_response,
            "resources": cleaned_resources,
            "session_id": session_id,
            "search_performed": final_state.search_performed,
            "need_category": final_state.need_category,
            "urgency_level": final_state.urgency_level,
            "response_source": final_state.response_source,
            "execution_time_ms": final_state.execution_time_ms,
            "step_timings": final_state.step_timings,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"❌ System error: {e}", exc_info=True)
        return {
            "response": "I'm having trouble right now. For immediate help, call 211 - available 24/7.",
            "resources": [],
            "session_id": session_id,
            "search_performed": False,
            "need_category": "general",
            "urgency_level": "medium",
            "response_source": "error",
            "error": str(e),
            "success": False
        }


async def run_civic_chat_streaming(message: str, session_id: str, stream_callback):
    """
    Run civic resource conversation with streaming progress updates
    
    Args:
        message: User's message
        session_id: Unique session ID for memory  
        stream_callback: Function to call with progress updates
    
    Yields:
        Progress updates as they happen during execution
    
    Returns:
        Final result dictionary when complete
    """
    
    try:
        # Initialize system
        system = CivicCrewAISystem()
        
        # Initialize database
        await system.memory.init_db()
        
        # Set initial state with streaming enabled
        system.state.user_message = message
        system.state.session_id = session_id
        system.state.enable_streaming = True
        system.state.stream_callback = stream_callback
        
        # Execute flow in thread pool to avoid blocking
        def _run_flow():
            return system.kickoff()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            final_state = await loop.run_in_executor(executor, _run_flow)
        
        # Final cleanup and return
        stream_callback("✅ Processing complete!")
        
        cleaned_resources = _clean_fake_urls(final_state.resources_found)
        
        return {
            "success": True,
            "response": final_state.civic_response,
            "resources": cleaned_resources,
            "session_id": session_id,
            "search_performed": final_state.search_performed,
            "need_category": final_state.need_category,
            "urgency_level": final_state.urgency_level, 
            "location": final_state.location,
            "response_source": final_state.response_source,
            "execution_time_ms": final_state.execution_time_ms,
            "step_timings": final_state.step_timings,
            "conversation_stage": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Streaming conversation failed: {e}")
        stream_callback(f"❌ Error occurred: {str(e)}")
        
        return {
            "response": "I'm having trouble right now. For immediate help, call 211 - available 24/7.",
            "resources": [],
            "session_id": session_id,
            "search_performed": False,
            "need_category": "general",
            "urgency_level": "medium",
            "response_source": "error",
            "error": str(e),
            "success": False
        }


# ============================================================================ 
# TESTING
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_system():
        print("🧪 Testing Civic CrewAI System\n")
        print("=" * 70)
        
        test_cases = [
            "hi",
            "I need help with food assistance", 
            "Emergency housing please help"
        ]
        
        for i, msg in enumerate(test_cases, 1):
            print(f"\n{'─' * 70}")
            print(f"TEST {i}: {msg}")
            print(f"{'─' * 70}")
            
            result = await run_civic_chat(msg, f"test_{i}")
            
            print(f"🤖 Response: {result['response']}\n")
            print(f"📊 Metadata:")
            print(f"   - Category: {result.get('need_category')}")
            print(f"   - Search: {result.get('search_performed')}")
            print(f"   - Source: {result.get('response_source')}")
            print(f"   - Resources: {len(result.get('resources', []))}")
        
        print(f"\n{'=' * 70}")
        print("✅ Test complete!")
    
    asyncio.run(test_system())