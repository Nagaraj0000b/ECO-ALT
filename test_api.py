"""
Test script to demonstrate the API functionality.
Run this after starting the API server with: python api.py
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test the eco-scoring API."""
    print("🧪 Testing Eco-Scoring API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data['status']}")
            print(f"   Gemini API: {'✅ Configured' if health_data['gemini_api_configured'] else '❌ Not configured'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running!")
        print("   Run: python api.py")
        return
    
    # Test products
    test_products = [
        "iPhone 15",
        "Tesla Model 3", 
        "Bamboo Toothbrush"
    ]
    
    print("\n2. Testing Product Analysis...")
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Analyzing: {product}")
        print("-" * 30)
        
        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"product_name": product},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data["success"]:
                    print(f"✅ Analysis successful! ({data['processing_time_ms']}ms)")
                    print(f"📱 Product: {data['product_name']}")
                    print(f"🏷️  Category: {data['category']}")
                    
                    eco_score = data['eco_score']
                    print(f"🌍 Overall Score: {eco_score['overall_score']:.1f}/100")
                    print(f"🔥 Carbon Footprint: {eco_score['carbon_footprint']:.1f}/100")
                    print(f"♻️  Recyclability: {eco_score['recyclability']:.1f}/100")
                    print(f"🌿 Sustainability: {eco_score['sustainability']:.1f}/100")
                    
                    alternatives = data.get('alternatives', [])
                    if alternatives:
                        print(f"\n🔄 Better Alternatives ({len(alternatives)}):")
                        for j, alt in enumerate(alternatives[:3]):
                            print(f"  {j+1}. {alt['name']} (Score: {alt['eco_score']:.1f})")
                            print(f"     Brand: {alt['brand']}")
                else:
                    print(f"❌ Analysis failed: {data['error']}")
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"   Response: {response.text}")
        
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    # Test documentation
    print(f"\n3. API Documentation:")
    print(f"   📋 Interactive Docs: {BASE_URL}/docs")
    print(f"   📖 ReDoc: {BASE_URL}/redoc")
    print(f"   🧪 Test Endpoint: {BASE_URL}/test")
    
    print(f"\n🎉 API testing complete!")
    print(f"\nTo test manually:")
    print(f"curl -X POST '{BASE_URL}/analyze' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"product_name\": \"iPhone 15\"}}'")

if __name__ == "__main__":
    test_api()
