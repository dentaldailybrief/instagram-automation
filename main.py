import json
import requests
import time
import os
import traceback
from instagram_image_generator import generate_instagram_image
from instagram_poster_cloudinary import post_to_instagram

def load_posted_stories():
    """Load the list of already posted story URLs."""
    try:
        with open('posted_stories.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_posted_stories(posted_stories):
    """Save the updated list of posted story URLs."""
    with open('posted_stories.json', 'w') as f:
        json.dump(posted_stories, f, indent=2)

def fetch_stories():
    """Fetch stories from the DentalDailyBrief API."""
    url = "https://dentaldailybrief.com/api/stories"
    headers = {
        'User-Agent': 'python-requests'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stories: {e}")
        return []

def main():
    """Main function to run the Instagram automation."""
    print("Starting Instagram automation...")
    print("=" * 50)
    
    # Check environment variables
    print("\nChecking environment variables...")
    has_token = bool(os.environ.get('INSTAGRAM_ACCESS_TOKEN'))
    has_account = bool(os.environ.get('INSTAGRAM_ACCOUNT_ID'))
    has_cloud_name = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))
    has_cloud_key = bool(os.environ.get('CLOUDINARY_API_KEY'))
    has_cloud_secret = bool(os.environ.get('CLOUDINARY_API_SECRET'))
    
    print(f"INSTAGRAM_ACCESS_TOKEN: {'✓ Set' if has_token else '✗ Missing'}")
    print(f"INSTAGRAM_ACCOUNT_ID: {'✓ Set' if has_account else '✗ Missing'}")
    print(f"CLOUDINARY_CLOUD_NAME: {'✓ Set' if has_cloud_name else '✗ Missing'}")
    print(f"CLOUDINARY_API_KEY: {'✓ Set' if has_cloud_key else '✗ Missing'}")
    print(f"CLOUDINARY_API_SECRET: {'✓ Set' if has_cloud_secret else '✗ Missing'}")
    
    if not all([has_token, has_account, has_cloud_name, has_cloud_key, has_cloud_secret]):
        print("\n❌ ERROR: Missing required environment variables!")
        return
    
    # Fetch stories from API
    print("\nFetching stories from API...")
    stories = fetch_stories()
    if not stories:
        print("No stories fetched from API")
        return
    
    print(f"✓ Fetched {len(stories)} stories from API")
    
    # Load already posted stories
    posted_stories = load_posted_stories()
    print(f"✓ Already posted {len(posted_stories)} stories in the past")
    
    # Filter out already posted stories
    new_stories = [
        story for story in stories 
        if story.get('url') and story['url'] not in posted_stories
    ]
    
    if not new_stories:
        print("\nNo new stories to post")
        return
    
    print(f"✓ Found {len(new_stories)} new stories to post")
    print("=" * 50)
    
    # Track successes and failures
    successful_posts = 0
    failed_posts = 0
    
    # Process each new story
    for i, story in enumerate(new_stories):
        print(f"\n📝 Processing story {i+1}/{len(new_stories)}:")
        print(f"   Title: {story.get('title', 'Untitled')[:60]}...")
        print(f"   URL: {story.get('url', 'No URL')}")
        print(f"   Age: {story.get('age', 'unknown')}")
        
        try:
            # Generate image for the story
            print("\n   🎨 Generating image...")
            image_path = generate_instagram_image(story, f"instagram_post_{i}.png")
            
            # Check if image was created
            if not os.path.exists(image_path):
                print(f"   ❌ ERROR: Image file not created at {image_path}")
                failed_posts += 1
                continue
            
            file_size = os.path.getsize(image_path) / 1024  # Size in KB
            print(f"   ✓ Image created: {image_path} ({file_size:.1f} KB)")
            
            # Post to Instagram
            print("\n   📤 Posting to Instagram...")
            success = post_to_instagram(
                image_path=image_path,
                caption=f"{story.get('title', '')}\n\n{story.get('summary', '')}\n\nSource: {story.get('source', 'DentalDailyBrief.com')}\n\n#DentalNews #Dentistry #DentalDaily #Healthcare #DentalProfessionals"
            )
            
            if success:
                print(f"   ✅ SUCCESS: Posted to Instagram!")
                successful_posts += 1
                # Add to posted stories
                posted_stories.append(story['url'])
                save_posted_stories(posted_stories)
                print(f"   ✓ Updated tracking file")
            else:
                print(f"   ❌ FAILED: Could not post to Instagram")
                failed_posts += 1
            
            # Clean up the generated image
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"   ✓ Cleaned up temporary image file")
            
            # Wait between posts to avoid rate limiting
            if i < len(new_stories) - 1:  # Don't wait after the last post
                print("\n   ⏳ Waiting 30 seconds before next post...")
                time.sleep(30)
                
        except Exception as e:
            print(f"\n   ❌ ERROR processing story: {str(e)}")
            print(f"   Full error trace:")
            traceback.print_exc()
            failed_posts += 1
            continue
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 AUTOMATION COMPLETE:")
    print(f"   ✅ Successful posts: {successful_posts}")
    print(f"   ❌ Failed posts: {failed_posts}")
    print(f"   📝 Total stories processed: {len(new_stories)}")
    print("=" * 50)
    
    # Exit with error code if any posts failed
    if failed_posts > 0:
        print(f"\n⚠️  Some posts failed. Check the logs above for details.")
        exit(1)
    else:
        print(f"\n✨ All posts completed successfully!")

if __name__ == "__main__":
    main()
