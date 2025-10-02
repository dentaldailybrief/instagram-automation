import json
import requests
import time
import os
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
    
    # Fetch stories from API
    stories = fetch_stories()
    if not stories:
        print("No stories fetched from API")
        return
    
    print(f"Fetched {len(stories)} stories from API")
    
    # Load already posted stories
    posted_stories = load_posted_stories()
    print(f"Already posted {len(posted_stories)} stories in the past")
    
    # Filter out already posted stories
    new_stories = [
        story for story in stories 
        if story.get('url') and story['url'] not in posted_stories
    ]
    
    if not new_stories:
        print("No new stories to post")
        return
    
    print(f"Found {len(new_stories)} new stories to post")
    
    # Process each new story
    for i, story in enumerate(new_stories):
        print(f"\nProcessing story {i+1}/{len(new_stories)}: {story.get('title', 'Untitled')}")
        
        try:
            # Generate image for the story
            print("Generating image...")
            image_path = generate_instagram_image(story, f"instagram_post_{i}.png")
            
            # Post to Instagram
            print("Posting to Instagram...")
            success = post_to_instagram(
                image_path=image_path,
                caption=f"{story.get('title', '')}\n\n{story.get('summary', '')}\n\nSource: {story.get('source', 'DentalDailyBrief.com')}\n\n#DentalNews #Dentistry #DentalDaily #Healthcare #DentalProfessionals"
            )
            
            if success:
                print(f"Successfully posted story: {story.get('title', 'Untitled')}")
                # Add to posted stories
                posted_stories.append(story['url'])
                save_posted_stories(posted_stories)
            else:
                print(f"Failed to post story: {story.get('title', 'Untitled')}")
            
            # Clean up the generated image
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Wait between posts to avoid rate limiting
            if i < len(new_stories) - 1:  # Don't wait after the last post
                print("Waiting 30 seconds before next post...")
                time.sleep(30)
                
        except Exception as e:
            print(f"Error processing story: {e}")
            continue
    
    print("\nInstagram automation completed!")

if __name__ == "__main__":
    main()
