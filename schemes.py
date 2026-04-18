from scheme_scraper import get_all_schemes, search_schemes

# Load schemes on startup (cached)
SCHEMES = get_all_schemes()


def get_scheme_by_id(scheme_id):
    for scheme in SCHEMES:
        if scheme['id'] == scheme_id:
            return scheme
    return None


def fallback_keyword_match(user_problem):
    """Keyword-based matching"""
    problem_lower = user_problem.lower()
    scored = []
    
    for scheme in SCHEMES:
        score = 0
        for kw in scheme.get('keywords', []):
            if kw in problem_lower:
                score += 2
        # Also check name and description
        if any(word in scheme['name'].lower() for word in problem_lower.split()):
            score += 1
        if any(word in scheme.get('description', '').lower() for word in problem_lower.split()):
            score += 1
        
        if score > 0:
            scored.append((score, scheme))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:3]] if scored else SCHEMES[:3]


def refresh_schemes():
    """Force refresh schemes from API"""
    global SCHEMES
    SCHEMES = get_all_schemes(force_refresh=True)
    return len(SCHEMES)