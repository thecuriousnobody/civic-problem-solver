#!/usr/bin/env python3
"""
Find real URLs for Peoria/Central Illinois organizations
"""

import requests
import time

# Known real organizations in Peoria - let me try to find their actual URLs
test_urls = [
    # Peoria Rescue Mission variations
    "https://www.peoriarescuemission.com",
    "https://peoriarescuemission.com", 
    "https://peoria-rescue-mission.org",
    
    # Salvation Army variations
    "https://centralusa.salvationarmy.org",
    "https://salvationarmypeoria.org",
    "https://salvationarmy.org",
    
    # Habitat for Humanity variations  
    "https://www.habitatpeoria.org",
    "https://peoriahabitat.org",
    "https://www.habitat.org/local/peoria",
    
    # United Way
    "https://www.unitedwaypeoria.org",
    "https://unitedwayheart.org",
    
    # Greater Peoria Economic Development
    "https://www.greaterpeoria.org",
    "https://www.peoriaedc.org",
    
    # Illinois SBDC
    "https://www.illinoissbdc.net",
    "https://sbdc.siu.edu",
    
    # SCORE
    "https://www.score.org/peoria",
    "https://peoria.score.org"
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
            "error": str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        }

print("🔍 Finding real URLs for Peoria organizations...")
print("=" * 70)

valid_urls = []

for url in test_urls:
    print(f"Testing: {url}")
    result = check_url(url)
    
    if result["status"] == "VALID":
        print(f"✅ FOUND: {url} -> {result.get('final_url', url)}")
        valid_urls.append((url, result.get('final_url', url)))
    else:
        print(f"❌ Failed: {url}")
    
    time.sleep(0.3)  # Be polite

print("\n" + "=" * 70)
print("📊 REAL URLS FOUND")
print("=" * 70)
for original, final in valid_urls:
    print(f"✅ {original} -> {final}")