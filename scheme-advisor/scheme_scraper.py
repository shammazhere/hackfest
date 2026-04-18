import requests
import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "schemes_cache.json"
CACHE_DURATION_HOURS = 24

# MyScheme.gov.in internal API endpoint
MYSCHEME_API = "https://api.myscheme.gov.in/search/v5/schemes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.myscheme.gov.in",
    "Referer": "https://www.myscheme.gov.in/",
    "x-api-key": "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"  # Public key from their website
}


def fetch_schemes_from_myscheme(query="", page=0, size=20):
    """Fetch schemes from MyScheme.gov.in"""
    
    params = {
        "lang": "en",
        "q": json.dumps([]) if not query else json.dumps([{"identifier": "q", "value": query}]),
        "keyword": query,
        "sort": "",
        "from": page * size,
        "size": size
    }
    
    try:
        response = requests.get(MYSCHEME_API, headers=HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fetch error: {e}")
        return None


def parse_scheme(raw_scheme, scheme_id):
    """Convert MyScheme data to our format"""
    
    # Color palette to assign
    colors = [
        {"color": "#FF6B35", "gradient": ["#FF6B35", "#F7931E"]},
        {"color": "#2E8B57", "gradient": ["#2E8B57", "#3CB371"]},
        {"color": "#4A90E2", "gradient": ["#4A90E2", "#5DADE2"]},
        {"color": "#E91E63", "gradient": ["#E91E63", "#F06292"]},
        {"color": "#9C27B0", "gradient": ["#9C27B0", "#BA68C8"]},
        {"color": "#F44336", "gradient": ["#F44336", "#EF5350"]},
        {"color": "#FF9800", "gradient": ["#FF9800", "#FFB74D"]},
        {"color": "#00BCD4", "gradient": ["#00BCD4", "#4DD0E1"]},
    ]
    
    # Icon mapping based on category
    icon_map = {
        "agriculture": "🌾", "education": "🎓", "health": "🏥",
        "business": "💼", "housing": "🏠", "women": "👩",
        "social": "🤝", "skill": "🛠️", "pension": "👴",
        "scholarship": "📚", "loan": "💰", "insurance": "🛡️"
    }
    
    fields = raw_scheme.get("fields", {})
    
    # Extract data
    name = fields.get("schemeName", "Unknown Scheme")
    short_title = fields.get("schemeShortTitle", name)
    
    # Find icon
    name_lower = name.lower()
    icon = "📋"
    for key, emoji in icon_map.items():
        if key in name_lower:
            icon = emoji
            break
    
    # Get tags/categories for keywords
    tags = fields.get("tags", [])
    keywords = [t.lower() for t in tags] if tags else []
    
    # Get benefits
    benefits_text = fields.get("briefDescription", "Government scheme benefits")
    if isinstance(benefits_text, list):
        benefits_text = " ".join(benefits_text)
    
    # Get eligibility
    eligibility = fields.get("eligibilityDescription", "Check official website for details")
    if isinstance(eligibility, list):
        eligibility = " ".join(eligibility)
    
    # Build URL
    slug = fields.get("slug", "")
    link = f"https://www.myscheme.gov.in/schemes/{slug}" if slug else "https://www.myscheme.gov.in"
    
    color_set = colors[scheme_id % len(colors)]
    
    return {
        "id": scheme_id,
        "name": short_title[:50] if short_title else name[:50],
        "full_name": name,
        "category": fields.get("level", "general").lower(),
        "tagline": fields.get("schemeShortTitle", "Government Welfare Scheme"),
        "keywords": keywords + name_lower.split()[:5],
        "benefits": benefits_text[:200] if benefits_text else "Multiple benefits available",
        "benefits_list": [
            benefits_text[:80] if benefits_text else "Government support",
            "Direct benefit transfer" if "dbt" in str(fields).lower() else "Easy application",
            "Official scheme",
            "Pan-India coverage"
        ],
        "eligibility": eligibility[:300] if eligibility else "Indian citizens",
        "description": benefits_text[:400] if benefits_text else name,
        "documents": ["Aadhaar Card", "PAN Card", "Address Proof", "Bank Account"],
        "link": link,
        "color": color_set["color"],
        "gradient": color_set["gradient"],
        "icon": icon,
        "ministry": fields.get("nodalMinistryName", "Government of India"),
        "state": fields.get("state", ["All India"])
    }


def get_all_schemes(force_refresh=False):
    """Get schemes with caching"""
    
    # Check cache
    if not force_refresh and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                print(f"✅ Loaded {len(cache['schemes'])} schemes from cache")
                return cache['schemes']
    
    # Fetch fresh data
    print("🌐 Fetching fresh schemes from MyScheme.gov.in...")
    all_schemes = []
    scheme_id = 1
    
    # Fetch multiple pages
    for page in range(3):  # Get 60 schemes (3 pages × 20)
        data = fetch_schemes_from_myscheme(page=page, size=20)
        
        if not data or 'data' not in data:
            break
        
        hits = data.get('data', {}).get('hits', {}).get('items', [])
        if not hits:
            break
        
        for item in hits:
            try:
                parsed = parse_scheme(item, scheme_id)
                all_schemes.append(parsed)
                scheme_id += 1
            except Exception as e:
                print(f"Parse error: {e}")
                continue
    
    if all_schemes:
        # Save cache
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'schemes': all_schemes
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ Cached {len(all_schemes)} schemes")
        return all_schemes
    
    # Fallback to local schemes if API fails
    print("⚠️ API failed, using fallback schemes")
    from schemes import SCHEMES as FALLBACK_SCHEMES
    return FALLBACK_SCHEMES


def search_schemes(query):
    """Search schemes by query"""
    print(f"🔍 Searching for: {query}")
    data = fetch_schemes_from_myscheme(query=query, size=10)
    
    if not data or 'data' not in data:
        return []
    
    hits = data.get('data', {}).get('hits', {}).get('items', [])
    schemes = []
    for i, item in enumerate(hits, 1):
        try:
            parsed = parse_scheme(item, i)
            schemes.append(parsed)
        except:
            continue
    
    return schemes


if __name__ == "__main__":
    # Test
    schemes = get_all_schemes(force_refresh=True)
    print(f"\nTotal schemes: {len(schemes)}")
    if schemes:
        print(f"\nFirst scheme: {schemes[0]['name']}")
        print(f"Link: {schemes[0]['link']}")