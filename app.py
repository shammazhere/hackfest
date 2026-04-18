from flask import Flask, render_template, request, jsonify, url_for
import os
import threading
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Import modules
from ai_matcher import match_schemes_with_ai
from poster_generator import generate_poster
from video_generator import generate_video
from schemes import refresh_schemes, SCHEMES, get_all_schemes, get_scheme_by_id

app = Flask(__name__)

# Directories
POSTER_DIR = os.path.join('static', 'posters')
VIDEO_DIR = os.path.join('static', 'videos')

os.makedirs(POSTER_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


# ✅ Load schemes safely (NO crash at startup)
def load_schemes():
    try:
        if not SCHEMES:
            print("🌐 Loading schemes from API...")
            SCHEMES.extend(get_all_schemes())
            print(f"✅ Loaded {len(SCHEMES)} schemes")
    except Exception as e:
        print(f"❌ Failed to load schemes: {e}")

with app.app_context():
    load_schemes()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    user_problem = data.get('problem', '')

    if not user_problem:
        return jsonify({'error': 'Please describe your problem'}), 400

    # Ensure schemes are loaded
    if not SCHEMES:
        try:
            SCHEMES.extend(get_all_schemes())
        except Exception as e:
            return jsonify({'error': f'Failed to load schemes: {str(e)}'}), 500

    result = match_schemes_with_ai(user_problem)
    matched_schemes = result['schemes']

    results = []
    for scheme in matched_schemes:
        poster_filename = f"scheme_{scheme['id']}.png"
        poster_path = os.path.join(POSTER_DIR, poster_filename)

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


# ✅ Async video generation (NO crash)
@app.route('/generate-video/<int:scheme_id>', methods=['POST'])
def create_video(scheme_id):
    scheme = get_scheme_by_id(scheme_id)

    if not scheme:
        return jsonify({'error': 'Scheme not found'}), 404

    video_filename = f"scheme_{scheme_id}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)

    def generate():
        try:
            print(f"🎬 Generating video for scheme {scheme_id}")
            generate_video(scheme, video_path)
            print(f"✅ Video created: {video_filename}")
        except Exception as e:
            print(f"❌ Video error: {e}")

    # Run in background thread
    threading.Thread(target=generate).start()

    return jsonify({
        'message': 'Video generation started',
        'video_url': url_for('static', filename=f'videos/{video_filename}')
    })


@app.route('/refresh-schemes', methods=['POST'])
def refresh():
    try:
        count = refresh_schemes()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/schemes-info')
def schemes_info():
    return jsonify({
        'total': len(SCHEMES),
        'sample_names': [s['name'] for s in SCHEMES[:5]]
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))

    print(f"\n{'='*50}")
    print(f"🚀 Starting server on port {port}")
    print(f"{'='*50}\n")

    app.run(host='0.0.0.0', port=port)
