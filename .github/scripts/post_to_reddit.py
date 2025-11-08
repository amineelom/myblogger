import os
import re
import subprocess
import time
from datetime import datetime

import praw
import yaml


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            print(f"Error parsing frontmatter: {e}")
            return None
    return None

def get_changed_posts():
    """Get list of changed post files from git."""
    try:
        # Get changed files in _posts directory
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD', '_posts/'],
            capture_output=True,
            text=True
        )
        changed_files = result.stdout.strip().split('\n')
        return [f for f in changed_files if f.endswith('.md') and f.startswith('_posts/')]
    except Exception as e:
        print(f"Error getting changed files: {e}")
        return []

def create_reddit_title(post_title):
    """Create a Reddit-friendly title (max 300 chars)."""
    if len(post_title) > 290:
        return post_title[:287] + "..."
    return post_title

def create_reddit_body(description, url, excerpt):
    """Create the Reddit post body."""
    body = f"{description}\n\n"
    body += f"**Read the full article:** {url}\n\n"
    if excerpt:
        body += f"*{excerpt}*\n\n"
    body += "---\n\n"
    body += "*I'm sharing quality tech content. Let me know what you think!*"
    return body

def post_to_reddit(post_path):
    """Post article to Reddit."""
    
    # Read the post file
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {post_path}: {e}")
        return False

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        print(f"Could not extract frontmatter from {post_path}")
        return False

    # Get post details
    title = frontmatter.get('title', '')
    description = frontmatter.get('description', '')
    excerpt = frontmatter.get('excerpt', '')
    permalink = frontmatter.get('permalink', '')
    
    # Generate URL
    site_url = os.environ.get('SITE_URL', 'https://markereviews.com')
    
    if permalink:
        post_url = f"{site_url}{permalink}"
    else:
        # Extract date and slug from filename
        filename = os.path.basename(post_path)
        match = re.match(r'(\d{4}-\d{2}-\d{2})-(.*?)\.md', filename)
        if match:
            date_str, slug = match.groups()
            categories = frontmatter.get('categories', [])
            if categories:
                # Convert categories to URL-friendly format
                category_path = '/'.join([cat.lower().replace(' ', '-') for cat in categories])
                post_url = f"{site_url}/{category_path}/{slug}/"
            else:
                post_url = f"{site_url}/{slug}/"
        else:
            print(f"Could not generate URL for {post_path}")
            return False

    # Create Reddit post
    reddit_title = create_reddit_title(title)
    reddit_body = create_reddit_body(description or excerpt, post_url, excerpt if description else None)

    # Initialize Reddit
    try:
        reddit = praw.Reddit(
            client_id=os.environ['REDDIT_CLIENT_ID'],
            client_secret=os.environ['REDDIT_CLIENT_SECRET'],
            username=os.environ['REDDIT_USERNAME'],
            password=os.environ['REDDIT_PASSWORD'],
            user_agent='MarkeReviews Blog Poster v1.0'
        )
        subreddits_env = os.environ.get('REDDIT_SUBREDDITS', '')
        subreddit_list = [s.strip() for s in subreddits_env.split(',') if s.strip()]

        if not subreddit_list:
            print("❌ No subreddits specified. Please set REDDIT_SUBREDDITS in your GitHub secrets.")
            return False

        for sub_name in subreddit_list:
            try:
                print(f"🚀 Posting to r/{sub_name} ...")
                subreddit = reddit.subreddit(sub_name)
                submission = subreddit.submit(
                    title=reddit_title,
                    selftext=reddit_body
                )
                print(f"✅ Posted to r/{sub_name}: {submission.url}")
            
                # Wait 60 seconds between posts to avoid rate limits
                time.sleep(60)

            except Exception as e:
                print(f"❌ Error posting to r/{sub_name}: {e}")

        return True

    except Exception as e:
        print(f"❌ Error posting to Reddit: {e}")
        return False

def main():
    """Main function."""
    
    # Check if manual post file specified
    manual_post = os.environ.get('POST_FILE', '')
    
    if manual_post:
        post_path = f"_posts/{manual_post}"
        if os.path.exists(post_path):
            print(f"Posting manually specified file: {post_path}")
            post_to_reddit(post_path)
        else:
            print(f"❌ File not found: {post_path}")
    else:
        # Get changed posts from git
        changed_posts = get_changed_posts()
        
        if not changed_posts:
            print("No new or changed posts found")
            return
        
        print(f"Found {len(changed_posts)} changed post(s)")
        
        # Post each changed article
        for post_path in changed_posts:
            print(f"\nProcessing: {post_path}")
            post_to_reddit(post_path)

if __name__ == "__main__":
    main()