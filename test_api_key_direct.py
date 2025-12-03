#!/usr/bin/env python3
"""
Quick API key test - test Anthropic key directly
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"API key loaded: {api_key[:20]}...{api_key[-4:] if api_key else 'None'}")

try:
    import anthropic
    print("Testing Anthropic API key...")
    
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    
    print("✅ API key works!")
    print(f"Response: {response.content[0].text}")
    
except Exception as e:
    print(f"❌ API key failed: {e}")