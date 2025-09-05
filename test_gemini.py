"""
Test just the core Gemini functionality for eco-scoring.
"""
import os
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class SimpleEcoScorer:
    """Simple eco-scoring using Gemini API directly."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_product(self, product_name: str) -> dict:
        """Analyze a product's eco-friendliness."""
        
        prompt = f"""
        You are an environmental sustainability expert. Analyze the eco-friendliness of the product "{product_name}".
        
        Rate the product on a scale of 0-100 (100 being most eco-friendly) across these dimensions:
        - Overall eco-friendliness score
        - Carbon footprint (lower emissions = higher score)
        - Recyclability (easier to recycle = higher score) 
        - Sustainability (renewable materials, ethical production = higher score)
        - Environmental impact (less pollution/waste = higher score)
        
        Also provide 3-5 more eco-friendly alternatives to this product with better scores.
        
        Return your analysis in this EXACT JSON format:
        {{
            "product_name": "{product_name}",
            "category": "appropriate category",
            "eco_score": {{
                "overall_score": 75.5,
                "carbon_footprint": 70.0,
                "recyclability": 80.0,
                "sustainability": 75.0,
                "environmental_impact": 78.0,
                "reasoning": "Detailed explanation of the scoring"
            }},
            "alternatives": [
                {{
                    "name": "Alternative product name",
                    "eco_score": 85.0,
                    "features": ["eco-friendly feature 1", "eco-friendly feature 2"],
                    "brand": "Brand name",
                    "availability": "Where to buy"
                }}
            ]
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Try to extract JSON from the response
            text = response.text.strip()
            
            # Find JSON in the response (sometimes wrapped in markdown)
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_text = text[start:end].strip()
            elif "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_text = text[start:end]
            else:
                json_text = text
            
            # Parse JSON
            result = json.loads(json_text)
            return {
                "success": True,
                "data": result
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw response: {response.text[:500]}...")
            return {
                "success": False,
                "error": f"Failed to parse JSON: {e}",
                "raw_response": response.text[:500]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

async def test_products():
    """Test the eco-scoring with various products."""
    try:
        scorer = SimpleEcoScorer()
        
        test_products = [
            "iPhone 15",
            "Tesla Model 3", 
            "Bamboo Toothbrush",
            "Fast Fashion T-shirt",
            "Solar Panel"
        ]
        
        print("🌱 Testing Eco-Friendliness Scoring")
        print("=" * 60)
        
        for product in test_products:
            print(f"\n🔍 Analyzing: {product}")
            print("-" * 40)
            
            result = await scorer.analyze_product(product)
            
            if result["success"]:
                data = result["data"]
                
                print(f"✅ Analysis successful!")
                print(f"📱 Product: {data['product_name']}")
                print(f"🏷️  Category: {data['category']}")
                
                eco_score = data['eco_score']
                print(f"🌍 Overall Score: {eco_score['overall_score']:.1f}/100")
                print(f"🔥 Carbon Footprint: {eco_score['carbon_footprint']:.1f}/100")
                print(f"♻️  Recyclability: {eco_score['recyclability']:.1f}/100")
                print(f"🌿 Sustainability: {eco_score['sustainability']:.1f}/100")
                print(f"🌊 Environmental Impact: {eco_score['environmental_impact']:.1f}/100")
                
                print(f"💭 Reasoning: {eco_score['reasoning'][:150]}...")
                
                alternatives = data.get('alternatives', [])
                if alternatives:
                    print(f"\n🔄 Better Alternatives ({len(alternatives)}):")
                    for i, alt in enumerate(alternatives[:3]):
                        print(f"  {i+1}. {alt['name']} (Score: {alt['eco_score']:.1f})")
                        print(f"     Brand: {alt['brand']}")
                        print(f"     Features: {', '.join(alt['features'][:2])}")
                
            else:
                print(f"❌ Analysis failed: {result['error']}")
                if 'raw_response' in result:
                    print(f"Raw response: {result['raw_response']}")
        
        print(f"\n🎉 Testing complete!")
        
    except Exception as e:
        print(f"💥 Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_products())
