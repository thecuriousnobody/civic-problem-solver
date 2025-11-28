#!/usr/bin/env python3
"""
Simple Civic Resource Flow - Fast, Demo-Ready Implementation
==========================================================

CrewAI Flow-based civic resource discovery using:
- Claude Haiku 4.5 for speed
- Serper for real-time search
- Minimal state management
- Quick responses for proof of concept
"""

import os
import json
import time
import asyncio
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, listen, start, router
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Load environment
load_dotenv()

class CivicState(BaseModel):
    """Simple state for civic resource discovery flow"""
    
    # User input
    user_message: str = ""
    session_id: str = ""
    
    # Analysis results
    needs_category: str = ""
    location: str = "peoria_illinois"
    urgency_level: str = "medium"  # low, medium, high
    
    # Search results
    resources_found: List[Dict[str, Any]] = []
    search_completed: bool = False
    
    # Response
    agent_response: str = ""
    conversation_stage: str = "intake"  # intake, searching, results
    response_source: str = "unknown"  # crew_search, crew_analysis, local_fallback
    
    # Metadata
    response_time_ms: int = 0
    timestamp: str = ""

class CivicResourceFlow(Flow[CivicState]):
    """Fast civic resource discovery flow"""
    
    def __init__(self):
        super().__init__()
        
        # Load YAML configurations
        config_dir = Path(__file__).parent / "config"
        
        with open(config_dir / "agents.yaml", 'r') as f:
            agents_config = yaml.safe_load(f)
        
        with open(config_dir / "tasks.yaml", 'r') as f:
            self.tasks_config = yaml.safe_load(f)
        
        # Initialize LLM (fast model)
        self.llm = LLM(
            model="anthropic/claude-haiku-4-5-20251001",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Initialize search tool
        self.search_tool = SerperDevTool(
            api_key=os.getenv("SERPER_API_KEY")
        ) if os.getenv("SERPER_API_KEY") else None
        
        # Create civic analyst agent from YAML config
        analyst_config = agents_config['civic_analyst']
        self.civic_analyst = Agent(
            role=analyst_config['role'],
            goal=analyst_config['goal'], 
            backstory=analyst_config['backstory'],
            llm=self.llm,
            verbose=analyst_config.get('verbose', True),
            allow_delegation=analyst_config.get('allow_delegation', False),
            max_iter=analyst_config.get('max_iter', 3),
            max_rpm=analyst_config.get('max_rpm', 10)
        )
    
    @start()
    def analyze_request(self):
        """Quick analysis of user request"""
        start_time = time.time()
        
        # Create analysis task from YAML config
        task_config = self.tasks_config['analyze_civic_request']
        analysis_task = Task(
            description=task_config['description'].format(user_message=self.state.user_message),
            expected_output=task_config['expected_output'],
            agent=self.civic_analyst
        )
        
        # Create a simple crew and execute synchronously
        crew = Crew(
            agents=[self.civic_analyst],
            tasks=[analysis_task],
            verbose=False
        )
        
        # Use kickoff_sync to avoid async issues
        result = crew.kickoff()
        
        try:
            analysis = json.loads(str(result))
            self.state.needs_category = analysis.get("category", "general")
            self.state.location = analysis.get("location", "peoria_illinois")
            self.state.urgency_level = analysis.get("urgency", "medium")
            self.state.agent_response = analysis.get("quick_response", "I'm here to help. Let me find resources for you...")
            self.state.conversation_stage = "searching"
            
            # Store additional analysis data for later use
            setattr(self.state, 'analysis_data', analysis)
            
            print(f"🔍 Analysis result - Category: {self.state.needs_category}, Response: {self.state.agent_response}")
                
        except Exception as e:
            print(f"Analysis parsing error: {e}")
            print(f"Raw result was: {str(result)}")
            
            # Check if this looks like a greeting based on input
            if self.state.user_message.lower().strip() in ['hi', 'hello', 'hey', 'help']:
                self.state.needs_category = "intake_greeting"
                self.state.agent_response = "Hello! I'm here to help you find local resources. What do you need help with today?"
            else:
                self.state.needs_category = "general"
                self.state.agent_response = "I'm here to help. Let me find resources for you..."
            self.state.conversation_stage = "searching"
        
        self.state.response_time_ms = int((time.time() - start_time) * 1000)
        self.state.timestamp = datetime.now().isoformat()
    
    @router(analyze_request)
    def route_request(self):
        """Route request based on analysis results"""
        # Additional fallback check for common greetings
        if (self.state.needs_category == "intake_greeting" or 
            self.state.user_message.lower().strip() in ['hi', 'hello', 'hey']):
            print("👋 Greeting detected - routing to greeting response")
            self.state.needs_category = "intake_greeting"  # Ensure it's set correctly
            return "greeting"
        else:
            print(f"📋 Need detected: {self.state.needs_category} - routing to resource search")
            return "search_resources"
    
    @listen("greeting")
    def greeting_response(self):
        """Handle greeting interactions"""
        self.state.response_source = "greeting_response"
        self.state.conversation_stage = "results"
        # Agent response already set in analyze_request with warm greeting
        print("✅ Greeting response complete")
        
    @listen("search_resources")
    def search_resources(self):
        """Search for relevant civic resources"""
        
        if not self.search_tool:
            # Fallback to basic local resources if no search API
            print("⚠️ No Serper API key - using local resources fallback")
            self.state.response_source = "local_fallback"
            self._use_local_resources()
            return "finalize_response"
        
        print("✅ Using Serper API for real-time search")
        self.state.response_source = "crew_search"
        
        # Build search query
        search_query = self._build_search_query()
        
        try:
            # Search for resources
            # Create search task from YAML config
            task_config = self.tasks_config['search_civic_resources']
            search_task = Task(
                description=task_config['description'].format(search_query=search_query),
                expected_output=task_config['expected_output'],
                agent=self.civic_analyst,
                tools=[self.search_tool]
            )
            
            # Create a simple crew and execute synchronously
            crew = Crew(
                agents=[self.civic_analyst],
                tasks=[search_task],
                verbose=False
            )
            
            # Use kickoff to execute
            result = crew.kickoff()
            self._parse_search_results(str(result))
            return "finalize_response"
            
        except Exception as e:
            print(f"⚠️ Search error: {e} - falling back to local resources")
            self.state.response_source = "local_fallback"
            self._use_local_resources()
            return "finalize_response"
    
    @listen("finalize_response")
    def finalize_response(self):
        """Generate final response with resources"""
        
        if not self.state.resources_found:
            self.state.agent_response = "I'm having trouble finding specific matches right now. For immediate help, call 211 - available 24/7."
            self.state.conversation_stage = "results"
            return
        
        # Generate response based on urgency and resource count
        resource_count = len(self.state.resources_found)
        
        # Urgency-appropriate tone
        if self.state.urgency_level == "high":
            tone = f"Found {resource_count} options. Start with the first one - they can help quickly."
        elif self.state.urgency_level == "medium":
            tone = f"Found {resource_count} resources that can help. Take a look."
        else:
            tone = f"Here are {resource_count} options to explore."
            
        self.state.agent_response = f"{tone} Results are displayed on the right, organized by accessibility."
        self.state.conversation_stage = "results"
        self.state.search_completed = True
    
    def _build_search_query(self) -> str:
        """Build effective search query"""
        category_map = {
            "housing": "housing assistance affordable housing Peoria Illinois",
            "food": "food pantry food assistance Peoria Illinois",
            "transportation": "public transportation paratransit Peoria Illinois", 
            "healthcare": "community health center free clinic Peoria Illinois",
            "employment": "job training employment services Peoria Illinois",
            "financial": "financial assistance emergency funds Peoria Illinois",
            "legal": "legal aid free legal services Peoria Illinois",
            "family_services": "family services child care Peoria Illinois",
            "elderly_services": "senior services elderly assistance Peoria Illinois"
        }
        
        base_query = category_map.get(self.state.needs_category, f"{self.state.needs_category} services Peoria Illinois")
        
        if self.state.urgency_level == "high":
            base_query += " emergency immediate help"
        
        return base_query
    
    def _parse_search_results(self, search_text: str):
        """Parse search results into structured format"""
        # Basic parsing - would be enhanced with better NLP
        resources = []
        
        # Try to extract structured information from search results
        lines = search_text.split('\n')
        current_resource = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_resource and 'name' in current_resource:
                    resources.append(current_resource)
                    current_resource = {}
                continue
            
            # Simple pattern matching for resource information
            if any(indicator in line.lower() for indicator in ['name:', 'organization:', 'program:']):
                current_resource['name'] = line.split(':', 1)[-1].strip()
                current_resource['category'] = self.state.needs_category.replace("_", " ").title()
            elif any(indicator in line.lower() for indicator in ['phone:', 'contact:', 'call:']):
                current_resource['contact'] = line.split(':', 1)[-1].strip()
            elif any(indicator in line.lower() for indicator in ['website:', 'web:', 'url:']):
                current_resource['url'] = line.split(':', 1)[-1].strip()
            elif any(indicator in line.lower() for indicator in ['description:', 'services:', 'offers:']):
                current_resource['description'] = line.split(':', 1)[-1].strip()
            elif any(indicator in line.lower() for indicator in ['eligibility:', 'requirements:', 'qualifies:']):
                current_resource['eligibility'] = line.split(':', 1)[-1].strip()
        
        # Add the last resource if it exists
        if current_resource and 'name' in current_resource:
            resources.append(current_resource)
        
        # If structured parsing didn't work, create basic resources from search text
        if not resources and search_text:
            resources = [{
                'name': 'Local Resource Information',
                'category': self.state.needs_category.replace("_", " ").title(),
                'description': search_text[:300] + "..." if len(search_text) > 300 else search_text,
                'contact': 'Call 2-1-1 for more information',
                'url': 'https://www.211.org',
                'eligibility': 'Varies by program'
            }]
        
        self.state.resources_found = resources[:6]  # Limit to 6 resources
    
    def _use_local_resources(self):
        """Fallback to local resource database"""
        # Basic local resources by category
        local_resources = {
            "housing": [
                {
                    "name": "Heart of Illinois Habitat for Humanity",
                    "category": "Housing",
                    "description": "Affordable housing and home repair programs for qualifying families",
                    "contact": "(309) 637-4828",
                    "url": "tel:309-637-4828",
                    "eligibility": "Income limits apply"
                }
            ],
            "food": [
                {
                    "name": "Peoria Area Food Bank",
                    "category": "Food Security",
                    "description": "Food pantry and emergency food assistance",
                    "contact": "(309) 671-3023", 
                    "url": "tel:309-671-3023",
                    "eligibility": "No income requirements"
                }
            ],
            "transportation": [
                {
                    "name": "CityLink",
                    "category": "Transportation",
                    "description": "Public transit and paratransit services",
                    "contact": "(309) 676-4040",
                    "url": "tel:309-676-4040", 
                    "eligibility": "General public, discounts for seniors/disabled"
                }
            ]
        }
        
        category_resources = local_resources.get(self.state.needs_category, [])
        if category_resources:
            self.state.resources_found = category_resources
        else:
            # Generic fallback
            self.state.resources_found = [{
                "name": "211 Central Illinois",
                "category": "General Resources",
                "description": "Comprehensive information about local health and human services",
                "contact": "Dial 2-1-1",
                "url": "tel:211",
                "eligibility": "Available to everyone"
            }]


def run_civic_flow(message: str, session_id: str, api_keys: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Run the civic resource flow with a user message
    
    Args:
        message: User's request for civic resources
        session_id: Session identifier
        api_keys: Optional API keys dict with 'anthropic' and 'serper' keys
    
    Returns:
        Dict with flow results including resources and response
    """
    
    # Override environment variables if API keys provided
    if api_keys:
        if api_keys.get('anthropic'):
            os.environ['ANTHROPIC_API_KEY'] = api_keys['anthropic']
        if api_keys.get('serper'):
            os.environ['SERPER_API_KEY'] = api_keys['serper']
    
    # Create and run flow
    flow = CivicResourceFlow()
    flow.state.user_message = message
    flow.state.session_id = session_id
    
    # Execute the flow - FIXED: No async await needed for sync execution
    try:
        # Run flow synchronously
        flow.analyze_request()
        flow.search_resources()
        flow.finalize_response()
        
        return {
            "success": True,
            "response": flow.state.agent_response,
            "resources": flow.state.resources_found,
            "conversation_stage": flow.state.conversation_stage,
            "needs_category": flow.state.needs_category,
            "location": flow.state.location,
            "urgency_level": flow.state.urgency_level,
            "response_time_ms": flow.state.response_time_ms,
            "timestamp": flow.state.timestamp,
            "session_id": session_id,
            "response_source": flow.state.response_source
        }
        
    except Exception as e:
        print(f"Flow execution error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I'm having trouble processing your request right now. Please try again.",
            "resources": [],
            "session_id": session_id
        }

if __name__ == "__main__":
    # Test the flow
    result = run_civic_flow(
        "I need help with food assistance in Peoria", 
        "test_session_123"
    )
    print(json.dumps(result, indent=2))