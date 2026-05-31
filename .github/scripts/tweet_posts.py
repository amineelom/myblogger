import json
import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

import frontmatter
import tweepy

# Configuration
POSTS_DIR = '_posts'
POSTED_LINKS_FILE = '.github/data/posted_links.json'
MAX_TWEET_LENGTH = 280
SITE_URL = 'https://markereviews.com'

# Topic-specific call-to-actions
TOPIC_CTAS = {
    'ai': ["🤖 Dive into AI →", "🧠 Master AI →", "⚡ AI Insights →", "🚀 AI Revolution →"],
    'javascript': ["⚡ Code smarter →", "🚀 JS Mastery →", "💻 Level up your JS →", "🎯 JS Pro tips →"],
    'web-development': ["🌐 Build better web →", "🚀 Web Dev insights →", "💡 Web mastery →", "⚡ Dev productivity →"],
    'tech-careers': ["💼 Boost your career →", "🚀 Career growth →", "🎯 Land your dream job →", "💡 Career insights →"],
    'software-testing': ["🧪 Test like a pro →", "✅ Master testing →", "🔍 Debug smarter →", "⚡ Testing insights →"],
    'app-development': ["📱 Build amazing apps →", "🚀 App dev mastery →", "💡 Mobile insights →", "⚡ App productivity →"],
    'default': ["🚀 Read now →", "📚 Learn more →", "👀 Check this out →", "💡 Dive in →"]
}

# Smart hashtag mapping
HASHTAG_MAP = {
    'ai': ['#AI', '#ArtificialIntelligence'],
    'machine learning': ['#MachineLearning', '#ML'],
    'llm': ['#LLM', '#LargeLanguageModels'],
    'openai': ['#OpenAI', '#GPT'],
    'chatgpt': ['#ChatGPT'],
    'gpt': ['#GPT'],
    'claude': ['#Claude', '#Anthropic'],
    'javascript': ['#JavaScript', '#JS'],
    'typescript': ['#TypeScript', '#TS'],
    'react': ['#ReactJS', '#React'],
    'next.js': ['#NextJS', '#React'],
    'node.js': ['#NodeJS', '#JavaScript'],
    'python': ['#Python', '#Coding'],
    'web development': ['#WebDev', '#WebDevelopment'],
    'career': ['#TechCareers', '#Career'],
    'jobs': ['#TechJobs', '#Hiring'],
    'salary': ['#TechSalaries', '#CareerGrowth'],
    'skills': ['#Skills', '#DeveloperSkills'],
    'testing': ['#Testing', '#QA'],
    'api': ['#API', '#RESTAPI'],
    'tools': ['#DevTools', '#Productivity'],
    'github': ['#GitHub'],
    'docker': ['#Docker', '#DevOps'],
    'kubernetes': ['#Kubernetes', '#K8s'],
    'mobile': ['#MobileDev', '#AppDevelopment'],
    'ios': ['#iOS', '#Swift'],
    'android': ['#Android', '#Kotlin'],
    'flutter': ['#Flutter', '#Dart'],
    'programming': ['#Programming', '#Coding'],
    'development': ['#Development', '#Dev'],
    'tech': ['#Tech', '#Technology'],
    'tutorial': ['#Tutorial', '#HowTo'],
    'guide': ['#Guide', '#Tutorial']
}

