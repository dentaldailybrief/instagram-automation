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
            # Handle both formats: list of URLs or list of story objects
            posted_urls = []
            for item in data:
                if isinstance(item, str):
                    # It's already a URL string
                    posted_urls.append(item)
                elif isinstance(item, dict) and 'url' in item:
                    # It's a story object with a url field
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
        stories = response.json()
        
        # Ensure we have a list of story objects
        if not isinstance(stories, list):
            print(f"Warning: API returned non-list data: {type(stories)}")
            return []
            
        # Validate each story has required fields
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
        return
    
    print(f"✓ Fetched {len(stories)} valid stories from API")
    
    # Load already posted story URLs
    posted_urls = load_posted_stories()
    print(f"✓ Loaded {len(posted_urls)} previously posted story URLs")
    
    # Debug: Show what we have
    if posted_urls:
        print(f"   Last posted URL: {posted_urls[-1][:50]}...")
    
    # Filter out already posted stories
    new_stories = []
    for story in stories:
        if story.get('url') and story['url'] not in posted_urls:
            new_stories.append(story)
    
    if not new_stories:
        print("\nNo new stories to post")
        print("All current stories have already been posted.")
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
                # Add URL to posted stories (not the whole object)
                posted_urls.append(story['url'])
                save_posted_stories(posted_urls)
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
    print(f"   📝 Total stories processed: {len(new_stories)}")
    print("=" * 50)
    
    # Exit with error code if any posts failed
    if failed_posts > 0 and successful_posts == 0:
        print(f"\n⚠️  All posts failed. Check the logs above for details.")
        exit(1)
    elif failed_posts > 0:
        print(f"\n⚠️  Some posts failed, but {successful_posts} succeeded.")
    else:
        print(f"\n✨ All posts completed successfully!")

if __name__ == "__main__":
    main()
