import os
from gtts import gTTS
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, TextClip, ColorClip
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from poster_generator import hex_to_rgb, create_gradient, get_font
import textwrap


def create_slide(text_title, text_body, color1, color2, size=(1280, 720)):
    """Create a single video slide"""
    width, height = size
    
    # Gradient background
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    img = create_gradient(width, height, rgb1, rgb2)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Decorative circles
    draw.ellipse([(-100, -100), (250, 250)], fill=(255, 255, 255, 25))
    draw.ellipse([(width-200, height-200), (width+100, height+100)], fill=(255, 255, 255, 20))
    
    # White card
    card_margin = 80
    draw.rounded_rectangle(
        [(card_margin, card_margin), (width - card_margin, height - card_margin)],
        radius=25,
        fill=(255, 255, 255, 240)
    )
    
    # Title
    title_font = get_font(52, bold=True)
    body_font = get_font(36)
    
    # Wrap title
    title_lines = textwrap.wrap(text_title, width=25)
    y = 150
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill=rgb1, font=title_font)
        y += 70
    
    # Body
    y += 40
    body_lines = textwrap.wrap(text_body, width=40)
    for line in body_lines[:5]:
        bbox = draw.textbbox((0, 0), line, font=body_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill='#333333', font=body_font)
        y += 50
    
    return np.array(img)


def generate_narration(text, output_path):
    """Generate TTS audio"""
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)
    return output_path


def generate_video(scheme, output_path, temp_dir='static/temp'):
    """Generate scheme explainer video"""
    
    os.makedirs(temp_dir, exist_ok=True)
    
    color1 = scheme['gradient'][0]
    color2 = scheme['gradient'][1]
    
    # Define slides with narration
    slides_data = [
        {
            'title': scheme['name'],
            'body': scheme['tagline'],
            'narration': f"Welcome! Let's learn about {scheme['name']}. {scheme['tagline']}."
        },
        {
            'title': 'What You Get',
            'body': scheme['benefits'],
            'narration': f"With this scheme, you can get {scheme['benefits']}."
        },
        {
            'title': 'Key Benefits',
            'body': ' • '.join(scheme['benefits_list'][:3]),
            'narration': f"Key benefits include: {'. '.join(scheme['benefits_list'][:3])}."
        },
        {
            'title': 'Who Can Apply',
            'body': scheme['eligibility'],
            'narration': f"This scheme is for: {scheme['eligibility']}."
        },
        {
            'title': 'Apply Now!',
            'body': f"Visit: {scheme['link']}",
            'narration': f"Ready to apply? Visit the official website and start your journey today!"
        }
    ]
    
    clips = []
    
    for i, slide in enumerate(slides_data):
        # Generate slide image
        slide_img = create_slide(slide['title'], slide['body'], color1, color2)
        
        # Generate narration
        audio_path = os.path.join(temp_dir, f"narration_{scheme['id']}_{i}.mp3")
        generate_narration(slide['narration'], audio_path)
        
        # Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration + 0.5  # small padding
        
        # Create image clip
        img_clip = ImageClip(slide_img).set_duration(duration)
        img_clip = img_clip.set_audio(audio_clip)
        
        clips.append(img_clip)
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Write video
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        verbose=False,
        logger=None
    )
    
    # Cleanup temp files
    for i in range(len(slides_data)):
        temp_audio = os.path.join(temp_dir, f"narration_{scheme['id']}_{i}.mp3")
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
    
    return output_path