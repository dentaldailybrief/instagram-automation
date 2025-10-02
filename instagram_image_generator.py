import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
    
    # Using Inter font which is clean and modern
    font_urls = {
        'black': 'https://github.com/google/fonts/raw/main/ofl/inter/Inter-VariableFont_slnt,wght.ttf',
        'bold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf',
        'regular': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf',
        'medium': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Medium.ttf'
    }
    
    fonts = {}
    try:
        fonts['title'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 48)
        fonts['summary'] = ImageFont.truetype(
            download_font(font_urls['regular'], f"{fonts_dir}/Montserrat-Regular.ttf"), 26)
        fonts['source'] = ImageFont.truetype(
            download_font(font_urls['medium'], f"{fonts_dir}/Montserrat-Medium.ttf"), 22)
        fonts['brand'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 36)
        fonts['badge'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 20)
        print("Custom fonts loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load custom fonts: {e}")
        # Create larger default fonts
        fonts = {
            'title': ImageFont.load_default(),
            'summary': ImageFont.load_default(),
            'source': ImageFont.load_default(),
            'brand': ImageFont.load_default(),
            'badge': ImageFont.load_default()
        }
    
    return fonts

def create_rounded_rect(draw, coords, radius, fill):
    """Create a rounded rectangle using circles and rectangles."""
    x1, y1, x2, y2 = coords
    
    # Draw 4 circles for corners
    diameter = radius * 2
    draw.ellipse([x1, y1, x1 + diameter, y1 + diameter], fill=fill)
    draw.ellipse([x2 - diameter, y1, x2, y1 + diameter], fill=fill)
    draw.ellipse([x1, y2 - diameter, x1 + diameter, y2], fill=fill)
    draw.ellipse([x2 - diameter, y2 - diameter, x2, y2], fill=fill)
    
    # Draw rectangles to connect them
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

