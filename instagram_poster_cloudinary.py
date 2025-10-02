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
        caption = self.generate_caption(st
