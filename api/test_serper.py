#!/usr/bin/env python3
"""
Quick test of Serper search functionality
"""

import os
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

def test_serper():
    """Test if Serper API is working"""
    
    serper_key = os.getenv("SERPER_API_KEY")
    if not serper_key:
        print("❌ No SERPER_API_KEY found in environment")
        return False
    
    print(f"✅ Found Serper API key: {serper_key[:8]}...")
    
    try:
        # Initialize Serper tool
        search_tool = SerperDevTool(api_key=serper_key)
        
        # Test search
        print("🔍 Testing search for 'Peoria housing assistance'...")
        results = search_tool.run("Peoria housing assistance 2024")
        
        if results and len(results) > 100:  # Should return substantial results
            print(f"✅ Search successful! Got {len(results)} characters of results")
            print("🔍 Sample results:")
            print(results[:300] + "..." if len(results) > 300 else results)
            return True
        else:
            print(f"⚠️ Search returned minimal results: {len(results) if results else 0} characters")
            return False
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Serper API Integration")
    print("=" * 50)
    
    success = test_serper()
    
    print("=" * 50)
    if success:
        print("✅ Serper integration is working!")
    else:
        print("❌ Serper integration has issues")