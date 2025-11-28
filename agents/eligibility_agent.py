#!/usr/bin/env python3
"""
Civic Eligibility Agent - Program Matching Logic
==============================================

Agent that determines user eligibility for specific programs and services
based on their profile and program requirements.
"""

from crewai import Agent, LLM
from typing import Dict, Any, List


class CivicEligibilityAgent:
    """Agent focused on matching users to programs they qualify for"""
    
    def __init__(self):
        self.llm = LLM(
            model="anthropic/claude-haiku-4-5-20251001",
            api_key="ANTHROPIC_API_KEY"
        )
        
        self.agent = Agent(
            role="Eligibility Assessment Specialist", 
            goal="Accurately determine user eligibility for civic programs and services based on their profile and program requirements",
            backstory="""You are an expert in program eligibility requirements across various
            civic services. You understand complex eligibility criteria including income limits,
            age requirements, residency requirements, and special circumstances. You help people
            navigate bureaucratic requirements to find programs they actually qualify for.""",
            
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def assess_eligibility(self, user_profile: Dict[str, Any], resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Determine eligibility for each resource based on user profile
        
        Args:
            user_profile: User's demographic and situation info
            resources: List of potential resources from ResourceAgent
            
        Returns:
            List of resources with eligibility assessment added
        """
        
        assessed_resources = []
        
        for resource in resources:
            eligibility_result = self._evaluate_single_resource(user_profile, resource)
            
            assessed_resources.append({
                **resource,
                "eligibility": eligibility_result
            })
        
        return assessed_resources
    
    def _evaluate_single_resource(self, user_profile: Dict[str, Any], resource: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate eligibility for a single resource"""
        
        eligibility_checks = []
        overall_status = "eligible"  # Start optimistic
        missing_info = []
        
        # Income eligibility check
        income_result = self._check_income_eligibility(user_profile, resource)
        eligibility_checks.append(income_result)
        if income_result["status"] == "ineligible":
            overall_status = "ineligible"
        elif income_result["status"] == "unknown":
            overall_status = "needs_verification"
            missing_info.extend(income_result.get("missing_info", []))
        
        # Age eligibility check
        age_result = self._check_age_eligibility(user_profile, resource)
        eligibility_checks.append(age_result)
        if age_result["status"] == "ineligible":
            overall_status = "ineligible"
        elif age_result["status"] == "unknown" and overall_status != "ineligible":
            overall_status = "needs_verification"
            missing_info.extend(age_result.get("missing_info", []))
        
        # Residency check
        residency_result = self._check_residency_eligibility(user_profile, resource)
        eligibility_checks.append(residency_result)
        if residency_result["status"] == "ineligible":
            overall_status = "ineligible"
        elif residency_result["status"] == "unknown" and overall_status != "ineligible":
            overall_status = "needs_verification"
            missing_info.extend(residency_result.get("missing_info", []))
        
        return {
            "status": overall_status,
            "confidence": self._calculate_confidence(eligibility_checks),
            "checks_performed": eligibility_checks,
            "missing_info": list(set(missing_info)),
            "next_steps": self._generate_next_steps(overall_status, resource, missing_info)
        }
    
    def _check_income_eligibility(self, user_profile: Dict[str, Any], resource: Dict[str, Any]) -> Dict[str, Any]:
        """Check if user meets income requirements"""
        
        user_income = user_profile.get("income_level")
        resource_requirements = resource.get("eligibility", "")
        
        if not user_income:
            return {
                "type": "income",
                "status": "unknown",
                "missing_info": ["household_income"],
                "message": "Income information needed to verify eligibility"
            }
        
        if "income" not in resource_requirements.lower():
            return {
                "type": "income", 
                "status": "eligible",
                "message": "No income restrictions"
            }
        
        # Basic income checking - would be enhanced with actual thresholds
        if "low income" in resource_requirements.lower() and user_income in ["low", "very_low"]:
            return {
                "type": "income",
                "status": "eligible", 
                "message": "Meets income requirements"
            }
        
        return {
            "type": "income",
            "status": "needs_verification",
            "message": "Income eligibility requires verification with program"
        }
    
    def _check_age_eligibility(self, user_profile: Dict[str, Any], resource: Dict[str, Any]) -> Dict[str, Any]:
        """Check age-based eligibility"""
        
        age_range = user_profile.get("age_range")
        resource_name = resource.get("name", "").lower()
        
        # Check for age-specific programs
        if "senior" in resource_name or "elderly" in resource_name:
            if age_range == "65_plus":
                return {"type": "age", "status": "eligible", "message": "Meets age requirement"}
            elif not age_range:
                return {"type": "age", "status": "unknown", "missing_info": ["age"], "message": "Age verification needed"}
            else:
                return {"type": "age", "status": "ineligible", "message": "Does not meet age requirement (65+)"}
        
        if "youth" in resource_name:
            if age_range in ["under_18", "18_24"]:
                return {"type": "age", "status": "eligible", "message": "Meets age requirement"}
            elif not age_range:
                return {"type": "age", "status": "unknown", "missing_info": ["age"], "message": "Age verification needed"}
            else:
                return {"type": "age", "status": "ineligible", "message": "Does not meet youth age requirement"}
        
        return {"type": "age", "status": "eligible", "message": "No age restrictions"}
    
    def _check_residency_eligibility(self, user_profile: Dict[str, Any], resource: Dict[str, Any]) -> Dict[str, Any]:
        """Check residency requirements"""
        
        user_location = user_profile.get("geographic_area", "unknown")
        resource_area = resource.get("geographic_area", "local")
        
        if user_location == "unknown":
            return {
                "type": "residency",
                "status": "unknown", 
                "missing_info": ["location"],
                "message": "Location needed to verify service area eligibility"
            }
        
        # Basic residency check - matches the geographic logic from resource_agent
        if resource_area == "local" or user_location in resource_area:
            return {
                "type": "residency",
                "status": "eligible",
                "message": "Lives in service area"
            }
        
        return {
            "type": "residency",
            "status": "needs_verification",
            "message": "Service area eligibility requires verification"
        }
    
    def _calculate_confidence(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on eligibility checks"""
        if not checks:
            return 0.0
        
        eligible_count = sum(1 for check in checks if check["status"] == "eligible")
        total_checks = len(checks)
        
        return eligible_count / total_checks
    
    def _generate_next_steps(self, status: str, resource: Dict[str, Any], missing_info: List[str]) -> List[str]:
        """Generate actionable next steps based on eligibility assessment"""
        
        steps = []
        
        if status == "eligible":
            contact = resource.get("contact", {})
            if contact.get("phone"):
                steps.append(f"Call {contact['phone']} to apply or get more information")
            if contact.get("website"):
                steps.append(f"Visit {contact['website']} for online application")
            steps.append("Have required documents ready (ID, proof of income, etc.)")
        
        elif status == "needs_verification":
            if missing_info:
                steps.append(f"Gather missing information: {', '.join(missing_info)}")
            contact = resource.get("contact", {})
            if contact.get("phone"):
                steps.append(f"Call {contact['phone']} to verify eligibility requirements")
        
        elif status == "ineligible":
            steps.append("This program may not be a match for your current situation")
            steps.append("Consider asking about alternative programs or resources")
        
        return steps