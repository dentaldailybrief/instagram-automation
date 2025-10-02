"""
Instagram Single Image Generator for Dental Daily Brief
Generates one image per story
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from datetime import datetime

class InstagramImageGenerator:
    def __init__(self):
        # Instagram optimal dimensions (1080x1080)
        self.width = 1080
        self.height = 1080
        
        # Brand colors
        self.bg_color = '#FFFFFF'
        self.primary_color = '#2C5282'  # Dark blue
        self.accent_color = '#4299E1'   # Light blue
        self.text_color = '#1A202C'
        
    def create_story_image(self, headline, summary, source):
        """Create a single Instagram post image for one story"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("Arial-Bold.ttf", 70)
            summary_font = ImageFont.truetype("Arial.ttf", 45)
            meta_font = ImageFont.truetype("Arial.ttf", 35)
            brand_font = ImageFont.truetype("Arial-Bold.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            summary_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
        
        # Header bar with branding
        draw.rectangle([(0, 0), (self.width, 180)], fill=self.primary_color)
        brand_text = "DENTAL DAILY BRIEF"
        brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_width = brand_bbox[2] - brand_bbox[0]
        draw.text(((self.width - brand_width) / 2, 70), brand_text, 
                 fill='white', font=brand_font)
        
        # Content area with padding
        padding = 60
        content_y = 240
        
        # Wrap and draw headline
        wrapped_headline = textwrap.fill(headline, width=25)
        current_y = content_y
        
        for line in wrapped_headline.split('\n'):
            if current_y > 800:  # Prevent overflow
                break
            draw.text((padding, current_y), line, 
                     fill=self.text_color, font=title_font)
            current_y += 85
        
        # Add separator line
        current_y += 30
        draw.line([(padding, current_y), (self.width - padding, current_y)],
                 fill=self.accent_color, width=4)
        current_y += 50
        
        # Wrap and draw summary
        wrapped_summary = textwrap.fill(summary, width=35)
        
        for line in wrapped_summary.split('\n'):
            if current_y > 880:  # Prevent overflow
                break
            draw.text((padding, current_y), line,
                     fill=self.text_color, font=summary_font)
            current_y += 60
        
        # Footer with source and website
        footer_y = 980
        draw.text((padding, footer_y), f"Source: {source}",
                 fill=self.text_color, font=meta_font)
        
        website_text = "DentalDailyBrief.com"
        website_bbox = draw.textbbox((0, 0), website_text, font=meta_font)
        website_width = website_bbox[2] - website_bbox[0]
        draw.text((self.width - padding - website_width, footer_y), website_text,
                 fill=self.accent_color, font=meta_font)
        
        return img
    
    def generate_image(self, story, output_dir="instagram_images"):
        """Generate and save image for a single story"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create safe filename from headline
        safe_title = "".join(c for c in story['title'][:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        img = self.create_story_image(
            headline=story['title'],
            summary=story['summary'][:200],  # Limit summary length
            source=story['source']
        )
        
        filename = f"{safe_title}_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        
        print(f"✓ Created image: {filename}")
        return filepath