def generate_instagram_image(story, output_path="instagram_post.png"):
    """Generate a 1080x1080 Instagram image for a dental news story."""
    
    width = 1080
    height = 1080
    
    # Create a more sophisticated gradient background
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Rich gradient from dark teal to deep blue
    for y in range(height):
        ratio = y / height
        # More sophisticated color interpolation
        r = int(10 * (1 - ratio) + 5 * ratio)
        g = int(120 * (1 - ratio) + 70 * ratio)
        b = int(140 * (1 - ratio) + 160 * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
    
    # Add a subtle overlay pattern for texture
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Add subtle diagonal lines for texture
    for i in range(0, width + height, 80):
        overlay_draw.line([(i, 0), (0, i)], fill=(255, 255, 255, 10), width=1)
        overlay_draw.line([(width, i), (i, height)], fill=(255, 255, 255, 10), width=1)
    
    # Composite the overlay
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    fonts = get_fonts()
    
    # Colors
    white = (255, 255, 255)
    off_white = (250, 250, 250)
    light_gray = (220, 220, 220)
    yellow = (255, 209, 0)
    dark_overlay = (0, 0, 0, 60)
    
    margin = 60
    y_position = 80
    
    # Add "NEW" badge if story is new
    if story.get('age') == 'new':
        badge_width = 80
        badge_height = 35
        badge_x = width - margin - badge_width - 20
        badge_y = 50
        
        # Create rounded badge
        create_rounded_rect(draw, 
            (badge_x, badge_y, badge_x + badge_width, badge_y + badge_height),
            radius=17, fill=yellow)
        
        # Add NEW text
        draw.text((badge_x + badge_width//2 - 18, badge_y + 8), 
                 "NEW", font=fonts['badge'], fill=(20, 20, 20))
    
    # Brand header with background
    header_height = 120
    header_bg = Image.new('RGBA', (width, header_height), (0, 0, 0, 50))
    image.paste(header_bg, (0, 0), header_bg)
    
    # Brand name
    brand_text = "DENTAL DAILY BRIEF"
    # Calculate approximate center
    text_width_approx = len(brand_text) * 20
    brand_x = (width - text_width_approx) // 2
    
    # Add text shadow for depth
    draw.text((brand_x + 2, y_position + 2), brand_text, 
             font=fonts['brand'], fill=(0, 0, 0, 128))
    draw.text((brand_x, y_position), brand_text, 
             font=fonts['brand'], fill=white)
    
    y_position += 70
    
    # Decorative line
    line_width = 300
    line_x = (width - line_width) // 2
    draw.rectangle([(line_x, y_position), (line_x + line_width, y_position + 3)], 
                  fill=(255, 255, 255, 180))
    
    y_position += 40
    
    # Title with better wrapping
    title = story.get('title', 'Dental News Update')
    title_lines = textwrap.wrap(title, width=28, break_long_words=False)
    
    # Title background for better readability
    title_bg_height = len(title_lines[:3]) * 60 + 40
    title_bg = Image.new('RGBA', (width - 100, title_bg_height), (0, 0, 0, 40))
    image.paste(title_bg, (50, y_position - 20), title_bg)
    
    # Draw title lines with better spacing
    for i, line in enumerate(title_lines[:3]):
        text_width_approx = len(line) * 17
        title_x = (width - text_width_approx) // 2
        
        # Text shadow
        draw.text((title_x + 2, y_position + 2), line, 
                 font=fonts['title'], fill=(0, 0, 0, 128))
        # Main text
        draw.text((title_x, y_position), line, 
                 font=fonts['title'], fill=white)
        y_position += 60
    
    if len(title_lines) > 3:
        draw.text((width//2 - 20, y_position), "...", 
                 font=fonts['title'], fill=white)
        y_position += 60
    
    y_position += 30
    
    # Summary section with card-like background
    summary = story.get('summary', '')
    summary_lines = textwrap.wrap(summary, width=42, break_long_words=False)
    summary_height = min(len(summary_lines), 5) * 38 + 60
    
    # Create a card effect for summary
    card_margin = 50
    card = Image.new('RGBA', (width - 2*card_margin, summary_height), (255, 255, 255, 20))
    card_draw = ImageDraw.Draw(card)
    
    # Add gradient to card
    for y in range(summary_height):
        alpha = int(20 + (15 * y / summary_height))
        card_draw.rectangle([(0, y), (width - 2*card_margin, y + 1)], 
                           fill=(255, 255, 255, alpha))
    
    image.paste(card, (card_margin, y_position - 20), card)
    
    y_position += 20
    
    # Draw summary text with better formatting
    for line in summary_lines[:5]:
        text_width_approx = len(line) * 11
        summary_x = (width - text_width_approx) // 2
        
        # Add subtle shadow
        draw.text((summary_x + 1, y_position + 1), line, 
                 font=fonts['summary'], fill=(0, 0, 0, 80))
        draw.text((summary_x, y_position), line, 
                 font=fonts['summary'], fill=off_white)
        y_position += 38
    
    if len(summary_lines) > 5:
        draw.text((width//2 - 15, y_position), "...", 
                 font=fonts['summary'], fill=off_white)
    
    # Footer section
    footer_height = 200
    footer_y = height - footer_height
    
    # Create gradient footer
    footer_overlay = Image.new('RGBA', (width, footer_height), (0, 0, 0, 0))
    footer_draw = ImageDraw.Draw(footer_overlay)
    for y in range(footer_height):
        alpha = int(0 + (60 * y / footer_height))
        footer_draw.rectangle([(0, y), (width, y + 1)], 
                            fill=(0, 0, 0, alpha))
    image.paste(footer_overlay, (0, footer_y), footer_overlay)
    
    # Source
    source = story.get('source', 'DentalDailyBrief.com')
    source_text = f"Source: {source}"
    
    y_position = height - 140
    text_width_approx = len(source_text) * 10
    source_x = (width - text_width_approx) // 2
    draw.text((source_x, y_position), source_text, 
             font=fonts['source'], fill=light_gray)
    
    # Call to action with button effect
    cta_text = "Visit DentalDailyBrief.com"
    y_position = height - 80
    
    button_width = 400
    button_height = 50
    button_x = (width - button_width) // 2
    button_y = y_position - 15
    
    # Create button with rounded corners
    create_rounded_rect(draw,
        (button_x, button_y, button_x + button_width, button_y + button_height),
        radius=25, fill=(255, 255, 255, 25))
    
    # Add button border
    for offset in range(2):
        draw.rectangle(
            [(button_x + offset, button_y + offset), 
             (button_x + button_width - offset, button_y + button_height - offset)],
            outline=(255, 255, 255, 100 - offset * 30), width=1)
    
    text_width_approx = len(cta_text) * 12
    cta_x = (width - text_width_approx) // 2
    draw.text((cta_x, y_position), cta_text, 
             font=fonts['brand'], fill=white)
    
    # Convert back to RGB for Instagram
    image = image.convert('RGB')
    
    # Save with high quality
    image.save(output_path, 'PNG', quality=95, optimize=True)
    print(f"Instagram image saved to {output_path}")
    
    return output_path

# Example usage
if __name__ == "__main__":
    test_story = {
        'title': 'Revolutionary AI Technology Transforms Dental Diagnostics in 2024',
        'summary': 'MIT researchers have developed an artificial intelligence system that can detect cavities and gum disease with 99% accuracy, potentially revolutionizing preventive dental care worldwide.',
        'source': 'MIT Technology Review',
        'age': 'new',
        'url': 'https://example.com/story'
    }
    
    generate_instagram_image(test_story)
