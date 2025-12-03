#!/usr/bin/env python3
"""
Simple CrewAI test - test the crew system directly
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, 'agents')

async def test_crew():
    print("Testing CrewAI system...")
    
    try:
        from civic_crewai_system import run_civic_chat
        
        print("✅ Imported civic_crewai_system")
        print(f"API Key loaded: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
        
        # Simple test
        print("🧪 Running simple test: 'hi'")
        result = await run_civic_chat("hi", "test_session")
        
        print("✅ CrewAI system works!")
        print(f"Response: {result.get('response', '')[:100]}...")
        print(f"Success: {result.get('success')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crew())