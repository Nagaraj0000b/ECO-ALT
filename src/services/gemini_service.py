import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from datetime import datetime
import asyncio


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    async def analyze_product(self, product_name: str) -> Dict[str, Any]:
        """Analyze a product's eco-friendliness using Gemini AI"""
        
        if not self.model:
            # Return mock data if no API key configured
            return self._create_mock_analysis(product_name)
        
        try:
            prompt = self._create_analysis_prompt(product_name)
            
            # Generate analysis using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            # Parse the response
            analysis_text = response.text
            
            # Try to extract JSON from the response
            try:
                # Look for JSON content between ```json markers
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    json_text = analysis_text[json_start:json_end].strip()
                    analysis_data = json.loads(json_text)
                else:
                    # Try to parse the entire response as JSON
                    analysis_data = json.loads(analysis_text)
                
                return self._validate_analysis(analysis_data, product_name)
                
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._parse_text_response(analysis_text, product_name)
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._create_mock_analysis(product_name)
    
    def _create_analysis_prompt(self, product_name: str) -> str:
        """Create a detailed prompt for eco-friendliness analysis"""
        
        return f"""
Analyze the eco-friendliness of "{product_name}" and provide a comprehensive environmental assessment.

Please respond with a JSON object containing:

1. "category": The product category (e.g., "Electronics & Technology", "Transportation", "Clothing & Textiles", etc.)
2. "brand": The brand/manufacturer if identifiable
3. "eco_score": An object with:
   - "overall_score": Overall eco-friendliness score (0-100)
   - "carbon_footprint": Carbon footprint score (0-100, higher is better)
   - "recyclability": Recyclability score (0-100)
   - "sustainability": Sustainability practices score (0-100)
   - "environmental_impact": Environmental impact score (0-100, higher means less impact)
   - "reasoning": Detailed explanation of the scoring (2-3 sentences)
   - "confidence_score": Confidence in the analysis (0.0-1.0)

4. "alternatives": Array of eco-friendly alternatives, each with:
   - "name": Alternative product name
   - "eco_score": Its eco-friendliness score (0-100)
   - "features": Array of eco-friendly features
   - "brand": Brand name
   - "comparison": Why it's better environmentally
   - "availability": Where to find it (optional)

5. "features": Array of notable features of the original product
6. "tags": Array of relevant tags for categorization

Focus on:
- Manufacturing processes and materials
- Energy efficiency and consumption
- End-of-life disposal and recyclability
- Supply chain sustainability
- Company environmental policies
- Certifications (Energy Star, EPEAT, etc.)

Be specific and provide actionable insights. If information is limited, indicate uncertainty in the confidence score.

Example format:
```json
{{
  "category": "Electronics & Technology",
  "brand": "Apple",
  "eco_score": {{
    "overall_score": 65.5,
    "carbon_footprint": 60.0,
    "recyclability": 75.0,
    "sustainability": 65.0,
    "environmental_impact": 68.0,
    "reasoning": "Good recyclability programs but high manufacturing carbon footprint. Uses some recycled materials.",
    "confidence_score": 0.85
  }},
  "alternatives": [
    {{
      "name": "Fairphone 5",
      "eco_score": 85.0,
      "features": ["Modular design", "Fair trade materials", "Repairable"],
      "brand": "Fairphone",
      "comparison": "Built with sustainability as core principle",
      "availability": "Europe, online"
    }}
  ],
  "features": ["Premium materials", "Long software support"],
  "tags": ["smartphone", "electronics", "premium"]
}}
```
"""
    
    def _validate_analysis(self, data: Dict[str, Any], product_name: str) -> Dict[str, Any]:
        """Validate and sanitize the analysis data"""
        
        # Ensure required fields exist
        if "eco_score" not in data:
            data["eco_score"] = self._create_default_eco_score()
        
        # Validate eco_score structure
        eco_score = data["eco_score"]
        required_score_fields = [
            "overall_score", "carbon_footprint", "recyclability", 
            "sustainability", "environmental_impact"
        ]
        
        for field in required_score_fields:
            if field not in eco_score:
                eco_score[field] = 50.0  # Default middle score
            else:
                # Clamp values between 0 and 100
                eco_score[field] = max(0.0, min(100.0, float(eco_score[field])))
        
        if "reasoning" not in eco_score:
            eco_score["reasoning"] = f"Analysis for {product_name}"
        
        if "confidence_score" not in eco_score:
            eco_score["confidence_score"] = 0.5
        else:
            eco_score["confidence_score"] = max(0.0, min(1.0, float(eco_score["confidence_score"])))
        
        # Ensure other required fields
        data.setdefault("category", "Unknown")
        data.setdefault("brand", None)
        data.setdefault("alternatives", [])
        data.setdefault("features", [])
        data.setdefault("tags", [])
        
        # Validate alternatives
        for alt in data["alternatives"]:
            if "eco_score" in alt:
                alt["eco_score"] = max(0.0, min(100.0, float(alt["eco_score"])))
            else:
                alt["eco_score"] = 75.0  # Default good score for alternatives
            
            alt.setdefault("features", [])
            alt.setdefault("brand", "Unknown")
            alt.setdefault("comparison", "Eco-friendly alternative")
        
        return data
    
    def _parse_text_response(self, text: str, product_name: str) -> Dict[str, Any]:
        """Parse a text response into structured data"""
        
        # This is a simplified parser - in production you'd want more sophisticated NLP
        lines = text.split('\n')
        
        # Extract basic information using simple pattern matching
        category = "Unknown"
        brand = None
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ["category:", "type:", "product type:"]):
                category = line.split(":", 1)[1].strip() if ":" in line else "Unknown"
            elif any(word in line_lower for word in ["brand:", "manufacturer:", "made by"]):
                brand = line.split(":", 1)[1].strip() if ":" in line else None
        
        return {
            "category": category,
            "brand": brand,
            "eco_score": self._create_default_eco_score(reasoning=f"Text analysis for {product_name}"),
            "alternatives": [
                {
                    "name": f"Eco-friendly alternative to {product_name}",
                    "eco_score": 80.0,
                    "features": ["Sustainable materials", "Lower carbon footprint"],
                    "brand": "EcoTech",
                    "comparison": "More environmentally responsible option"
                }
            ],
            "features": ["Standard features"],
            "tags": [category.lower().replace(" ", "_")]
        }
    
    def _create_default_eco_score(self, reasoning: str = "Default analysis") -> Dict[str, Any]:
        """Create a default eco score structure"""
        
        return {
            "overall_score": 50.0,
            "carbon_footprint": 50.0,
            "recyclability": 50.0,
            "sustainability": 50.0,
            "environmental_impact": 50.0,
            "reasoning": reasoning,
            "confidence_score": 0.3
        }
    
    def _create_mock_analysis(self, product_name: str) -> Dict[str, Any]:
        """Create mock analysis data for testing"""
        
        # Determine category based on product name keywords
        name_lower = product_name.lower()
        if any(word in name_lower for word in ["iphone", "samsung", "phone", "smartphone"]):
            category = "Electronics & Technology"
            brand = "Apple" if "iphone" in name_lower else "Samsung" if "samsung" in name_lower else "Unknown"
            tags = ["smartphone", "electronics", "mobile"]
        elif any(word in name_lower for word in ["tesla", "car", "vehicle", "model"]):
            category = "Transportation"
            brand = "Tesla" if "tesla" in name_lower else "Unknown"
            tags = ["car", "transportation", "vehicle"]
        elif any(word in name_lower for word in ["laptop", "computer", "macbook"]):
            category = "Electronics & Technology"
            brand = "Apple" if "macbook" in name_lower else "Unknown"
            tags = ["laptop", "computer", "electronics"]
        else:
            category = "General"
            brand = None
            tags = ["product"]
        
        # Generate realistic but varied scores
        base_score = 55 + (hash(product_name) % 30)  # 55-85 range
        
        return {
            "category": category,
            "brand": brand,
            "eco_score": {
                "overall_score": base_score,
                "carbon_footprint": base_score + (hash(product_name + "carbon") % 20) - 10,
                "recyclability": base_score + (hash(product_name + "recycle") % 20) - 10,
                "sustainability": base_score + (hash(product_name + "sustain") % 20) - 10,
                "environmental_impact": base_score + (hash(product_name + "impact") % 20) - 10,
                "reasoning": f"Mock analysis for {product_name}. Scores based on typical products in this category.",
                "confidence_score": 0.7
            },
            "alternatives": [
                {
                    "name": f"Eco-friendly alternative to {product_name}",
                    "eco_score": min(95, base_score + 20),
                    "features": ["Sustainable materials", "Lower carbon footprint", "Recyclable design"],
                    "brand": "EcoTech",
                    "comparison": "Designed with environmental impact as primary consideration",
                    "availability": "Online retailers"
                }
            ],
            "features": ["Standard build quality", "Market-typical performance"],
            "tags": tags
        }
