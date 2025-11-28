#!/usr/bin/env python3
"""
Civic Resource Agent - Local Knowledge Database
=============================================

Agent that maintains and searches local resource database.
Knows about programs, services, and organizations in the community.

Patterns from: distillery-intake-ai/simple_market_crew.py
"""

from crewai import Agent, LLM
from typing import Dict, Any, List
import json


class CivicResourceAgent:
    """Agent that knows local civic resources and programs"""
    
    def __init__(self, geographic_scope: str = "peoria_illinois"):
        self.geographic_scope = geographic_scope
        self.llm = LLM(
            model="anthropic/claude-haiku-4-5-20251001", 
            api_key="ANTHROPIC_API_KEY"
        )
        
        self.agent = Agent(
            role="Local Resource Database Expert",
            goal="Provide comprehensive, accurate information about local civic resources, programs, and services available in the community",
            backstory=f"""You are a knowledgeable local resource specialist with deep expertise
            in {geographic_scope} community services. You maintain an up-to-date database of
            programs, organizations, contact information, and service details. You understand
            how different programs work together and can recommend the most relevant resources.""",
            
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Load local resource database
        self.resources_db = self._load_resource_database()
    
    def _load_resource_database(self) -> Dict[str, Any]:
        """Load local resource database - would connect to real DB in production"""
        
        # Example structure for Peoria, IL
        return {
            "housing": [
                {
                    "name": "Heart of Illinois Habitat for Humanity",
                    "type": "Housing Assistance",
                    "services": ["Affordable housing", "Home repairs", "First-time homebuyer"],
                    "contact": {"phone": "(309) 637-4828", "website": "https://hoihabitat.org"},
                    "eligibility": "Income limits apply",
                    "geographic_area": "peoria_county"
                }
            ],
            "food_security": [
                {
                    "name": "Peoria Area Food Bank",
                    "type": "Food Assistance", 
                    "services": ["Food pantry", "Mobile food pantry", "Emergency food"],
                    "contact": {"phone": "(309) 671-3023", "website": "https://pafb.org"},
                    "eligibility": "No income requirements",
                    "geographic_area": "central_illinois"
                }
            ],
            "transportation": [
                {
                    "name": "CityLink",
                    "type": "Public Transportation",
                    "services": ["Fixed routes", "Paratransit", "Reduced fare programs"],
                    "contact": {"phone": "(309) 676-4040", "website": "https://ridecitylink.org"},
                    "eligibility": "Age/disability discounts available",
                    "geographic_area": "greater_peoria"
                }
            ],
            "healthcare": [],
            "employment": [],
            "financial_assistance": [],
            "legal_aid": [],
            "education": [],
            "elderly_services": [],
            "family_services": []
        }
    
    def search_resources(self, need_categories: List[str], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for relevant resources based on user needs"""
        
        relevant_resources = []
        
        for category in need_categories:
            if category in self.resources_db:
                for resource in self.resources_db[category]:
                    # Basic matching - would be enhanced with eligibility logic
                    if self._matches_geographic_scope(resource, user_profile):
                        relevant_resources.append({
                            **resource,
                            "category": category,
                            "match_confidence": self._calculate_match_score(resource, user_profile)
                        })
        
        # Sort by match confidence
        relevant_resources.sort(key=lambda x: x["match_confidence"], reverse=True)
        
        return relevant_resources
    
    def _matches_geographic_scope(self, resource: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Check if resource serves user's geographic area"""
        user_location = user_profile.get("geographic_area", "peoria_illinois")
        resource_area = resource.get("geographic_area", "local")
        
        # Simple matching - would be enhanced with proper geographic logic
        location_hierarchy = {
            "central_illinois": ["peoria_illinois", "pekin_illinois", "morton_illinois"],
            "greater_peoria": ["peoria_illinois", "east_peoria_illinois"],
            "peoria_county": ["peoria_illinois", "pekin_illinois", "morton_illinois"]
        }
        
        if resource_area in location_hierarchy:
            return user_location in location_hierarchy[resource_area]
        
        return resource_area == user_location or resource_area == "local"
    
    def _calculate_match_score(self, resource: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate how well resource matches user profile"""
        # Basic scoring - would be enhanced with ML/rules engine
        base_score = 0.5
        
        # Geographic match bonus
        if self._matches_geographic_scope(resource, user_profile):
            base_score += 0.3
            
        # Would add eligibility matching, service type matching, etc.
        
        return min(base_score, 1.0)