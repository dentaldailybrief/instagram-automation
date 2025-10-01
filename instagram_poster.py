"""
Instagram Auto-Poster for Dental Daily Brief
Integrates with Instagram Graph API to post carousels
"""

import requests
import json
from datetime import datetime
import time

class InstagramPoster:
    def __init__(self, access_token, instagram_account_id):
        """
        Initialize with Instagram credentials
        
        Get these from: https://developers.facebook.com/
        1. Create Facebook App
        2. Add Instagram Graph API
        3. Get Page Access Token
        4. Get Instagram Business Account ID
        """
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def upload_image(self, image_path, is_carousel_item=True):
        """Upload image to Instagram and get media ID"""
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            
            params = {
                'access_token': self.access_token,
            }
            
            if is_carousel_item:
                params['is_carousel_item'] = 'true'
            
            response = requests.post(url, params=params, files=files)
            
        if response.status_code == 200:
            media_id = response.json()['id']
            print(f"✓ Uploaded image: {image_path}")
            return media_id
        else:
            print(f"✗ Upload failed: {response.text}")
            return None
    
    def create_carousel_container(self, media_ids, caption):
        """Create carousel post container"""
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        
        params = {
            'access_token': self.access_token,
            'media_type': 'CAROUSEL',
            'children': ','.join(media_ids),
            'caption': caption
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            container_id = response.json()['id']
            print(f"✓ Created carousel container")
            return container_id
        else:
            print(f"✗ Carousel creation failed: {response.text}")
            return None
    
    def publish_post(self, container_id):
        """Publish the carousel post"""
        url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
        
        params = {
            'access_token': self.access_token,
            'creation_id': container_id
        }
        
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            post_id = response.json()['id']
            print(f"✅ Post published successfully! ID: {post_id}")
            return post_id
        else:
            print(f"✗ Publishing failed: {response.text}")
            return None
    
    def post_carousel(self, image_paths, caption):
        """Complete workflow to post carousel"""
        print(f"\n🚀 Starting Instagram carousel post...")
        print(f"📸 Uploading {len(image_paths)} images...")
        
        # Upload all images
        media_ids = []
        for image_path in image_paths:
            media_id = self.upload_image(image_path)
            if media_id:
                media_ids.append(media_id)
                time.sleep(1)  # Rate limiting
            else:
                print(f"Failed to upload {image_path}, aborting...")
                return None
        
        # Create carousel
        print(f"\n📦 Creating carousel container...")
        container_id = self.create_carousel_container(media_ids, caption)
        if not container_id:
            return None
        
        # Publish
        print(f"\n📤 Publishing post...")
        time.sleep(2)  # Wait for processing
        post_id = self.publish_post(container_id)
        
        return post_id


def generate_caption(stories, date_str):
    """Generate engaging Instagram caption"""
    caption = f"""📰 Dental Daily Brief • {date_str}

Today's top dental industry stories:

"""
    
    for idx, story in enumerate(stories, 1):
        caption += f"{idx}. {story['headline']}\n"
    
    caption += f"""
📱 Swipe through for summaries →

🔗 Read full articles at DentalDailyBrief.com

#DentalNews #Dentistry #DentalProfessional #DentalIndustry #Dentist #DentalHealth #DentalBusiness #DentalCommunity #OralHealth
"""
    
    return caption


# Complete automation workflow
def automate_daily_post(stories):
    """
    Complete automation: Generate images + Post to Instagram
    
    Run this daily via cron job or GitHub Actions
    """
    from instagram_carousel_generator import InstagramCarouselGenerator
    
    # 1. Generate carousel images
    print("=" * 60)
    print("STEP 1: GENERATING CAROUSEL IMAGES")
    print("=" * 60)
    
    generator = InstagramCarouselGenerator()
    image_paths = generator.generate_carousel(stories)
    
    # 2. Create caption
    date_str = datetime.now().strftime("%B %d, %Y")
    caption = generate_caption(stories, date_str)
    
    # 3. Post to Instagram
    print("\n" + "=" * 60)
    print("STEP 2: POSTING TO INSTAGRAM")
    print("=" * 60)
    
    # Load credentials from environment variables (more secure)
    import os
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID')
    
    if not access_token or not account_id:
        print("\n⚠️  Instagram credentials not found!")
        print("Set environment variables:")
        print("  - INSTAGRAM_ACCESS_TOKEN")
        print("  - INSTAGRAM_ACCOUNT_ID")
        return None
    
    poster = InstagramPoster(access_token, account_id)
    post_id = poster.post_carousel(image_paths, caption)
    
    if post_id:
        print(f"\n" + "=" * 60)
        print("✅ AUTOMATION COMPLETE!")
        print("=" * 60)
        print(f"Post ID: {post_id}")
        print(f"View at: https://www.instagram.com/p/{post_id}/")
    
    return post_id


# Example usage
if __name__ == "__main__":
    # Sample stories (in production, fetch from your WordPress API)
    sample_stories = [
        {
            "headline": "Economic Confidence Hits New Low Among U.S. Dentists",
            "summary": "Q2 2025 report shows declining confidence for second quarter. Key concerns include tariffs and inflation."
        },
        {
            "headline": "AI Technology Transforms Dental Diagnostics",
            "summary": "New AI system achieves 95% accuracy in detecting early-stage cavities."
        }
    ]
    
    # Run the automation
    automate_daily_post(sample_stories)
