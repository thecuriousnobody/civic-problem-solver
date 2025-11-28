#!/usr/bin/env python3
"""
Quick URL validator for resource URLs
"""

import requests
import time

urls_to_check = [
    "https://peoriarescuemission.org",
    "https://salvationarmyheartland.org", 
    "https://hoihabitat.org",
    "https://211centralillinois.org",
    "https://centerforpreventionofabuse.org",
    "https://uwheart.org",
    "https://peoria.score.org",
    "https://www.greaterpeoriaedc.org",
    "https://www.illinoissbdc.org"
]

def check_url(url):
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            response = requests.get(url, timeout=10, allow_redirects=True)
        
        return {
            "url": url,
            "status": "VALID" if response.status_code < 400 else "INVALID",
            "status_code": response.status_code,
            "final_url": response.url
        }
    except Exception as e:
        return {
            "url": url,
            "status": "INVALID",
            "error": str(e)
        }

print("🔍 Validating resource URLs...")
print("=" * 60)

valid_urls = []
invalid_urls = []

for url in urls_to_check:
    print(f"Checking: {url}")
    result = check_url(url)
    
    if result["status"] == "VALID":
        print(f"✅ VALID: {url} -> {result.get('final_url', url)}")
        valid_urls.append(url)
    else:
        print(f"❌ INVALID: {url} - {result.get('error', 'HTTP error')}")
        invalid_urls.append(url)
    
    time.sleep(0.5)  # Be polite

print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"✅ Valid URLs: {len(valid_urls)}")
for url in valid_urls:
    print(f"   {url}")

print(f"\n❌ Invalid URLs: {len(invalid_urls)}")
for url in invalid_urls:
    print(f"   {url}")

print(f"\n🔧 URLs to remove from codebase:")
for url in invalid_urls:
    print(f'   "{url}"')