#!/usr/bin/env python3
"""Generate new 8bit Legends posts based on patterns from existing posts."""

import os
import re
import random
import json
from datetime import datetime
from typing import List, Dict

# Common tags used in posts
COMMON_TAGS = [
    "c64", "commodore", "Commodore 64", "demoscene", "retro",
    "retrogaming", "vintage", "8bit", "amiga", "atari",
    "retro-gaming", "C64 demo scene", "games", "history"
]

# Common groups/crews mentioned
COMMON_GROUPS = [
    "Genesis Project", "Noice", "F4CG", "TRSI", "Atlantis",
    "Fairlight", "Censor Design", "Oxyron", "Bonzai", "Horizon",
    "Alpha Flight", "Byterapers", "Ikari", "Paradox", "Razor 1911"
]

# Post templates based on existing patterns
POST_TEMPLATES = {
    "memorial": {
        "opening": [
            "We are saddened to share the news that {name}, known in the scene as {handle} of {group}, has passed away.",
            "Another 8-bit legend has gone. {name}, also known as {handle}/{group}, has left us.",
            "It is with heavy hearts that we announce the passing of {name}, better known as {handle} from {group}.",
            "The retro community mourns the loss of {name} ({handle}/{group}) who has left us too soon."
        ],
        "contribution": [
            "{pronoun} was known for {contributions} that pushed the boundaries of what was possible on 8-bit machines.",
            "As a {role}, {handle} created {contributions} that will be remembered forever.",
            "{handle}'s work in {contributions} helped define the golden age of the demoscene.",
            "Their contributions to {contributions} inspired countless others in the scene."
        ],
        "personal": [
            "Those who knew {pronoun_lower} remember a passionate and dedicated member of the community.",
            "{pronoun} was not just a talented {role}, but also a friend to many in the scene.",
            "Beyond the technical achievements, {handle} will be remembered for {pronoun_lower} kindness and willingness to help others.",
            "The demoscene has lost not just a skilled {role}, but a true friend and mentor."
        ],
        "closing": [
            "Rest in peace, {handle}. Your legacy lives on in every pixel and every note.",
            "May {pronoun_lower} memory live on through {pronoun_lower} work and the scene {pronoun_lower} helped build.",
            "Thank you for everything, {handle}. The scene will never forget you.",
            "Rest in peace, {name}. Your contributions to the 8-bit world will never be forgotten."
        ]
    },
    "tribute": {
        "opening": [
            "Today we remember {name} ({handle}/{group}), a true legend of the 8-bit era.",
            "Let's take a moment to celebrate the life and work of {handle} from {group}.",
            "In tribute to {name}, known as {handle}, whose work continues to inspire."
        ],
        "legacy": [
            "{pronoun_lower} productions remain some of the most celebrated works in demoscene history.",
            "The impact of {handle}'s work can still be felt in modern productions.",
            "{handle}'s innovative techniques influenced an entire generation of sceners."
        ]
    }
}

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
            if val.startswith("["):
                try:
                    val = json.loads(val)
                except json.JSONDecodeError:
                    pass
            elif val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            meta[key] = val

    body = text[match.end():]
    return meta, body

