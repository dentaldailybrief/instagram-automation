import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from io import BytesIO

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
    # Create fonts directory if it doesn't exist
    fonts_dir = "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    
    # Use Google Fonts (Open Font License) - these are reliable and free
    font_urls = {
        'bold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf',
        'regular': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Regular.ttf',
        'semibold': 'https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-SemiBold.ttf'
    }
    
    fonts = {}
    try:
        # Download fonts if needed
        fonts['title'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 
            42
        )
        fonts['summary'] = ImageFont.truetype(
            download_font(font_urls['regular'], f"{fonts_dir}/Montserrat-Regular.ttf"), 
            28
        )
        fonts['source'] = ImageFont.truetype(
            download_font(font_urls['semibold'], f"{fonts_dir}/Montserrat-SemiBold.ttf"), 
            24
        )
        fonts['brand'] = ImageFont.truetype(
            download_font(font_urls['bold'], f"{fonts_dir}/Montserrat-Bold.ttf"), 
            32
        )
        fonts['cta'] = ImageFont.truetype(
            download_font(font_urls['semibold'], f"{fonts_dir}/Montserrat-SemiBold.ttf"), 
            26
        )
        print("Custom fonts loaded successfully")
    except Exception as e:
        print(f"Error loading custom fonts: {e}")
        print("Falling back to default font")
        # Fallback to default font with larger sizes
        default = ImageFont.load_default()
        fonts = {
            'title': default,
            'summary': default,
            'source': default,
            'brand': default,
            'cta': default
        }
    
    return fonts

def create_gradient_background(width, height):
    """Create a gradient background."""
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Dental-themed gradient (teal to blue)
    start_color = (0, 150, 160)  # Teal
    end_color = (0, 100, 180)    # Blue
    
    for y in range(height):
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
    
    return image

def add_design_elements(draw, width, height):
    """Add subtle design elements to make the image more professional."""
    # Add subtle corner accents
    accent_color = (255, 255, 255, 60)  # Semi-transparent white
    
    # Top-left corner accent
    draw.ellipse([(-50, -50, 150, 150)], fill=accent_color)
    
    # Bottom-right corner accent
    draw.ellipse([(width-150, height-150, width+50, height+50)], fill=accent_color)
    
    # Add a subtle frame
    frame_color = (255, 255, 255, 80)
    draw.rectangle([(20, 20), (width-20, height-20)], outline=frame_color, width=2)

def draw_text_with_shadow(draw, position, text, font, fill, shadow_color=(0, 0, 0, 100), offset=2):
    """Draw text with a subtle shadow for better readability."""
    x, y = position
    # Draw shadow
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)

