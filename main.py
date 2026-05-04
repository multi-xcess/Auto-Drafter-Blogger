import os
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# =========================
# CONFIG (from GitHub Secrets)
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BLOG_ID = os.getenv("BLOG_ID")

# Optional: OAuth token file (from Google login)
TOKEN_FILE = "token.json"


# =========================
# 1. READ TOPICS
# =========================
def get_topics():
    with open("topics.txt", "r", encoding="utf-8") as f:
        topics = f.read().splitlines()
    return [t.strip() for t in topics if t.strip()]


# =========================
# 2. GEMINI ARTICLE GENERATION
# =========================
def generate_article(topic):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
Write a SEO-friendly blog article on this topic:

Topic: {topic}

Requirements:
- 5 paragraphs
- simple English
- SEO optimized
- engaging and human-like tone
"""
            }]
        }]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    try:
        article = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        article = "Error generating article."

    return article


# =========================
# 3. FORMAT CONTENT
# =========================
def format_content(article, topic):
    return f"""
<h1>{topic}</h1>

{article}

<br><br>
<i>Note: This article is auto-generated using AI.</i>
"""


# =========================
# 4. BLOGGER POST (DRAFT)
# =========================
def get_credentials():
    return Credentials.from_authorized_user_file(TOKEN_FILE)


def post_to_blogger(title, content, creds):
    service = build("blogger", "v3", credentials=creds)

    post = {
        "title": title,
        "content": content,
        "isDraft": True   # IMPORTANT: draft mode
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post
    ).execute()


# =========================
# 5. MAIN FLOW
# =========================
def main():
    print("Reading topics...")
    topics = get_topics()

    if not topics:
        print("No topics found!")
        return

    creds = get_credentials()

    for topic in topics:
        print(f"\nProcessing topic: {topic}")

        # Step 1: Generate article
        article = generate_article(topic)

        # Step 2: Format
        content = format_content(article, topic)

        # Step 3: Post to Blogger as draft
        post_to_blogger(topic, content, creds)

        print(f"Draft created for: {topic}")

    print("\nAll topics processed successfully.")


# =========================
# RUN SCRIPT
# =========================
if __name__ == "__main__":
    main()