def analyze_existing_posts(posts_dir="posts", sample_size=10):
    """Analyze existing posts to understand patterns."""
    analysis = {
        "common_phrases": [],
        "title_patterns": [],
        "content_patterns": [],
        "tags_frequency": {}
    }

    files = sorted([f for f in os.listdir(posts_dir) if f.endswith(".md")], reverse=True)

    # Only analyze the most recent posts for efficiency
    files_to_analyze = files[:sample_size]

    for filename in files_to_analyze:
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        meta, body = parse_frontmatter(text)

        # Analyze title patterns
        title = meta.get("title", "")
        if "has left us" in title.lower() or "has passed away" in title.lower():
            analysis["title_patterns"].append(title)

        # Analyze tags
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            analysis["tags_frequency"][tag] = analysis["tags_frequency"].get(tag, 0) + 1

    # Sort tags by frequency
    analysis["top_tags"] = sorted(
        analysis["tags_frequency"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:15]

    return analysis

def generate_post(
    name: str,
    handle: str,
    group: str,
    role: str = "coder",
    contributions: str = "amazing demos and intros",
    template_type: str = "memorial",
    custom_tags: List[str] = None
) -> Dict:
    """Generate a new post based on templates and patterns."""

    # Determine pronouns
    pronoun = "They"
    pronoun_lower = "their"

    # Select template
    template = POST_TEMPLATES.get(template_type, POST_TEMPLATES["memorial"])

    # Generate content sections
    opening = random.choice(template["opening"]).format(
        name=name, handle=handle, group=group,
        pronoun=pronoun, pronoun_lower=pronoun_lower
    )

    contribution = ""
    if "contribution" in template:
        contribution = random.choice(template["contribution"]).format(
            name=name, handle=handle, group=group, role=role,
            contributions=contributions, pronoun=pronoun, pronoun_lower=pronoun_lower
        )

    personal = ""
    if "personal" in template:
        personal = random.choice(template["personal"]).format(
            name=name, handle=handle, group=group, role=role,
            pronoun=pronoun, pronoun_lower=pronoun_lower
        )

    closing = random.choice(template["closing"]).format(
        name=name, handle=handle, group=group,
        pronoun=pronoun, pronoun_lower=pronoun_lower
    )

    # Build content
    content_parts = [opening]
    if contribution:
        content_parts.append(contribution)
    if personal:
        content_parts.append(personal)
    content_parts.append(closing)

    content = "\n\n".join(content_parts)

    # Add links section
    links = f"\n\n<!-- Links -->\n"
    links += f"<!-- [CSDB Profile](https://csdb.dk/scener/?id=XXXX) -->\n"
    links += f"<!-- [Pouet Profile](https://www.pouet.net/user.php?who=XXXX) -->"

    # Select tags
    if custom_tags:
        tags = custom_tags
    else:
        tags = random.sample(COMMON_TAGS, min(8, len(COMMON_TAGS)))
        # Always include some core tags
        if "c64" not in tags:
            tags.append("c64")
        if "demoscene" not in tags:
            tags.append("demoscene")

    # Generate title
    title_patterns = [
        f"{handle}/{group} has left us",
        f"{name} ({handle}) has passed away",
        f"Rest in Peace - {handle} of {group}",
        f"{handle}/{group} - Gone but not forgotten",
        f"Farewell to {handle} from {group}"
    ]
    title = random.choice(title_patterns)

    return {
        "title": title,
        "content": content + links,
        "tags": tags,
        "metadata": {
            "name": name,
            "handle": handle,
            "group": group,
            "role": role
        }
    }

def create_post_file(post_data: Dict, output_dir: str = "posts"):
    """Create a markdown file from generated post data."""

    # Generate filename
    date = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", post_data["title"].lower()).strip("-")
    filename = f"{date}-{slug}.md"
    filepath = os.path.join(output_dir, filename)

    # Build frontmatter
    frontmatter = f"""---
title: "{post_data['title']}"
status: draft
tags: {json.dumps(post_data['tags'])}
featured_image:
---"""

    # Combine frontmatter and content
    full_content = frontmatter + "\n\n" + post_data["content"]

    # Write file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath

def suggest_post_from_history():
    """Suggest a new post based on analyzing existing posts."""
    analysis = analyze_existing_posts(sample_size=10)

    print("\n=== Post Pattern Analysis (Last 10 posts) ===")
    print(f"Found {len(analysis['title_patterns'])} memorial posts in recent posts")
    print(f"\nMost common tags from sample:")
    for tag, count in analysis["top_tags"][:10]:
        print(f"  - {tag}: {count} uses")

    print("\n=== Suggested Post Elements ===")
    print(f"Group: {random.choice(COMMON_GROUPS)}")
    print(f"Role: {random.choice(['coder', 'musician', 'graphician', 'swapper', 'organizer'])}")
    print(f"Tags: {', '.join(random.sample([t[0] for t in analysis['top_tags'][:10]], 6))}")

    return analysis

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("""
8bit Legends Post Generator

Usage:
  python post_generator.py analyze              Analyze existing posts for patterns
  python post_generator.py generate              Interactive post generation
  python post_generator.py quick <name> <handle> <group>  Quick generation with defaults

Example:
  python post_generator.py quick "John Smith" "Wizard" "Elite"
""")
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        suggest_post_from_history()

    elif command == "generate":
        print("\n=== Interactive Post Generator ===")
        name = input("Enter real name: ")
        handle = input("Enter handle/nickname: ")
        group = input("Enter group/crew: ")
        role = input("Enter role (coder/musician/graphician/etc): ")
        contributions = input("Enter main contributions: ")

        post = generate_post(name, handle, group, role, contributions)
        filepath = create_post_file(post)

        print(f"\nPost created: {filepath}")
        print(f"Title: {post['title']}")
        print(f"Tags: {', '.join(post['tags'])}")

    elif command == "quick" and len(sys.argv) >= 5:
        name = sys.argv[2]
        handle = sys.argv[3]
        group = sys.argv[4]

        post = generate_post(name, handle, group)
        filepath = create_post_file(post)

        print(f"Post created: {filepath}")
        print(f"Title: {post['title']}")