#!/usr/bin/env python3
"""
Test civic_flow directly - this uses YAML configs and plain Crew
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
print(f"API key: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")

sys.path.insert(0, 'agents')

try:
    from civic_flow import run_civic_flow
    
    print("Testing civic_flow with YAML configs...")
    
    result = run_civic_flow("I need food assistance", "test", {
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'serper': os.getenv('SERPER_API_KEY')
    })
    
    print("✅ Success!")
    print(f"Response: {result.get('response', '')[:100]}...")
    print(f"Success: {result.get('success')}")
    print(f"Resources: {len(result.get('resources', []))}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()