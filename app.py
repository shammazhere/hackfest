from flask import Flask, render_template, request, jsonify, url_for
import os
from dotenv import load_dotenv
from ai_matcher import match_schemes_with_ai
from poster_generator import generate_poster
from video_generator import generate_video
from schemes import refresh_schemes, SCHEMES

load_dotenv()

app = Flask(__name__)

POSTER_DIR = os.path.join('static', 'posters')
VIDEO_DIR = os.path.join('static', 'videos')
os.makedirs(POSTER_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    user_problem = data.get('problem', '')
    
    if not user_problem:
        return jsonify({'error': 'Please describe your problem'}), 400
    
    result = match_schemes_with_ai(user_problem)
    matched_schemes = result['schemes']
    
    results = []
    for scheme in matched_schemes:
        poster_filename = f"scheme_{scheme['id']}.png"
        poster_path = os.path.join(POSTER_DIR, poster_filename)
        
        # Always regenerate (since schemes might change)
        try:
            generate_poster(scheme, poster_path)
        except Exception as e:
            print(f"Poster error: {e}")
        
        results.append({
            'id': scheme['id'],
            'name': scheme['name'],
            'tagline': scheme.get('tagline', ''),
            'icon': scheme.get('icon', '📋'),
            'benefits': scheme.get('benefits', ''),
            'benefits_list': scheme.get('benefits_list', []),
            'eligibility': scheme.get('eligibility', ''),
            'description': scheme.get('description', ''),
            'documents': scheme.get('documents', []),
            'link': scheme['link'],
            'color': scheme.get('color', '#4A90E2'),
            'gradient': scheme.get('gradient', ['#4A90E2', '#5DADE2']),
            'ai_reasoning': scheme.get('ai_reasoning', ''),
            'ministry': scheme.get('ministry', ''),
            'poster_url': url_for('static', filename=f'posters/{poster_filename}')
        })
    
    return jsonify({
        'analysis': result['analysis'],
        'schemes': results,
        'total_schemes_available': len(SCHEMES)
    })


@app.route('/generate-video/<int:scheme_id>', methods=['POST'])
def create_video(scheme_id):
    from schemes import get_scheme_by_id
    
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return jsonify({'error': 'Scheme not found'}), 404
    
    video_filename = f"scheme_{scheme_id}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    
    if not os.path.exists(video_path):
        try:
            generate_video(scheme, video_path)
        except Exception as e:
            return jsonify({'error': f'Video generation failed: {str(e)}'}), 500
    
    return jsonify({
        'video_url': url_for('static', filename=f'videos/{video_filename}')
    })


@app.route('/refresh-schemes', methods=['POST'])
def refresh():
    """Refresh schemes from MyScheme.gov.in"""
    try:
        count = refresh_schemes()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/schemes-info')
def schemes_info():
    """Get info about loaded schemes"""
    return jsonify({
        'total': len(SCHEMES),
        'sample_names': [s['name'] for s in SCHEMES[:5]]
    })


if __name__ == '__main__':
    # Get the port from the environment variable (Render sets this automatically)
    # Default to 5000 if running locally
    port = int(os.environ.get("PORT", 5000))
    
    print(f"\n{'='*50}")
    print(f"📊 Loaded {len(SCHEMES)} schemes")
    print(f"🚀 Starting FinSaathi server at port {port}")
    print(f"{'='*50}\n")
    
    # Use 0.0.0.0 so the service is accessible externally
    app.run(host='0.0.0.0', port=port)