def generate_instagram_image(story, output_path="instagram_post.png"):
    """Generate a 1080x1080 Instagram image for a dental news story."""
    
    # Image dimensions (Instagram square)
    width = 1080
    height = 1080
    
    # Create gradient background
    image = create_gradient_background(width, height)
    
    # Convert to RGBA for transparency support
    image = image.convert('RGBA')
    
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    
    # Add design elements
    add_design_elements(draw, width, height)
    
    # Get fonts
    fonts = get_fonts()
    
    # Colors
    white = (255, 255, 255)
    light_gray = (240, 240, 240)
    yellow = (255, 223, 0)  # Accent color for NEW badge
    
    # Margins and spacing
    margin = 80
    content_width = width - (2 * margin)
    
    # Starting Y position
    y_position = 100
    
    # Add "NEW" badge if story is new
    if story.get('age') == 'new':
        badge_bg = yellow
        badge_text = (40, 40, 40)
        
        # Draw badge background (rounded rectangle effect)
        badge_width = 100
        badge_height = 40
        badge_x = width - margin - badge_width
        badge_y = 60
        
        # Create rounded rectangle for badge
        draw.ellipse([(badge_x, badge_y), (badge_x + 20, badge_y + badge_height)], fill=badge_bg)
        draw.ellipse([(badge_x + badge_width - 20, badge_y), (badge_x + badge_width, badge_y + badge_height)], fill=badge_bg)
        draw.rectangle([(badge_x + 10, badge_y), (badge_x + badge_width - 10, badge_y + badge_height)], fill=badge_bg)
        
        # Draw "NEW" text
        draw.text((badge_x + badge_width//2, badge_y + badge_height//2), "NEW", 
                 font=fonts['source'], fill=badge_text, anchor="mm")
    
    # Brand name at top
    brand_text = "DENTAL DAILY BRIEF"
    draw_text_with_shadow(draw, (width//2, y_position), brand_text, 
                         fonts['brand'], white, offset=3)
    # Note: We're not using anchor="mm" to maintain compatibility
    # Adjust position manually
    bbox = draw.textbbox((0, 0), brand_text, font=fonts['brand'])
    text_width = bbox[2] - bbox[0]
    draw_text_with_shadow(draw, ((width - text_width)//2, y_position), 
                         brand_text, fonts['brand'], white, offset=3)
    
    y_position += 80
    
    # Divider line
    draw.rectangle([(margin, y_position), (width - margin, y_position + 2)], 
                  fill=(255, 255, 255, 120))
    y_position += 30
    
    # Title (wrapped)
    title = story.get('title', 'Dental News Update')
    title_lines = textwrap.wrap(title, width=30, break_long_words=False)
    
    # Draw title lines
    for line in title_lines[:3]:  # Limit to 3 lines
        bbox = draw.textbbox((0, 0), line, font=fonts['title'])
        text_width = bbox[2] - bbox[0]
        draw_text_with_shadow(draw, ((width - text_width)//2, y_position), 
                             line, fonts['title'], white, offset=3)
        y_position += 55
    
    if len(title_lines) > 3:
        draw.text((width//2, y_position), "...", font=fonts['title'], 
                 fill=white, anchor="mm")
        y_position += 55
    
    y_position += 20
    
    # Summary box with background
    summary_bg_color = (255, 255, 255, 25)  # Semi-transparent white
    summary_padding = 30
    
    # Calculate summary box dimensions
    summary_y_start = y_position - 10
    summary = story.get('summary', '')
    summary_lines = textwrap.wrap(summary, width=38, break_long_words=False)
    summary_height = len(summary_lines[:6]) * 40 + (summary_padding * 2)
    
    # Draw summary background
    draw.rounded_rectangle(
        [(margin - 20, summary_y_start), 
         (width - margin + 20, summary_y_start + summary_height)],
        radius=20,
        fill=summary_bg_color
    )
    
    y_position += summary_padding
    
    # Draw summary text
    for line in summary_lines[:6]:  # Limit to 6 lines
        bbox = draw.textbbox((0, 0), line, font=fonts['summary'])
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width)//2, y_position), line, 
                 font=fonts['summary'], fill=light_gray)
        y_position += 40
    
    if len(summary_lines) > 6:
        draw.text((width//2, y_position), "...", font=fonts['summary'], 
                 fill=light_gray, anchor="mm")
        y_position += 40
    
    y_position += 30
    
    # Source at bottom
    source = story.get('source', 'DentalDailyBrief.com')
    source_text = f"Source: {source}"
    
    # Position source near bottom
    y_position = height - 180
    
    bbox = draw.textbbox((0, 0), source_text, font=fonts['source'])
    text_width = bbox[2] - bbox[0]
    draw.text(((width - text_width)//2, y_position), source_text, 
             font=fonts['source'], fill=light_gray)
    
    # Call to action at very bottom
    cta_text = "Visit DentalDailyBrief.com for more"
    y_position = height - 100
    
    # Draw CTA with background
    cta_bg = (255, 255, 255, 40)
    cta_padding = 20
    bbox = draw.textbbox((0, 0), cta_text, font=fonts['cta'])
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    cta_x = (width - text_width) // 2
    draw.rounded_rectangle(
        [(cta_x - cta_padding, y_position - 10), 
         (cta_x + text_width + cta_padding, y_position + text_height + 10)],
        radius=25,
        fill=cta_bg
    )
    
    draw_text_with_shadow(draw, (cta_x, y_position), cta_text, 
                         fonts['cta'], white, offset=2)
    
    # Convert back to RGB for saving
    image = image.convert('RGB')
    
    # Save the image
    image.save(output_path, 'PNG', quality=95)
    print(f"Instagram image saved to {output_path}")
    
    return output_path

# Example usage
if __name__ == "__main__":
    # Test story
    test_story = {
        'title': 'Revolutionary AI Technology Transforms Dental Diagnostics in 2024',
        'summary': 'A groundbreaking artificial intelligence system developed by researchers at MIT can now detect cavities and gum disease with 99% accuracy, potentially revolutionizing preventive dental care and making early detection more accessible to patients worldwide.',
        'source': 'MIT Technology Review',
        'age': 'new',
        'url': 'https://example.com/story'
    }
    
    generate_instagram_image(test_story)
