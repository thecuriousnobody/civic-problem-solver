#!/usr/bin/env python3
"""
Quick Domain Test - Test just 3 domains to validate approach
"""

import sys
import os
sys.path.append('skills/system-testing')

from test_runner import SystemTester
import time

def quick_test():
    # Load API keys from .env
    api_keys = {}
    try:
        with open('.env') as f:
            for line in f:
                if 'ANTHROPIC_API_KEY' in line:
                    api_keys['anthropic'] = line.split('=')[1].strip().strip("'\"")
                elif 'SERPER_API_KEY' in line:
                    api_keys['serper'] = line.split('=')[1].strip().strip("'\"")
    except FileNotFoundError:
        print("❌ No .env file found")
        return
    
    if not api_keys.get('anthropic'):
        print("❌ Missing API keys")
        return
    
    tester = SystemTester()
    
    # Test just 3 domains
    test_queries = {
        "housing": "I need emergency housing assistance",
        "childcare": "I need affordable childcare for my toddler", 
        "business_grants": "I need small business grants in Central Illinois"
    }
    
    print("🧪 Quick Domain Test")
    print("=" * 50)
    
    results = {}
    for domain, query in test_queries.items():
        print(f"\n📋 Testing {domain}...")
        start = time.time()
        
        result = tester.test_api_query_endpoint(query, api_keys)
        elapsed = time.time() - start
        
        if result["status"] == "PASS":
            data = result["data"]
            resources = data.get("resources", [])
            print(f"✅ {domain}: {len(resources)} resources, {elapsed:.1f}s")
            print(f"   Category: {data.get('need_category')}")
            print(f"   Search: {data.get('search_performed')}")
            
            # Check for fake URLs
            fake_urls = []
            for res in resources:
                url = res.get('url', '')
                if '211centralillinois.org' in url:
                    fake_urls.append(f"{res.get('name')}: {url}")
            
            if fake_urls:
                print(f"   ⚠️  FAKE URLs found:")
                for fake in fake_urls:
                    print(f"      {fake}")
            
            results[domain] = {
                "success": True,
                "resources": len(resources),
                "fake_urls": len(fake_urls)
            }
        else:
            print(f"❌ {domain}: FAILED - {result.get('error')}")
            results[domain] = {"success": False}
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    total_resources = sum(r.get("resources", 0) for r in results.values() if r.get("success"))
    total_fake_urls = sum(r.get("fake_urls", 0) for r in results.values() if r.get("success"))
    
    print(f"✅ Total resources found: {total_resources}")
    print(f"⚠️  Total fake URLs: {total_fake_urls}")
    
    if total_fake_urls > 0:
        print("🚨 URL cleaning is NOT working properly!")
    else:
        print("✅ No fake URLs detected!")

if __name__ == "__main__":
    quick_test()