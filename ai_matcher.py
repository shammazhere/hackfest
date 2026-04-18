import os
import json
from groq import Groq
from dotenv import load_dotenv
from schemes import SCHEMES, get_scheme_by_id, fallback_keyword_match

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def match_schemes_with_ai(user_problem):
    """Use Groq AI to match schemes from live database"""
    
    # Limit schemes for AI context (top 30)
    schemes_for_ai = SCHEMES[:30]
    
    scheme_list = "\n".join([
        f"ID {s['id']}: {s['name']} - {s.get('description', '')[:150]}"
        for s in schemes_for_ai
    ])
    
    prompt = f"""You are a financial advisor for Indian citizens seeking government schemes.

USER PROBLEM: "{user_problem}"

AVAILABLE SCHEMES:
{scheme_list}

Analyze and recommend TOP 3 most relevant schemes.

Respond ONLY in JSON:
{{
  "analysis": "Brief 1-sentence analysis",
  "recommended_scheme_ids": [id1, id2, id3],
  "reasoning": {{
    "id1": "Why this fits",
    "id2": "Why this fits",
    "id3": "Why this fits"
  }}
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        matched_schemes = []
        for scheme_id in result.get('recommended_scheme_ids', [])[:3]:
            scheme = get_scheme_by_id(scheme_id)
            if scheme:
                scheme_copy = scheme.copy()
                scheme_copy['ai_reasoning'] = result.get('reasoning', {}).get(str(scheme_id), '')
                matched_schemes.append(scheme_copy)
        
        if not matched_schemes:
            matched_schemes = fallback_keyword_match(user_problem)
        
        return {
            'analysis': result.get('analysis', ''),
            'schemes': matched_schemes
        }
    
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            'analysis': 'Here are schemes matching your needs',
            'schemes': fallback_keyword_match(user_problem)
        }