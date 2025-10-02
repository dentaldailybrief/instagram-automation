"""
Instagram Auto-Poster with Cloudinary for Dental Daily Brief
Posts single images to Instagram using Cloudinary for hosting
"""

import requests
import json
from datetime import datetime
import time
import cloudinary
import cloudinary.uploader
import os

class InstagramPoster:
    def __init__(self, access_token, instagram_account_id, cloudinary_config):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloudinary_config['cloud_name'],
            api_key=cloudinary_config['api_key'],
            api_secret=cloudinary_config['api_secret']
        )
        
    def upload_to_cloudinary(self, image_path):
        """Upload image to Cloudinary and get public URL"""
        try:
            upload_result = cloudinary.uploader.upload(
                image_path,
                folder="dental_daily_brief"
            )
            image_url = upload_result['secure_url']
            print(f"✓ Uploaded to Cloudinary: {image_url}")
            return image_url
        except Exception as e:
            print(f"✗ Cloudinary upload failed: {str(e)}")
            return None
    
    def create_media_container(self, image_url, caption):
        """Create Instagram media container"""
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        
        params = {
            'access_token': self.access_token,
            'image_url': image_url,
            'caption': caption
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            container_id = response.json()['id']
            print(f"✓ Created media container")
            return container_id
        else:
            print(f"✗ Container creation failed: {response.text}")
            return None
    
    def publish_post(self, container_id):
        """Publish the Instagram post"""
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
    
    def post_single_image(self, image_path, story):
        """Complete workflow to post single image"""
        print(f"\n🚀 Posting story: {story['title'][:50]}...")
        
        # Upload to Cloudinary
        image_url = self.upload_to_cloudinary(image_path)
        if not image_url:
            return None
        
        # Generate caption
        caption = self.generate_caption(story)
        
        # Create container
        time.sleep(2)  # Rate limiting
        container_id = self.create_media_container(image_url, caption)
        if not container_id:
            return None
        
        # Publish
        time.sleep(3)  # Wait for processing
        post_id = self.publish_post(container_id)
        
        return post_id
    
    def generate_caption(self, story):
        """Generate Instagram caption for a story"""
        caption = f"""📰 {story['title']}

{story['summary'][:150]}...

🔗 Read more at DentalDailyBrief.com

Source: {story['source']}

#DentalNews #Dentistry #DentalProfessional #DentalIndustry #Dentist #OralHealth #DentalCare #HealthcareNews
"""
        return caption


def post_story_to_instagram(story, image_path):
    """Post a single story to Instagram"""
    
    # Load credentials from environment
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID')
    
    cloudinary_config = {
        'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.environ.get('CLOUDINARY_API_KEY'),
        'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
    }
    
    if not all([access_token, account_id, cloudinary_config['cloud_name']]):
        print("⚠️ Missing credentials!")
        return None
    
    poster = InstagramPoster(access_token, account_id, cloudinary_config)
    post_id = poster.post_single_image(image_path, story)
    
    return post_id


# Example usage
if __name__ == "__main__":
    sample_story = {
        "title": "Economic Confidence Hits New Low Among U.S. Dentists",
        "summary": "The Q2 2025 report reveals declining confidence among dentists.",
        "source": "ADA News",
        "url": "https://example.com/story"
    }
    
    post_id = post_story_to_instagram(sample_story, "test_image.png")
