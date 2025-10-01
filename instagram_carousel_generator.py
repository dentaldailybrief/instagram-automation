"""
Instagram Carousel Automation for Dental Daily Brief
Generates carousel posts from daily dental news stories
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from io import BytesIO
import os
from datetime import datetime

class InstagramCarouselGenerator:
    def __init__(self):
        # Instagram optimal dimensions
        self.width = 1080
        self.height = 1080
        
        # Brand colors (adjust to match your site)
        self.bg_color = '#FFFFFF'
        self.primary_color = '#2C5282'  # Dark blue
        self.accent_color = '#4299E1'   # Light blue
        self.text_color = '#1A202C'
        
    def create_cover_slide(self, date_str):
        """Create the first slide - cover/intro"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load custom fonts, fallback to default
        try:
            title_font = ImageFont.truetype("Arial.ttf", 80)
            subtitle_font = ImageFont.truetype("Arial.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add logo/branding area at top
        draw.rectangle([(0, 0), (self.width, 200)], fill=self.primary_color)
        
        # Add title
        title = "DENTAL DAILY BRIEF"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((self.width - title_width) / 2, 50), title, 
                 fill='white', font=title_font)
        
        # Add date
        date_text = f"Daily Update • {date_str}"
        date_bbox = draw.textbbox((0, 0), date_text, font=subtitle_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((self.width - date_width) / 2, 500), date_text,
                 fill=self.text_color, font=subtitle_font)
        
        # Add swipe indicator
        swipe_text = "Swipe for today's stories →"
        swipe_bbox = draw.textbbox((0, 0), swipe_text, font=subtitle_font)
        swipe_width = swipe_bbox[2] - swipe_bbox[0]
        draw.text(((self.width - swipe_width) / 2, 900), swipe_text,
                 fill=self.accent_color, font=subtitle_font)
        
        return img
    
    def create_story_slide(self, story_number, headline, summary, total_stories):
        """Create a slide for each news story"""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            headline_font = ImageFont.truetype("Arial-Bold.ttf", 60)
            summary_font = ImageFont.truetype("Arial.ttf", 40)
            meta_font = ImageFont.truetype("Arial.ttf", 30)
        except:
            headline_font = ImageFont.load_default()
            summary_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
        
        # Header bar with story number
        draw.rectangle([(0, 0), (self.width, 150)], fill=self.primary_color)
        story_num_text = f"Story {story_number} of {total_stories}"
        draw.text((40, 50), story_num_text, fill='white', font=meta_font)
        
        # Progress dots
        dot_spacing = 30
        dot_start = self.width - (total_stories * dot_spacing + 40)
        for i in range(total_stories):
            x = dot_start + (i * dot_spacing)
            color = self.accent_color if i == story_number - 1 else '#E2E8F0'
            draw.ellipse([(x, 60), (x + 15, 75)], fill=color)
        
        # Content area with padding
        padding = 60
        content_y = 200
        max_width = self.width - (padding * 2)
        
        # Wrap and draw headline
        wrapped_headline = textwrap.fill(headline, width=30)
        current_y = content_y
        
        for line in wrapped_headline.split('\n'):
            draw.text((padding, current_y), line, 
                     fill=self.text_color, font=headline_font)
            current_y += 80
        
        # Add separator line
        current_y += 20
        draw.line([(padding, current_y), (self.width - padding, current_y)],
                 fill=self.accent_color, width=3)
        current_y += 40
        
        # Wrap and draw summary
        wrapped_summary = textwrap.fill(summary, width=40)
        
        for line in wrapped_summary.split('\n'):
            if current_y > 900:  # Prevent overflow
                break
            draw.text((padding, current_y), line,
                     fill=self.text_color, font=summary_font)
            current_y += 55
        
        # Footer
        draw.text((padding, 1000), "DentalDailyBrief.com",
                 fill=self.accent_color, font=meta_font)
        
        return img
    
    def create_closing_slide(self):
        """Create final CTA slide"""
        img = Image.new('RGB', (self.width, self.height), self.primary_color)
        draw = ImageDraw.Draw(img)
        
        try:
            cta_font = ImageFont.truetype("Arial-Bold.ttf", 70)
            sub_font = ImageFont.truetype("Arial.ttf", 45)
        except:
            cta_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
        
        # Main CTA
        cta_text = "Visit DentalDailyBrief.com"
        cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cta_width = cta_bbox[2] - cta_bbox[0]
        draw.text(((self.width - cta_width) / 2, 400), cta_text,
                 fill='white', font=cta_font)
        
        # Sub text
        sub_text = "For full articles and more dental news"
        sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_width = sub_bbox[2] - sub_bbox[0]
        draw.text(((self.width - sub_width) / 2, 520), sub_text,
                 fill=self.accent_color, font=sub_font)
        
        return img
    
    def generate_carousel(self, stories, output_dir="instagram_posts"):
        """Generate complete carousel from stories data"""
        os.makedirs(output_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%B %d, %Y")
        timestamp = datetime.now().strftime("%Y%m%d")
        
        images = []
        
        # 1. Cover slide
        cover = self.create_cover_slide(date_str)
        cover_path = f"{output_dir}/slide_0_cover_{timestamp}.png"
        cover.save(cover_path)
        images.append(cover_path)
        print(f"✓ Created cover slide")
        
        # 2. Story slides
        for idx, story in enumerate(stories, 1):
            slide = self.create_story_slide(
                story_number=idx,
                headline=story['headline'],
                summary=story['summary'],
                total_stories=len(stories)
            )
            slide_path = f"{output_dir}/slide_{idx}_story_{timestamp}.png"
            slide.save(slide_path)
            images.append(slide_path)
            print(f"✓ Created story slide {idx}/{len(stories)}")
        
        # 3. Closing CTA slide
        closing = self.create_closing_slide()
        closing_path = f"{output_dir}/slide_{len(stories)+1}_cta_{timestamp}.png"
        closing.save(closing_path)
        images.append(closing_path)
        print(f"✓ Created closing slide")
        
        return images


# Example usage with your dental news data
if __name__ == "__main__":
    # Sample stories (replace with your actual data from WordPress)
    sample_stories = [
        {
            "headline": "Economic Confidence Hits New Low Among U.S. Dentists in Q2 2025",
            "summary": "The Q2 2025 report reveals a decline in economic confidence among dentists for the second consecutive quarter. Key concerns include tariffs and inflation."
        },
        {
            "headline": "New AI Technology Transforms Dental Diagnostics",
            "summary": "Revolutionary AI system shows 95% accuracy in detecting early-stage cavities, potentially changing preventive care standards."
        },
        {
            "headline": "Study Links Oral Health to Cardiovascular Disease Prevention",
            "summary": "Major research study demonstrates strong correlation between regular dental care and reduced heart disease risk in adults over 40."
        }
    ]
    
    generator = InstagramCarouselGenerator()
    image_paths = generator.generate_carousel(sample_stories)
    
    print(f"\n✅ Generated {len(image_paths)} slides successfully!")
    print(f"Images saved in: instagram_posts/")
