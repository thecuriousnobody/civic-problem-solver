#!/usr/bin/env python3
"""
Civic Intake Agent - Understands User Context
==========================================

Conversational agent that gathers user information to understand their specific
civic needs and situation for accurate resource matching.

Patterns from: distillery-intake-ai/sarah_crewai_flow.py
"""

from crewai import Agent, LLM
from typing import Dict, Any


class CivicIntakeAgent:
    """Agent focused on understanding user context and civic needs"""
    
    def __init__(self):
        self.llm = LLM(
            model="anthropic/claude-haiku-4-5-20251001",
            api_key="ANTHROPIC_API_KEY"
        )
        
        self.agent = Agent(
            role="Civic Resource Intake Specialist",
            goal="Understand the user's specific situation, needs, and eligibility factors to enable accurate resource matching",
            backstory="""You are a helpful civic resource specialist who excels at understanding
            people's unique situations through conversation. You ask thoughtful questions to gather
            the information needed for accurate resource matching, while being empathetic and 
            respectful of people's circumstances.""",
            
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def assess_user_needs(self, user_input: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Analyze user input to understand their civic resource needs
        
        Returns:
            dict: Contains user profile, needs assessment, and follow-up questions
        """
        
        context = {
            "user_input": user_input,
            "conversation_history": conversation_history or [],
            "focus_areas": [
                "Housing assistance",
                "Food security", 
                "Transportation",
                "Healthcare",
                "Employment services",
                "Financial assistance",
                "Legal aid",
                "Education/training",
                "Elderly/disability services",
                "Family services"
            ]
        }
        
        # In a real implementation, this would execute a CrewAI task
        # For now, returning structure for the proof of concept
        
        return {
            "needs_identified": [],
            "user_profile": {
                "age_range": None,
                "household_size": None,
                "employment_status": None,
                "income_level": None,
                "disability_status": None,
                "geographic_area": "peoria_illinois"  # Default for POC
            },
            "follow_up_questions": [],
            "ready_for_matching": False
        }
    
    def extract_geographic_context(self, user_input: str) -> str:
        """Extract geographic location from user input"""
        # Basic implementation - would be enhanced with NLP
        location_keywords = {
            "peoria": "peoria_illinois",
            "pekin": "pekin_illinois", 
            "morton": "morton_illinois",
            "east peoria": "east_peoria_illinois"
        }
        
        user_lower = user_input.lower()
        for keyword, location_code in location_keywords.items():
            if keyword in user_lower:
                return location_code
                
        return "peoria_illinois"  # Default