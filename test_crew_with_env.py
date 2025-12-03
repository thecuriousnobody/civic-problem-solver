#!/usr/bin/env python3
"""
Test crew system with .env file (bypass frontend API key issues)
"""
import os
import asyncio
from dotenv import load_dotenv

# Load the .env file first
load_dotenv()

print(f"Loaded API key: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")

import sys
sys.path.insert(0, 'agents')

async def test_with_env():
    print("Testing CrewAI with .env file...")
    
    try:
        from civic_crewai_system import run_civic_chat
        
        # Test with a civic need that should trigger search
        print("🧪 Testing: 'I need food assistance in Peoria'")
        result = await run_civic_chat("I need food assistance in Peoria", "test_session")
        
        print("✅ Success!")
        print(f"Response: {result.get('response', '')[:200]}...")
        print(f"Search performed: {result.get('search_performed')}")
        print(f"Resources found: {len(result.get('resources', []))}")
        print(f"Success: {result.get('success')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_env())