def setup_twitter_client():
    """Initialize Twitter client"""
    return tweepy.Client(
        consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_SECRET'],
        access_token=os.environ['TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    )

def load_posted_links():
    """Load previously posted links"""
    try:
        with open(POSTED_LINKS_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_posted_links(links):
    """Save posted links to file"""
    os.makedirs(os.path.dirname(POSTED_LINKS_FILE), exist_ok=True)
    with open(POSTED_LINKS_FILE, 'w') as f:
        json.dump(list(links), f)

def parse_post_filename(filename):
    """Extract date and slug from post filename"""
    pattern = r'(\d{4}-\d{2}-\d{2})-(.+)\.md'
    match = re.match(pattern, filename)
    if match:
        date_str = match.group(1)
        slug = match.group(2)
        return datetime.strptime(date_str, '%Y-%m-%d'), slug
    return None, None

def read_post_metadata(filepath):
    """Read frontmatter from post file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            return post
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def extract_content_topics(title, excerpt, categories, tags):
    """Extract key topics from post content for smart targeting"""
    all_text = f"{title} {excerpt} {' '.join(categories)} {' '.join(tags)}".lower()
    
    detected_topics = []
    
    # Check for main categories first
    main_categories = ['ai', 'javascript', 'web-development', 'tech-careers', 'software-testing', 'app-development']
    for category in main_categories:
        if category in all_text or category.replace('-', ' ') in all_text:
            detected_topics.append(category)
    
    # Detect specific technologies and topics
    for topic, hashtags in HASHTAG_MAP.items():
        if topic in all_text:
            detected_topics.append(topic)
    
    # If no specific topics found, use categories
    if not detected_topics and categories:
        detected_topics.extend(categories)
    
    return list(set(detected_topics))

def get_relevant_hashtags(topics):
    """Get the most relevant hashtags based on detected topics"""
    hashtags = []
    
    for topic in topics:
        if topic in HASHTAG_MAP:
            hashtags.extend(HASHTAG_MAP[topic])
    
    # Remove duplicates and limit to 4 hashtags
    unique_hashtags = list(dict.fromkeys(hashtags))
    return unique_hashtags[:4]

def get_topic_cta(main_topic):
    """Get a relevant CTA based on the main topic"""
    if main_topic in TOPIC_CTAS:
        return random.choice(TOPIC_CTAS[main_topic])
    else:
        return random.choice(TOPIC_CTAS['default'])

def clean_excerpt(excerpt):
    """Clean and shorten excerpt for tweet"""
    if not excerpt:
        return ""
    
    # Remove markdown formatting
    clean_text = re.sub(r'[#*`\[\]]', '', excerpt)
    clean_text = re.sub(r'\n+', ' ', clean_text)
    
    # Shorten if too long
    if len(clean_text) > 120:
        clean_text = clean_text[:117] + "..."
    
    return clean_text.strip()

def generate_post_url(filepath, slug, post_date, categories):
    """Generate the post URL. Permalink is flat (/:title/), so the URL is just
    the filename slug (leading dashes stripped, matching how Jekyll builds it)."""
    return f"{SITE_URL}/{slug.lstrip('-')}/"
    
def create_smart_tweet(title, excerpt, link, categories, tags):
    """Create a highly targeted tweet based on post content"""
    
    # Extract topics from the post
    topics = extract_content_topics(title, excerpt, categories, tags)
    main_topic = topics[0] if topics else 'default'
    
    # Get targeted CTA and hashtags
    cta = get_topic_cta(main_topic)
    hashtags = get_relevant_hashtags(topics)
    
    # Clean and prepare content
    clean_title = title.strip()
    clean_excerpt_text = clean_excerpt(excerpt)
    
    # Build tweet components
    if clean_excerpt_text:
        base_tweet = f"{clean_title}\n\n{clean_excerpt_text}\n\n{cta}\n{link}"
    else:
        base_tweet = f"{clean_title}\n\n{cta}\n{link}"
    
    base_length = len(base_tweet)
    
    # Add hashtags if space permits
    hashtags_text = " ".join(hashtags)
    total_length = base_length + len(hashtags_text) + 1
    
    if total_length <= MAX_TWEET_LENGTH:
        return f"{base_tweet}\n\n{hashtags_text}"
    else:
        # Try with fewer hashtags
        for i in range(len(hashtags), 0, -1):
            reduced_hashtags = hashtags[:i]
            reduced_text = " ".join(reduced_hashtags)
            reduced_length = base_length + len(reduced_text) + 1
            
            if reduced_length <= MAX_TWEET_LENGTH:
                return f"{base_tweet}\n\n{reduced_text}"
        
        # If still too long, remove hashtags completely
        return base_tweet

def get_todays_posts():
    """Get today's posts that haven't been tweeted yet"""
    posted_links = load_posted_links()
    todays_posts = []
    
    today = datetime.now().date()
    
    # Scan _posts directory
    posts_path = Path(POSTS_DIR)
    if not posts_path.exists():
        print(f"❌ {POSTS_DIR} directory not found!")
        return []
    
    for post_file in posts_path.glob('*.md'):
        post_date, slug = parse_post_filename(post_file.name)
        
        if not post_date or not slug:
            continue
        
        # Only process today's posts
        if post_date.date() != today:
            continue
        
        # Read post metadata
        post_metadata = read_post_metadata(post_file)
        if not post_metadata:
            continue
        
        # Extract categories and tags from frontmatter FIRST
        categories = post_metadata.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        
        tags = post_metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        # Convert all to lowercase for consistency
        categories = [cat.lower() for cat in categories]
        tags = [tag.lower() for tag in tags]
        
        # Get excerpt or use description
        excerpt = post_metadata.get('excerpt') or post_metadata.get('description', '')
        
        # NOW generate the post URL (after categories is defined)
        post_url = generate_post_url(str(post_file), slug, post_date, categories)
        
        # Skip if already tweeted
        if post_url in posted_links:
            print(f"⏭️ Already tweeted: {post_file.name}")
            continue
        
        todays_posts.append({
            'title': post_metadata.get('title', ''),
            'excerpt': excerpt,
            'link': post_url,
            'categories': categories,
            'tags': tags,
            'published': post_date,
            'filename': post_file.name
        })
    
    return todays_posts

def main():
    """Main function to tweet today's posts"""
    client = setup_twitter_client()
    todays_posts = get_todays_posts()
    
    if not todays_posts:
        print("No new posts from today to tweet.")
        return
    
    print(f"🎉 Found {len(todays_posts)} new posts from today to tweet.")
    
    # Tweet today's posts
    for post in todays_posts:
        try:
            print(f"📝 Processing: {post['filename']}")
            print(f"   Title: {post['title']}")
            print(f"   Categories: {post['categories']}")
            print(f"   Tags: {post['tags']}")
            
            tweet_text = create_smart_tweet(
                post['title'],
                post['excerpt'],
                post['link'],
                post['categories'],
                post['tags']
            )
            
            print(f"   Tweet length: {len(tweet_text)}")
            print(f"   Tweet preview: {tweet_text[:100]}...")
            
            # Send tweet
            response = client.create_tweet(text=tweet_text)
            tweet_id = response.data['id']
            
            # Mark as posted
            posted_links = load_posted_links()
            posted_links.add(post['link'])
            save_posted_links(posted_links)
            
            print(f"✅ Successfully tweeted!")
            print(f"   Tweet ID: {tweet_id}")
            print(f"   URL: {post['link']}")
            print("---")
            
        except tweepy.TweepyException as e:
            print(f"❌ Failed to tweet '{post['title']}': {e}")
        except Exception as e:
            print(f"❌ Unexpected error with '{post['title']}': {e}")

if __name__ == "__main__":
    main()