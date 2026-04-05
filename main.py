#!/usr/bin/env python3
"""8bit Legends WordPress CLI - manage posts locally and publish to 8bitlegends.com"""

import sys
import os
import re
import json
from datetime import datetime

import markdown
from wp_client import WordPressClient

POSTS_DIR = os.path.join(os.path.dirname(__file__), "posts")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.md")


def ensure_posts_dir():
    os.makedirs(POSTS_DIR, exist_ok=True)


def parse_frontmatter(text):
    """Parse YAML-like frontmatter from a markdown file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text

    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # Parse JSON arrays
            if val.startswith("["):
                try:
                    val = json.loads(val)
                except json.JSONDecodeError:
                    pass
            # Strip quotes
            elif val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            meta[key] = val

    body = text[match.end():]
    return meta, body


# ── Commands ─────────────────────────────────────────────────────


def cmd_fetch():
    """Download all posts from 8bitlegends.com to posts/ directory."""
    ensure_posts_dir()
    client = WordPressClient()

    print("Fetching posts from 8bitlegends.com...")
    posts = client.get_all_posts()
    print(f"Found {len(posts)} posts.")

    for post in posts:
        date = post.get("date", "")[:10]
        slug = post.get("slug", "untitled")
        filename = f"{date}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)

        md_content = client.post_to_markdown(post)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        title = post.get("title", slug)
        print(f"  Saved: {filename} - {title}")

    print(f"\nDone! {len(posts)} posts saved to posts/")


def cmd_list():
    """List all local post files."""
    ensure_posts_dir()

    files = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith(".md"))
    if not files:
        print("No local posts found. Run 'python main.py fetch' to download existing posts.")
        return

    print(f"Local posts ({len(files)}):\n")
    for f in files:
        filepath = os.path.join(POSTS_DIR, f)
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()
        meta, _ = parse_frontmatter(text)
        title = meta.get("title", f)
        status = meta.get("status", "fetched")
        print(f"  [{status:>8}] {f}")
        print(f"            {title}")


def cmd_new(title):
    """Create a new draft post from the template."""
    ensure_posts_dir()

    # Generate filename
    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    filename = f"{date}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    if os.path.exists(filepath):
        print(f"Error: {filename} already exists.")
        return

    # Copy template and fill in title
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace(
        'title: "Name/Handle (Group) has left us..."',
        f'title: "{title}"',
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"Created new draft: {filename}")
    print(f"Edit it at: {filepath}")


def cmd_publish(filepath, live=False):
    """Publish a local markdown post to WordPress."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    meta, body = parse_frontmatter(text)

    title = meta.get("title", "Untitled")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    status = "publish" if live else "draft"
    featured_image_path = meta.get("featured_image", "")

    # Convert markdown body to HTML
    # Strip HTML comments first
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    content_html = markdown.markdown(body, extensions=["extra"])

    client = WordPressClient()

    # Upload featured image if provided
    featured_image_id = None
    if featured_image_path and os.path.isfile(featured_image_path):
        print(f"Uploading featured image: {featured_image_path}")
        result = client.upload_image(featured_image_path)
        featured_image_id = result.get("id")
        print(f"  Uploaded as media ID: {featured_image_id}")

    print(f"Publishing '{title}' as {status}...")
    post_id = client.create_post(
        title=title,
        content_html=content_html,
        tags=tags,
        status=status,
        featured_image_id=featured_image_id,
    )

    print(f"Success! Post created with ID: {post_id}")
    if status == "draft":
        print(f"  Review it in your WordPress admin before publishing.")
    else:
        print(f"  Post is live!")
    print(f"  Admin: https://wordpress.com/post/{client.site}/{post_id}")


def cmd_help():
    print("""8bit Legends WordPress CLI

Usage:
  python main.py fetch                    Download all existing posts locally
  python main.py list                     List local posts
  python main.py new "Post Title"         Create a new draft from template
  python main.py publish <file.md>        Upload post as draft to WordPress
  python main.py publish --live <file.md> Upload and publish immediately
  python main.py help                     Show this help message
""")


# ── Main ─────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1]

    if command == "fetch":
        cmd_fetch()
    elif command == "list":
        cmd_list()
    elif command == "new":
        if len(sys.argv) < 3:
            print("Usage: python main.py new \"Post Title\"")
            return
        cmd_new(sys.argv[2])
    elif command == "publish":
        args = sys.argv[2:]
        live = "--live" in args
        args = [a for a in args if a != "--live"]
        if not args:
            print("Usage: python main.py publish [--live] <file.md>")
            return
        cmd_publish(args[0], live=live)
    elif command == "help":
        cmd_help()
    else:
        print(f"Unknown command: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
