import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests

def download_font(font_url, font_path):
    """Download a font file from a URL if it doesn't exist locally."""
    if not os.path.exists(font_path):
        print(f"Downloading font to {font_path}...")
        response = requests.get(font_url)
        with open(font_path, 'wb') as f:
            f.write(response.content)
        print(f"Font downloaded successfully")
    return font_path

def get_fonts():
    """Get fonts that work in GitHub Actions environment."""
    fonts_dir = "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    font_urls = {
        'bold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf',
        'regular': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf',
        'semibold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-SemiBold.ttf'
    }
    
    fonts = {}
    try:
        fonts['title'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 42)
        fonts['summary'] = ImageFont.truetype(
            download_font(font_urls['regular'], f"{fonts_dir}/Montserrat-Regular.ttf"), 28)
        fonts['source'] = ImageFont.truetype(
            download_font(font_urls['semibold'], f"{fonts_dir}/Montserrat-SemiBold.ttf"), 24)
        fonts['brand'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 32)
        fonts['cta'] = ImageFont.truetype(
            download_font(font_urls['semibold'], f"{fonts_dir}/Montserrat-SemiBold.ttf"), 26)
        print("Custom fonts loaded successfully")
    except Exception as e:
        print(f"Error loading custom fonts: {e}")
        print("Using default font")
        default = ImageFont.load_default()
        fonts = {
            'title': default,
            'summary': default,
            'source': default,
            'brand': default,
            'cta': default
        }
    
    return fonts

def generate_instagram_image(story, output_path="instagram_post.png"):
    """Generate a 1080x1080 Instagram image for a dental news story."""
    
    width = 1080
    height = 1080
    
    # Create gradient background
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Simple gradient from teal to blue
    for y in range(height):
        ratio = y / height
        r = int(0 * (1 - ratio) + 0 * ratio)
        g = int(150 * (1 - ratio) + 100 * ratio)
        b = int(160 * (1 - ratio) + 180 * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
    
    # Get fonts
    fonts = get_fonts()
    
    # Colors
    white = (255, 255, 255)
    light_gray = (240, 240, 240)
    yellow = (255, 223, 0)
    
    margin = 80
    y_position = 100
    
    # Add "NEW" badge if story is new
    if story.get('age') == 'new':
        badge_x = width - margin - 100
        badge_y = 60
        # Simple rectangle for badge
        draw.rectangle([(badge_x, badge_y), (badge_x + 100, badge_y + 40)], fill=yellow)
        draw.text((badge_x + 30, badge_y + 10), "NEW", font=fonts['source'], fill=(40, 40, 40))
    
    # Brand name at top
    brand_text = "DENTAL DAILY BRIEF"
    text_width = len(brand_text) * 18  # Approximate width
    draw.text(((width - text_width)//2, y_position), brand_text, font=fonts['brand'], fill=white)
    
    y_position += 80
    
    # Divider line
    draw.rectangle([(margin, y_position), (width - margin, y_position + 2)], fill=white)
    y_position += 30
    
    # Title (wrapped)
    title = story.get('title', 'Dental News Update')
    title_lines = textwrap.wrap(title, width=30, break_long_words=False)
    
    # Draw title lines
    for line in title_lines[:3]:
        text_width = len(line) * 14  # Approximate
        draw.text(((width - text_width)//2, y_position), line, font=fonts['title'], fill=white)
        y_position += 55
    
    if len(title_lines) > 3:
        draw.text((width//2 - 20, y_position), "...", font=fonts['title'], fill=white)
        y_position += 55
    
    y_position += 20
    
    # Summary background - simple semi-transparent rectangle
    summary = story.get('summary', '')
    summary_lines = textwrap.wrap(summary, width=38, break_long_words=False)
    summary_height = min(len(summary_lines), 6) * 40 + 60
    
    # Draw a slightly darker background for summary
    summary_bg = Image.new('RGBA', (width - 2*margin + 40, summary_height), (255, 255, 255, 30))
    image.paste(summary_bg, (margin - 20, y_position - 10), summary_bg)
    
    y_position += 30
    
    # Draw summary text
    for line in summary_lines[:6]:
        text_width = len(line) * 11  # Approximate
        draw.text(((width - text_width)//2, y_position), line, font=fonts['summary'], fill=light_gray)
        y_position += 40
    
    if len(summary_lines) > 6:
        draw.text((width//2 - 20, y_position), "...", font=fonts['summary'], fill=light_gray)
        y_position += 40
    
    # Source at bottom
    source = story.get('source', 'DentalDailyBrief.com')
    source_text = f"Source: {source}"
    
    y_position = height - 180
    text_width = len(source_text) * 10  # Approximate
    draw.text(((width - text_width)//2, y_position), source_text, font=fonts['source'], fill=light_gray)
    
    # Call to action at very bottom
    cta_text = "Visit DentalDailyBrief.com for more"
    y_position = height - 100
    text_width = len(cta_text) * 11  # Approximate
    
    # Simple background rectangle for CTA
    cta_x = (width - text_width) // 2
    draw.rectangle(
        [(cta_x - 20, y_position - 10), (cta_x + text_width + 20, y_position + 40)],
        fill=(255, 255, 255, 40)
    )
    
    draw.text((cta_x, y_position), cta_text, font=fonts['cta'], fill=white)
    
    # Save the image
    image.save(output_path, 'PNG', quality=95)
    print(f"Instagram image saved to {output_path}")
    
    return output_path

# Example usage
if __name__ == "__main__":
    test_story = {
        'title': 'Revolutionary AI Technology Transforms Dental Diagnostics',
        'summary': 'MIT researchers develop AI system detecting cavities with 99% accuracy.',
        'source': 'MIT Technology Review',
        'age': 'new',
        'url': 'https://example.com/story'
    }
    
    generate_instagram_image(test_story)
