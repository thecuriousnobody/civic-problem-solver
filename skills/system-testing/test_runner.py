#!/usr/bin/env python3
"""
System Testing & Validation Runner
Comprehensive testing suite for civic resource systems
"""

import asyncio
import json
import requests
import time
import sys
import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Any
from pathlib import Path

class SystemTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = {}
        self.errors = []
        
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def test_api_query_endpoint(self, message: str, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Test the main query endpoint with real data"""
        try:
            start_time = time.time()
            
            payload = {
                "message": message,
                "session_id": "test_session",
                "api_keys": api_keys
            }
            
            response = requests.post(
                f"{self.base_url}/api/query",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "PASS",
                    "response_time": end_time - start_time,
                    "search_performed": data.get("search_performed", False),
                    "resources_count": len(data.get("resources", [])),
                    "need_category": data.get("need_category"),
                    "has_valid_response": bool(data.get("response", "").strip()),
                    "execution_time_ms": data.get("execution_time_ms"),
                    "step_timings": data.get("step_timings"),
                    "data": data
                }
            else:
                return {
                    "status": "FAIL",
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "error": response.text
                }
                
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate that a URL actually exists and is accessible"""
        try:
            # Clean URL
            if not url.startswith('http'):
                url = f"https://{url}"
            
            # Test with HEAD request first (faster)
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code >= 400:
                # Try GET if HEAD fails
                response = requests.get(url, timeout=10, allow_redirects=True)
            
            return {
                "url": url,
                "status": "PASS" if response.status_code < 400 else "FAIL",
                "status_code": response.status_code,
                "final_url": response.url,
                "accessible": response.status_code < 400
            }
            
        except Exception as e:
            return {
                "url": url,
                "status": "FAIL",
                "error": str(e),
                "accessible": False
            }
    
    def validate_phone_number(self, phone: str) -> Dict[str, Any]:
        """Basic validation of phone number format"""
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid US phone number
        if len(digits_only) == 10:
            formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
            return {"phone": phone, "valid": True, "formatted": formatted}
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            formatted = f"1-({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
            return {"phone": phone, "valid": True, "formatted": formatted}
        else:
            return {"phone": phone, "valid": False, "reason": "Invalid format"}
    
    def test_search_functionality(self, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Test if search tools are actually being called"""
        # Test with a query that should trigger search
        result = self.test_api_query_endpoint("I need emergency housing help", api_keys)
        
        if result["status"] == "PASS":
            data = result["data"]
            
            # Check if search was actually performed
            search_performed = data.get("search_performed", False)
            resources = data.get("resources", [])
            
            return {
                "status": "PASS" if search_performed else "FAIL",
                "search_actually_performed": search_performed,
                "resources_found": len(resources),
                "response_contains_search_results": "search" in data.get("response_source", ""),
                "execution_time": result["response_time"],
                "details": {
                    "need_category": data.get("need_category"),
                    "response_source": data.get("response_source"),
                    "step_timings": data.get("step_timings", {})
                }
            }
        else:
            return {"status": "FAIL", "error": "API query failed", "details": result}
    
    def validate_resources_data(self, resources: List[Dict]) -> Dict[str, Any]:
        """Validate all resource data for accuracy"""
        results = {
            "total_resources": len(resources),
            "url_validation": [],
            "phone_validation": [],
            "issues": []
        }
        
        for i, resource in enumerate(resources):
            # Validate URL if present
            if resource.get("url"):
                url_result = self.validate_url(resource["url"])
                url_result["resource_name"] = resource.get("name", f"Resource {i}")
                results["url_validation"].append(url_result)
                
                if not url_result["accessible"]:
                    results["issues"].append(f"Resource '{resource.get('name')}' has broken URL: {resource['url']}")
            
            # Validate phone if present
            if resource.get("contact") and "(" in resource["contact"]:
                phone_result = self.validate_phone_number(resource["contact"])
                phone_result["resource_name"] = resource.get("name", f"Resource {i}")
                results["phone_validation"].append(phone_result)
                
                if not phone_result["valid"]:
                    results["issues"].append(f"Resource '{resource.get('name')}' has invalid phone: {resource['contact']}")
        
        return results
    
    def test_resource_domains(self, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Test different resource domains systematically"""
        
        # Define test domains with representative queries
        test_domains = {
            "housing": {
                "query": "I need emergency housing assistance",
                "expected_categories": ["housing", "emergency", "shelter"]
            },
            "childcare": {
                "query": "I need affordable childcare for my toddler",
                "expected_categories": ["childcare", "family_services", "child"]
            },
            "business_grants": {
                "query": "I need small business grants and funding in Central Illinois",
                "expected_categories": ["business", "financial", "entrepreneurship"]
            },
            "healthcare": {
                "query": "I need low-cost medical care and health services",
                "expected_categories": ["healthcare", "medical", "health"]
            },
            "food_assistance": {
                "query": "I need food assistance and emergency food help",
                "expected_categories": ["food", "nutrition", "emergency"]
            },
            "transportation": {
                "query": "I need transportation help for disability services",
                "expected_categories": ["transportation", "disability", "mobility"]
            }
        }
        
        domain_results = {}
        
        for domain_name, domain_config in test_domains.items():
            print(f"   📋 Testing {domain_name} domain...")
            
            start_time = time.time()
            result = self.test_api_query_endpoint(domain_config["query"], api_keys)
            end_time = time.time()
            
            # Analyze results
            if result["status"] == "PASS":
                data = result["data"]
                resources_count = len(data.get("resources", []))
                need_category = data.get("need_category", "").lower()
                
                # Check if response is relevant to domain
                expected_cats = domain_config["expected_categories"]
                category_match = any(cat in need_category for cat in expected_cats)
                
                domain_results[domain_name] = {
                    "status": "PASS",
                    "query": domain_config["query"],
                    "response_time": end_time - start_time,
                    "resources_found": resources_count,
                    "need_category": data.get("need_category"),
                    "search_performed": data.get("search_performed", False),
                    "category_match": category_match,
                    "data": data
                }
                
                print(f"     ✅ {domain_name}: {resources_count} resources, {end_time - start_time:.1f}s")
                if not category_match:
                    print(f"     ⚠️  Category mismatch: got '{need_category}', expected one of {expected_cats}")
                    
            else:
                domain_results[domain_name] = {
                    "status": "FAIL",
                    "query": domain_config["query"],
                    "error": result.get("error", "Unknown error"),
                    "response_time": end_time - start_time
                }
                print(f"     ❌ {domain_name}: FAILED - {result.get('error', 'Unknown error')}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        return domain_results
    
    async def run_comprehensive_test(self, api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🧪 Starting Comprehensive System Test...")
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {}
        }
        
        # 1. Test Health Endpoint
        print("1️⃣ Testing health endpoint...")
        results["tests"]["health"] = self.test_health_endpoint()
        
        # 2. Test Basic Query
        print("2️⃣ Testing basic query...")
        basic_query = self.test_api_query_endpoint("hi", api_keys)
        results["tests"]["basic_query"] = basic_query
        
        # 3. Test Search Functionality
        print("3️⃣ Testing search functionality...")
        search_test = self.test_search_functionality(api_keys)
        results["tests"]["search"] = search_test
        
        # 4. Test Resource Domains
        print("4️⃣ Testing resource domains...")
        domain_tests = self.test_resource_domains(api_keys)
        results["tests"]["resource_domains"] = domain_tests
        
        # 5. Validate All Resource Data
        print("5️⃣ Validating all resource data...")
        all_resources = []
        for domain_name, domain_result in domain_tests.items():
            if domain_result.get("status") == "PASS":
                resources = domain_result.get("data", {}).get("resources", [])
                all_resources.extend(resources)
        
        if all_resources:
            validation_result = self.validate_resources_data(all_resources)
            validation_result["domains_tested"] = list(domain_tests.keys())
            validation_result["total_resources_tested"] = len(all_resources)
            results["tests"]["resource_validation"] = validation_result
        else:
            results["tests"]["resource_validation"] = {
                "status": "FAIL",
                "error": "No resources found across any domain",
                "domains_tested": list(domain_tests.keys())
            }
        
        # Summary
        results["summary"] = self.generate_summary(results["tests"])
        
        return results
    
    def generate_summary(self, tests: Dict) -> Dict[str, Any]:
        """Generate test summary and recommendations"""
        summary = {
            "total_tests": len(tests),
            "passed": 0,
            "failed": 0,
            "critical_issues": [],
            "recommendations": []
        }
        
        for test_name, test_result in tests.items():
            if test_name == "resource_domains":
                # Handle domain tests specially
                domain_passed = 0
                domain_failed = 0
                for domain_name, domain_result in test_result.items():
                    if domain_result.get("status") == "PASS":
                        domain_passed += 1
                    else:
                        domain_failed += 1
                        summary["critical_issues"].append(f"domain_{domain_name}: {domain_result.get('error', 'Failed')}")
                
                # Count domains as individual tests
                summary["passed"] += domain_passed
                summary["failed"] += domain_failed
                summary["total_tests"] += len(test_result) - 1  # Adjust for the extra count
                
            elif test_result.get("status") == "PASS":
                summary["passed"] += 1
            else:
                summary["failed"] += 1
                summary["critical_issues"].append(f"{test_name}: {test_result.get('error', 'Failed')}")
        
        # Generate recommendations
        if "search" in tests and tests["search"].get("status") == "FAIL":
            summary["recommendations"].append("🔍 Search functionality not working - verify Serper API key and tool integration")
        
        if "resource_domains" in tests:
            domains = tests["resource_domains"]
            failed_domains = [name for name, result in domains.items() if result.get("status") != "PASS"]
            if failed_domains:
                summary["recommendations"].append(f"🏗️ Fix {len(failed_domains)} failing resource domains: {', '.join(failed_domains)}")
        
        if "resource_validation" in tests:
            issues = tests["resource_validation"].get("issues", [])
            if issues:
                summary["recommendations"].append(f"📋 Fix {len(issues)} resource data issues (broken URLs/phones)")
        
        if summary["failed"] > summary["passed"]:
            summary["recommendations"].append("⚠️ System has major issues - do not deploy until fixed")
        
        return summary

def main():
    """Run the comprehensive test suite"""
    # Load API keys
    env_file = Path(".env")
    api_keys = {}
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "ANTHROPIC_API_KEY" in line:
                    api_keys["anthropic"] = line.split("=")[1].strip().strip("'\"")
                elif "SERPER_API_KEY" in line:
                    api_keys["serper"] = line.split("=")[1].strip().strip("'\"")
    
    if not api_keys.get("anthropic"):
        print("❌ Missing ANTHROPIC_API_KEY in .env file")
        return
    
    # Run tests
    tester = SystemTester()
    
    async def run_tests():
        results = await tester.run_comprehensive_test(api_keys)
        
        # Print results
        print("\n" + "="*70)
        print("📊 TEST RESULTS SUMMARY")
        print("="*70)
        
        summary = results["summary"]
        print(f"✅ Passed: {summary['passed']}/{summary['total_tests']}")
        print(f"❌ Failed: {summary['failed']}/{summary['total_tests']}")
        
        if summary["critical_issues"]:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in summary["critical_issues"]:
                print(f"   • {issue}")
        
        if summary["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in summary["recommendations"]:
                print(f"   • {rec}")
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed results saved to test_results.json")
        
        return summary["failed"] == 0
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()