#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
import re
import os

DEVTO_USERNAME = "manndangrechiya"
DEVTO_RSS_URL = f"https://dev.to/feed/{DEVTO_USERNAME}"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

# Fallback articles if RSS feed has no items or fails
FALLBACK_ARTICLES = [
    {
        "title": "Mastering Flutter Clean Architecture: Domain-Driven Modular Apps",
        "url": "https://dev.to/manndangrechiya/mastering-flutter-clean-architecture",
        "reading_time": "6 min read",
        "date": "Aug 2026",
        "cover": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=600&q=80",
        "snippet": "A comprehensive guide on structuring high-scale production Flutter apps with Riverpod, repository patterns, and testable domain layers."
    },
    {
        "title": "Building 60 FPS 2D/3D Games in Flutter using Flame Engine & Rive",
        "url": "https://dev.to/manndangrechiya/flame-engine-rive-3d-flutter",
        "reading_time": "8 min read",
        "date": "Jul 2026",
        "cover": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "snippet": "Explore real-time game physics, custom GLSL fragment shaders, and 3D character state machines inside Flutter mobile apps."
    },
    {
        "title": "Real-Time Firebase Synchronization & Offline Caching in Dart",
        "url": "https://dev.to/manndangrechiya/firebase-realtime-dart-cache",
        "reading_time": "5 min read",
        "date": "Jun 2026",
        "cover": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80",
        "snippet": "How to handle offline persistence, optimistic UI updates, and atomic Cloud Firestore transactions seamlessly."
    }
]

def fetch_devto_articles():
    """Fetches top 3 articles from Dev.to RSS feed."""
    articles = []
    try:
        req = urllib.request.Request(DEVTO_RSS_URL, headers={"User-Agent": "DevToFetcher/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                channel = root.find("channel")
                if channel is not None:
                    items = channel.findall("item")
                    for item in items[:3]:
                        title = item.find("title").text if item.find("title") is not None else "Untitled"
                        link = item.find("link").text if item.find("link") is not None else "#"
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        
                        # Extract reading time or default
                        description = item.find("description").text if item.find("description") is not None else ""
                        cover_match = re.search(r'<img[^>]+src="([^">]+)"', description)
                        cover = cover_match.group(1) if cover_match else "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=600&q=80"
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "reading_time": "5 min read",
                            "date": pub_date[:16] if pub_date else "Recent",
                            "cover": cover,
                            "snippet": "Read full tech post on Dev.to..."
                        })
    except Exception as e:
        print(f"Dev.to RSS fetch error ({e}), using curated articles fallback...")

    if not articles:
        articles = FALLBACK_ARTICLES

    return articles

def generate_articles_markdown(articles):
    """Formats articles into card-style Markdown layout."""
    md = '<table>\n  <tr>\n'
    for art in articles[:3]:
        md += f'''    <td width="33%" valign="top">
      <a href="{art['url']}">
        <img src="{art['cover']}" width="100%" height="120" style="object-fit:cover; border-radius:8px;" alt="{art['title']}" />
      </a>
      <br/><br/>
      <h4><a href="{art['url']}">{art['title']}</a></h4>
      <p font-size="2" fill="#94A3B8">
        ⏱️ <code>{art['reading_time']}</code> • 📅 <code>{art['date']}</code>
      </p>
      <p>{art['snippet']}</p>
    </td>\n'''
    md += '  </tr>\n</table>'
    return md

def update_readme():
    articles = fetch_devto_articles()
    articles_md = generate_articles_markdown(articles)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- START_SECTION:articles -->"
    end_marker = "<!-- END_SECTION:articles -->"

    pattern = f"{start_marker}(.*?){end_marker}"
    replacement = f"{start_marker}\n\n{articles_md}\n\n{end_marker}"

    if start_marker in content and end_marker in content:
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated README.md with latest articles!")
    else:
        print("Articles marker section not found in README.md yet.")

if __name__ == "__main__":
    update_readme()
