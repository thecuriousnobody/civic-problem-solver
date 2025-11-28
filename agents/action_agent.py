#!/usr/bin/env python3
"""
Civic Action Agent - Next Steps Guidance
======================================

Agent that provides clear, actionable next steps for users based on
their eligibility assessment and resource matches.
"""

from crewai import Agent, LLM
from typing import Dict, Any, List
from datetime import datetime


class CivicActionAgent:
    """Agent focused on providing actionable guidance and next steps"""
    
    def __init__(self):
        self.llm = LLM(
            model="anthropic/claude-haiku-4-5-20251001",
            api_key="ANTHROPIC_API_KEY"
        )
        
        self.agent = Agent(
            role="Community Action Guide",
            goal="Transform resource matches into clear, actionable steps that help users successfully connect with services they need",
            backstory="""You are a community navigator who excels at helping people take 
            concrete action. You understand that finding resources is only half the battle - 
            people need clear, step-by-step guidance to actually access services. You provide
            practical advice, anticipate common obstacles, and offer multiple pathways to success.""",
            
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_action_plan(self, assessed_resources: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a personalized action plan based on resource matches and eligibility
        
        Args:
            assessed_resources: Resources with eligibility assessments
            user_profile: User's profile information
            
        Returns:
            Comprehensive action plan with prioritized steps
        """
        
        # Categorize resources by eligibility
        immediate_actions = []
        follow_up_actions = []
        backup_options = []
        
        for resource in assessed_resources:
            eligibility = resource.get("eligibility", {})
            status = eligibility.get("status", "unknown")
            
            if status == "eligible":
                immediate_actions.append(resource)
            elif status == "needs_verification":
                follow_up_actions.append(resource)
            else:
                backup_options.append(resource)
        
        return {
            "summary": self._create_summary(immediate_actions, follow_up_actions, user_profile),
            "immediate_steps": self._generate_immediate_steps(immediate_actions),
            "follow_up_steps": self._generate_follow_up_steps(follow_up_actions),
            "backup_options": self._generate_backup_options(backup_options),
            "preparation_checklist": self._create_preparation_checklist(immediate_actions + follow_up_actions),
            "timeline": self._suggest_timeline(immediate_actions, follow_up_actions),
            "support_contacts": self._extract_support_contacts(immediate_actions + follow_up_actions)
        }
    
    def _create_summary(self, immediate: List[Dict], follow_up: List[Dict], user_profile: Dict[str, Any]) -> str:
        """Create a personalized summary of the action plan"""
        
        summary_parts = []
        
        if immediate:
            summary_parts.append(f"Great news! I found {len(immediate)} program(s) you appear to qualify for right now.")
        
        if follow_up:
            summary_parts.append(f"There are {len(follow_up)} additional program(s) that may be a good fit - we just need to verify a few details.")
        
        if not immediate and not follow_up:
            summary_parts.append("While I didn't find exact matches for your current situation, I have some alternative resources that might help.")
        
        summary_parts.append("Here's your personalized action plan to get connected with help:")
        
        return " ".join(summary_parts)
    
    def _generate_immediate_steps(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate immediate action steps for eligible resources"""
        
        steps = []
        priority = 1
        
        for resource in resources[:3]:  # Limit to top 3 for focus
            contact = resource.get("contact", {})
            next_steps = resource.get("eligibility", {}).get("next_steps", [])
            
            step = {
                "priority": priority,
                "resource_name": resource.get("name", "Unknown"),
                "action": f"Contact {resource.get('name')} for {', '.join(resource.get('services', ['assistance']))}",
                "contact_info": contact,
                "specific_steps": next_steps,
                "urgency": "high" if priority == 1 else "medium",
                "estimated_time": "15-30 minutes for initial contact"
            }
            
            steps.append(step)
            priority += 1
        
        return steps
    
    def _generate_follow_up_steps(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate follow-up steps for resources needing verification"""
        
        steps = []
        
        for resource in resources:
            missing_info = resource.get("eligibility", {}).get("missing_info", [])
            
            if missing_info:
                step = {
                    "resource_name": resource.get("name", "Unknown"),
                    "action": f"Gather information and verify eligibility for {resource.get('name')}",
                    "missing_info": missing_info,
                    "contact_info": resource.get("contact", {}),
                    "urgency": "medium",
                    "estimated_time": "30-60 minutes"
                }
                steps.append(step)
        
        return steps
    
    def _generate_backup_options(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate backup options for ineligible or uncertain resources"""
        
        options = []
        
        for resource in resources[:2]:  # Limit backup options
            option = {
                "resource_name": resource.get("name", "Unknown"),
                "reason": "May have alternative programs or future eligibility",
                "action": f"Ask {resource.get('name')} about alternative programs or future opportunities",
                "contact_info": resource.get("contact", {}),
                "urgency": "low"
            }
            options.append(option)
        
        return options
    
    def _create_preparation_checklist(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a checklist of items to prepare before contacting programs"""
        
        checklist_items = [
            {
                "item": "Photo ID (driver's license, state ID, passport)",
                "reason": "Required for most program applications",
                "urgency": "essential"
            },
            {
                "item": "Proof of income (pay stubs, benefits statements, tax returns)",
                "reason": "Many programs have income requirements",
                "urgency": "high"
            },
            {
                "item": "Proof of residency (utility bill, lease agreement, mail)",
                "reason": "Programs serve specific geographic areas", 
                "urgency": "high"
            },
            {
                "item": "List of current household members",
                "reason": "Household size affects eligibility for many programs",
                "urgency": "medium"
            }
        ]
        
        # Add specific items based on resources
        for resource in resources:
            if "housing" in resource.get("category", "").lower():
                checklist_items.append({
                    "item": "Current housing situation documentation",
                    "reason": f"Required for {resource.get('name')} housing services",
                    "urgency": "high"
                })
        
        return checklist_items
    
    def _suggest_timeline(self, immediate: List[Dict], follow_up: List[Dict]) -> Dict[str, Any]:
        """Suggest a timeline for taking action"""
        
        timeline = {
            "this_week": [],
            "next_week": [], 
            "ongoing": []
        }
        
        # Immediate actions for this week
        for i, resource in enumerate(immediate[:2]):
            timeline["this_week"].append({
                "day": f"Day {i+1}-{i+2}",
                "action": f"Contact {resource.get('name')}",
                "goal": "Initial contact and information gathering"
            })
        
        # Follow-up actions for next week
        for resource in follow_up[:2]:
            timeline["next_week"].append({
                "action": f"Follow up with {resource.get('name')} after gathering required info",
                "goal": "Complete application or eligibility verification"
            })
        
        # Ongoing actions
        timeline["ongoing"].append({
            "action": "Check back in 2-4 weeks if applications are pending",
            "goal": "Follow up on application status and next steps"
        })
        
        return timeline
    
    def _extract_support_contacts(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and format contact information for easy reference"""
        
        contacts = []
        
        for resource in resources:
            contact_info = resource.get("contact", {})
            if contact_info:
                contact = {
                    "organization": resource.get("name", "Unknown"),
                    "phone": contact_info.get("phone"),
                    "website": contact_info.get("website"),
                    "email": contact_info.get("email"),
                    "services": resource.get("services", []),
                    "best_time_to_call": "Weekday business hours (9 AM - 5 PM)"  # Default
                }
                contacts.append(contact)
        
        return contacts