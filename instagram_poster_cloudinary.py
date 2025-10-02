import os
import requests
import cloudinary
import cloudinary.uploader

def upload_to_cloudinary(image_path):
    """Upload image to Cloudinary and return the URL."""
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    
    try:
        # Upload image to Cloudinary
        response = cloudinary.uploader.upload(
            image_path,
            folder="instagram_posts",
            resource_type="image"
        )
        
        # Return the secure URL
        return response['secure_url']
    
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None

def create_instagram_media(image_url, caption, access_token, account_id):
    """Create a media object on Instagram."""
    
    url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    
    params = {
        'image_url': image_url,
        'caption': caption,
        'access_token': access_token
    }
    
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json().get('id')
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating Instagram media: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None

def publish_instagram_media(media_id, access_token, account_id):
    """Publish a media object on Instagram."""
    
    url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
    
    params = {
        'creation_id': media_id,
        'access_token': access_token
    }
    
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json().get('id')
    
    except requests.exceptions.RequestException as e:
        print(f"Error publishing Instagram media: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None

def post_to_instagram(image_path, caption):
    """Main function to post an image to Instagram via Cloudinary."""
    
    # Get environment variables
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID')
    
    if not access_token or not account_id:
        print("Error: Instagram credentials not found in environment variables")
        return False
    
    print("Uploading image to Cloudinary...")
    image_url = upload_to_cloudinary(image_path)
    
    if not image_url:
        print("Failed to upload image to Cloudinary")
        return False
    
    print(f"Image uploaded successfully: {image_url}")
    
    print("Creating Instagram media object...")
    media_id = create_instagram_media(image_url, caption, access_token, account_id)
    
    if not media_id:
        print("Failed to create Instagram media object")
        return False
    
    print(f"Media object created: {media_id}")
    
    print("Publishing to Instagram...")
    post_id = publish_instagram_media(media_id, access_token, account_id)
    
    if not post_id:
        print("Failed to publish to Instagram")
        return False
    
    print(f"Successfully posted to Instagram! Post ID: {post_id}")
    return True

# Test function (optional)
if __name__ == "__main__":
    # This is just for testing the module independently
    test_image = "test_image.png"
    test_caption = "Test post from automation script"
    
    if os.path.exists(test_image):
        success = post_to_instagram(test_image, test_caption)
        if success:
            print("Test post successful!")
        else:
            print("Test post failed!")
    else:
        print(f"Test image {test_image} not found")
