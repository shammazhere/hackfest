from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(width, height, color1, color2):
    """Create vertical gradient"""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def get_font(size, bold=False):
    """Get font with fallbacks"""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


def generate_poster(scheme, output_path):
    """Generate modern, beautiful poster"""
    
    width, height = 900, 1200
    
    # Create gradient background
    color1 = hex_to_rgb(scheme['gradient'][0])
    color2 = hex_to_rgb(scheme['gradient'][1])
    img = create_gradient(width, height, color1, color2)
    
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Decorative circles (top)
    draw.ellipse([(-100, -100), (200, 200)], fill=(255, 255, 255, 30))
    draw.ellipse([(width-150, -50), (width+100, 200)], fill=(255, 255, 255, 20))
    draw.ellipse([(width-80, height-200), (width+100, height+50)], fill=(255, 255, 255, 25))
    
    # Fonts
    tag_font = get_font(28, bold=True)
    title_font = get_font(56, bold=True)
    tagline_font = get_font(28)
    section_font = get_font(32, bold=True)
    body_font = get_font(24)
    small_font = get_font(20)
    icon_font = get_font(80)
    
    # Top tag
    draw.rounded_rectangle([(40, 40), (280, 90)], radius=25, fill=(255, 255, 255, 230))
    draw.text((60, 50), "🇮🇳 GOVT SCHEME", fill=color1, font=tag_font)
    
    # Icon (big emoji)
    try:
        draw.text((width - 150, 40), scheme['icon'], font=icon_font, embedded_color=True)
    except:
        draw.text((width - 120, 60), scheme['icon'], fill='white', font=icon_font)
    
    # Main Title
    y = 160
    title_lines = textwrap.wrap(scheme['name'], width=20)
    for line in title_lines:
        draw.text((50, y), line, fill='white', font=title_font)
        y += 70
    
    # Tagline
    draw.text((50, y), scheme['tagline'], fill=(255, 255, 255, 220), font=tagline_font)
    y += 70
    
    # White content card
    card_y = y + 20
    card_height = height - card_y - 150
    draw.rounded_rectangle(
        [(40, card_y), (width - 40, card_y + card_height)],
        radius=30,
        fill=(255, 255, 255, 240)
    )
    
    # Benefits section
    content_y = card_y + 40
    draw.text((70, content_y), "✨ KEY BENEFITS", fill=color1, font=section_font)
    content_y += 55
    
    for benefit in scheme['benefits_list'][:4]:
        draw.ellipse([(75, content_y + 8), (90, content_y + 23)], fill=color1)
        draw.text((105, content_y), benefit, fill='#2C2C2C', font=body_font)
        content_y += 40
    
    # Divider
    content_y += 20
    draw.rectangle([(70, content_y), (width - 70, content_y + 2)], fill=(200, 200, 200))
    content_y += 30
    
    # Eligibility
    draw.text((70, content_y), "👥 WHO CAN APPLY", fill=color1, font=section_font)
    content_y += 50
    elig_lines = textwrap.wrap(scheme['eligibility'], width=45)
    for line in elig_lines[:2]:
        draw.text((75, content_y), line, fill='#2C2C2C', font=body_font)
        content_y += 35
    
    # Divider
    content_y += 15
    draw.rectangle([(70, content_y), (width - 70, content_y + 2)], fill=(200, 200, 200))
    content_y += 25
    
    # Main benefit highlight
    draw.text((70, content_y), "💰 GET", fill=color1, font=section_font)
    content_y += 45
    benefit_lines = textwrap.wrap(scheme['benefits'], width=30)
    for line in benefit_lines[:2]:
        draw.text((75, content_y), line, fill=color1, font=get_font(30, bold=True))
        content_y += 40
    
    # Footer CTA
    footer_y = height - 120
    draw.rounded_rectangle(
        [(40, footer_y), (width - 40, footer_y + 90)],
        radius=20,
        fill=(255, 255, 255, 255)
    )
    draw.text((70, footer_y + 15), "📲 Apply Today!", fill=color1, font=get_font(32, bold=True))
    draw.text((70, footer_y + 55), scheme['link'][:50], fill='#666', font=small_font)
    
    img.save(output_path, quality=95)
    return output_path