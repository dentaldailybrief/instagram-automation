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
            data = json.load(f)
            posted_urls = []
            for item in data:
                if isinstance(item, str):
                    posted_urls.append(item)
                elif isinstance(item, dict) and 'url' in item:
                    posted_urls.append(item['url'])
            return posted_urls
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Warning: Error reading posted_stories.json: {e}")
        return []

def save_posted_stories(posted_urls):
    """Save the updated list of posted story URLs (as strings only)."""
    with open('posted_stories.json', 'w') as f:
        json.dump(posted_urls, f, indent=2)

def fetch_stories():
    """Fetch stories from the DentalDailyBrief API."""
    url = "https://dentaldailybrief.com/api/stories"
    headers = {
        'User-Agent': 'python-requests'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Debug: Show what we received
        print(f"API Response type: {type(data)}")
        
        # Handle different response formats
        stories = []
        
        if isinstance(data, list):
            # It's already a list of stories
            stories = data
        elif isinstance(data, dict):
            # It's an object, look for common keys
            if 'stories' in data:
                stories = data['stories']
                print(f"Found 'stories' key in response")
            elif 'data' in data:
                stories = data['data']
                print(f"Found 'data' key in response")
            elif 'items' in data:
                stories = data['items']
                print(f"Found 'items' key in response")
            else:
                # Try to extract any list from the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"Found list under key '{key}'")
                        stories = value
                        break
                
                if not stories:
                    # If no list found, maybe the dict itself is a single story
                    if 'url' in data and 'title' in data:
                        stories = [data]
                        print("Response appears to be a single story")
                    else:
                        print(f"Unknown API response structure. Keys: {list(data.keys())}")
                        print(f"Full response: {json.dumps(data, indent=2)[:500]}...")  # First 500 chars
        
        # Validate stories
        valid_stories = []
        for story in stories:
            if isinstance(story, dict) and 'url' in story:
                valid_stories.append(story)
            else:
                print(f"Warning: Invalid story format: {story}")
        
        return valid_stories
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stories: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from API: {e}")
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
        print("No valid stories fetched from API")
        print("Please check the API endpoint or response format")
        return
    
    print(f"✓ Fetched {len(stories)} valid stories from API")
    
    # Show first story as example
    if stories:
        print(f"Example story: {json.dumps(stories[0], indent=2)[:300]}...")
    
    # Load already posted story URLs
    posted_urls = load_posted_stories()
    print(f"✓ Loaded {len(posted_urls)} previously posted story URLs")
    
    # Filter out already posted stories
    new_stories = []
    for story in stories:
        if story.get('url') and story['url'] not in posted_urls:
            new_stories.append(story)
    
    if not new_stories:
        print("\nNo new stories to post")
        print("All current stories have already been posted.")
        # Show what we have vs what's posted
        print(f"Current story URLs from API:")
        for s in stories[:3]:
            print(f"  - {s.get('url', 'No URL')}")
        if posted_urls:
            print(f"Already posted URLs:")
            for url in posted_urls[:3]:
                print(f"  - {url}")
        return
    
    print(f"✓ Found {len(new_stories)} new stories to post")
    print("=" * 50)
    
    # Track successes and failures
    successful_posts = 0
    failed_posts = 0
    
    # Process each new story (limit to 3 per run to avoid rate limits)
    stories_to_post = new_stories[:3]
    print(f"Will post {len(stories_to_post)} stories (max 3 per run)")
    
    for i, story in enumerate(stories_to_post):
        print(f"\n📝 Processing story {i+1}/{len(stories_to_post)}:")
        print(f"   Title: {story.get('title', 'Untitled')[:60]}...")
        print(f"   URL: {story.get('url', 'No URL')}")
        print(f"   Age: {story.get('age', 'unknown')}")
        print(f"   Source: {story.get('source', 'Unknown')}")
        
        try:
            # Generate image for the story
            print("\n   🎨 Generating image...")
            image_path = f"instagram_post_{i}.png"
            generate_instagram_image(story, image_path)
            
            # Check if image was created
            if not os.path.exists(image_path):
                print(f"   ❌ ERROR: Image file not created at {image_path}")
                failed_posts += 1
                continue
            
            file_size = os.path.getsize(image_path) / 1024  # Size in KB
            print(f"   ✓ Image created: {image_path} ({file_size:.1f} KB)")
            
            # Prepare caption
            title = story.get('title', '')
            summary = story.get('summary', '')
            source = story.get('source', 'DentalDailyBrief.com')
            
            # Truncate if too long
            if len(title) > 200:
                title = title[:197] + "..."
            if len(summary) > 500:
                summary = summary[:497] + "..."
            
            caption = f"{title}\n\n{summary}\n\nSource: {source}\n\n#DentalNews #Dentistry #DentalDaily #Healthcare #DentalProfessionals #DentalEducation #OralHealth"
            
            # Post to Instagram
            print("\n   📤 Posting to Instagram...")
            print(f"   Caption length: {len(caption)} characters")
            
            success = post_to_instagram(
                image_path=image_path,
                caption=caption
            )
            
            if success:
                print(f"   ✅ SUCCESS: Posted to Instagram!")
                successful_posts += 1
                # Add URL to posted stories
                posted_urls.append(story['url'])
                save_posted_stories(posted_urls)
                print(f"   ✓ Updated tracking file")
            else:
                print(f"   ❌ FAILED: Could not post to Instagram")
                print(f"   Check Instagram token and Cloudinary settings")
                failed_posts += 1
            
            # Clean up the generated image
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"   ✓ Cleaned up temporary image file")
            
            # Wait between posts to avoid rate limiting
            if i < len(stories_to_post) - 1:
                print("\n   ⏳ Waiting 30 seconds before next post...")
                time.sleep(30)
                
        except Exception as e:
            print(f"\n   ❌ ERROR processing story: {str(e)}")
            print(f"   Full error trace:")
            traceback.print_exc()
            failed_posts += 1
            
            # Clean up on error
            try:
                if 'image_path' in locals() and os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass
            continue
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 AUTOMATION COMPLETE:")
    print(f"   ✅ Successful posts: {successful_posts}")
    print(f"   ❌ Failed posts: {failed_posts}")
    print(f"   📝 Total stories processed: {len(stories_to_post)}")
    print("=" * 50)
    
    if failed_posts > 0 and successful_posts == 0:
        print(f"\n⚠️  All posts failed. Check logs for details.")
        exit(1)
    elif successful_posts > 0:
        print(f"\n✨ Successfully posted {successful_posts} stories!")

if __name__ == "__main__":
    main()
