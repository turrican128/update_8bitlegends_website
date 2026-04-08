#!/usr/bin/env python3
"""Claude API integration for generating memorial post content.

Supports one-shot generation from multiple source URLs (CSDB, Pouet,
C64GFX.com, Facebook, Instagram, or any webpage).
"""

import os
import re
import requests
from urllib.parse import urlparse
from anthropic import Anthropic
from dotenv import load_dotenv
from post_styles import POST_STYLES, get_template_html

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are writing memorial posts for 8bitlegends.com, a demoscene memorial site \
honoring Commodore 64 and retro computing legends who have passed away.

Write in a heartfelt but not overly sentimental tone. Use demoscene vocabulary naturally \
(scener, handle, crew/group, demo, intro, crack, SID music, pixel art, etc.).

IMPORTANT: Output as HTML with inline styles. Use the EXACT dark cinematic style from the \
Rebecca Heineman memorial page — dark radial gradients, glassmorphic borders, card grids.

## Structure (in order)

1. WRAPPER: <section> with style="{wrapper}"
2. MEMORIAL HEADER: <header> with style="{memorial_header}"
   - <h1> with style="{person_name}"> — "In Memory of [Full Name]"
   - <p> with style="{person_handle}"> — "[Year] – [Year] · [Handle] / [Group] · [Role]"
3. BIOGRAPHY: 3-6 paragraphs in an <article> wrapper
   - <p> with style="{paragraph}"
   - First sentence of first paragraph wraps in <strong style="{paragraph_strong}">
   - Game/demo titles use <em style="{paragraph_em}"> (soft pink, NOT italic)
4. QUOTE: a tribute or community quote
   - <div> with style="{blockquote}"
   - Include <span style="{blockquote_mark}">&ldquo;</span> watermark
5. KEY MILESTONES: <section> with style="{milestones_section}"
   - <h2> with style="{section_heading}"> — "Key Milestones"
   - <ul> with style="{milestones_list}">, each <li> has <strong style="{milestones_bold}">[Year]:</strong>
6. WORKS GRID: responsive card grid
   - Grid container: <div> with style="{works_grid}"
   - Each card: <div> with style="{works_card}">
     - Title: <div> with style="{works_card_title}"
     - Subtitle: <div> with style="{works_card_subtitle}"> — "[Year] · [Type]"
     - Body: <p> with style="{works_card_body}"
   - If image URLs are available, add screenshot images INSIDE cards:
     <div style="{image_container}"><img src="URL" style="{image}" alt="..."></div>
7. CLOSING TRIBUTE: <footer> with style="{closing_tribute}"
   - <div> with style="{closing_tribute_text}"> — poetic closing line
   - <div> with style="{closing_tribute_stars}"> — "★ [handle] · forever in our memories ★"
8. LINKS: <div> with style="{links_section}"
   - <p> with style="{links_heading}"> — "Links"
   - Source URLs as <a> with style="{link}"
9. CLOSE the wrapper </section>
10. RIP SECTION (OUTSIDE the main wrapper, as a separate div):
   - <div> with style="{rip_section}"
   - <h2> with style="{rip_heading}"><em>Rest in Peace<br>[Full Name]</em></h2>
   - <img src="https://amigac64.wordpress.com/wp-content/uploads/2015/04/flower6.png" style="width:85px;margin-top:1rem;opacity:0.9" alt="Flower tribute">
   - <p> with style="{rip_subtitle}"> — "[Year] – [Year] · Forever in Our Memories"

## Images
When image URLs are provided, embed 1-3 in works cards or biography. Use:
<div style="{image_container}"><img src="URL" style="{image}" alt="..."></div>
Add <p style="{image_caption}">Caption</p> below. Max 3 images.

## Important
- Do NOT invent dates, events, or quotes you're not sure about. Use [brackets] for unknowns.
- Use the person's REAL FIRST NAME in the RIP section. Fall back to handle if unknown.
- The RIP section uses a FLOWER IMAGE, not emoji.
""".format(**POST_STYLES)

HTTP_HEADERS = {"User-Agent": "8bitLegends/2.0 (memorial site research)"}


# ── Source Scrapers ───────────────────────────────────────────


def _strip_html(html):
    """Strip HTML tags and collapse whitespace."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def scrape_csdb(url):
    """Scrape a CSDB scener profile page."""
    try:
        resp = requests.get(url, timeout=10, headers=HTTP_HEADERS)
        resp.raise_for_status()
        html = resp.text
        info = {"source": "CSDB", "url": url}

        # Title format: "[CSDb] - Handle/Group1/Group2"
        title_match = re.search(r'<title>\[CSDb\]\s*-\s*(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            import html as html_mod
            parts = html_mod.unescape(title_match.group(1)).split('/')
            if parts:
                info["handle"] = parts[0].strip()
            if len(parts) > 1:
                info["groups"] = [p.strip() for p in parts[1:]]

        # Real name from page content
        name_match = re.search(r'Real\s*[Nn]ame\s*:?\s*</b>\s*(?:<br>)?\s*(?:<font[^>]*>)?(.*?)(?:</font>)?<', html, re.DOTALL)
        if name_match:
            name = re.sub(r'<[^>]+>', '', name_match.group(1)).strip()
            if name:
                info["real_name"] = name

        # Country
        country_match = re.search(r'Country\s*:?\s*</b>.*?<a[^>]*>(.*?)</a>', html, re.DOTALL)
        if country_match:
            info["country"] = re.sub(r'<[^>]+>', '', country_match.group(1)).strip()

        # Extract release screenshots — CSDB stores them at /gfx/releases/{floor}/{id}.png
        release_ids = re.findall(r'href="/release/\?id=(\d+)"', html)
        unique_ids = list(dict.fromkeys(release_ids))  # dedupe preserving order
        images = []
        for rid in unique_ids[:8]:
            folder = str((int(rid) // 1000) * 1000)
            images.append(f"https://csdb.dk/gfx/releases/{folder}/{rid}.png")
        if images:
            info["image_urls"] = images
            info["image_url"] = images[0]

        info["page_text"] = _strip_html(html)[:4000]
        return info
    except Exception as e:
        return {"source": "CSDB", "url": url, "error": str(e)}


def scrape_pouet(url):
    """Scrape a Pouet user or production page."""
    try:
        resp = requests.get(url, timeout=10, headers=HTTP_HEADERS)
        resp.raise_for_status()
        html = resp.text
        info = {"source": "Pouet", "url": url}

        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        if title_match:
            info["page_title"] = title_match.group(1).strip()

        info["page_text"] = _strip_html(html)[:4000]
        return info
    except Exception as e:
        return {"source": "Pouet", "url": url, "error": str(e)}


def scrape_c64gfx(url):
    """Scrape a C64GFX.com artist page (logos, PETSCII, pixel art)."""
    try:
        resp = requests.get(url, timeout=10, headers=HTTP_HEADERS)
        resp.raise_for_status()
        html = resp.text
        info = {"source": "C64GFX.com", "url": url}

        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        if title_match:
            info["page_title"] = title_match.group(1).strip()

        # Extract artwork images
        images = []
        skip_patterns = ['icon', 'logo', 'nav', 'spacer', 'banner', 'button']
        for img_match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html):
            img_url = img_match.group(1)
            if img_url.startswith('/'):
                img_url = 'https://www.c64gfx.com' + img_url
            elif not img_url.startswith('http'):
                continue
            if any(skip in img_url.lower() for skip in skip_patterns):
                continue
            if img_url not in images:
                images.append(img_url)
        if images:
            info["image_urls"] = images[:10]
            info["image_url"] = images[0]
            info["works_count"] = len(images)

        info["page_text"] = _strip_html(html)[:4000]
        return info
    except Exception as e:
        return {"source": "C64GFX.com", "url": url, "error": str(e)}


def scrape_generic(url):
    """Generic scraper for any webpage (Facebook, Instagram, news, etc.)."""
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        source_name = domain.split(".")[0].capitalize()

        resp = requests.get(url, timeout=10, headers=HTTP_HEADERS)
        resp.raise_for_status()
        html = resp.text
        info = {"source": source_name, "url": url}

        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        if title_match:
            info["page_title"] = title_match.group(1).strip()

        # Extract Open Graph meta for social media pages
        og_desc = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if og_desc:
            info["description"] = og_desc.group(1).strip()

        og_image = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if og_image:
            info["image_url"] = og_image.group(1).strip()

        info["page_text"] = _strip_html(html)[:3000]
        return info
    except Exception as e:
        domain = urlparse(url).netloc if url.startswith("http") else url
        return {"source": domain, "url": url, "error": str(e)}


def detect_and_scrape(source):
    """Detect source type from URL and scrape accordingly."""
    if not source.startswith("http"):
        # Not a URL — treat as a handle/name
        return {"source": "handle", "handle": source}

    domain = urlparse(source).netloc.lower()

    if "csdb.dk" in domain:
        return scrape_csdb(source)
    elif "pouet.net" in domain:
        return scrape_pouet(source)
    elif "c64gfx.com" in domain:
        return scrape_c64gfx(source)
    else:
        return scrape_generic(source)


# ── Post Generation ───────────────────────────────────────────


def create_post_from_sources(sources):
    """One-shot: scrape multiple URLs, combine data, generate memorial post.

    Args:
        sources: List of URLs or handle strings.

    Returns:
        dict with keys: content (HTML), title, tags, profile_info
    """
    # Scrape all sources
    all_data = []
    for source in sources:
        data = detect_and_scrape(source.strip())
        all_data.append(data)

    # Build combined profile info
    profile_summary = _build_profile_summary(all_data)

    # Build the prompt
    template_html = get_template_html()
    sources_text = _format_all_sources(all_data)

    prompt = f"""Create a complete memorial post for this person from the demoscene/retro computing community.

Information gathered from {len(all_data)} source(s):

{sources_text}

Here is the HTML template structure to follow (fill in real content, keep the EXACT inline styles):
{template_html}

Generate the COMPLETE memorial post as HTML with inline styles. Follow the dark cinematic design exactly.
Use ALL the information from the sources above to create a rich, detailed post.
If some details are unknown, write something respectful and general instead of leaving brackets.

The post must include:
- Dark gradient wrapper <section>
- "In Memory of [Name]" header
- Biography paragraphs (bold first sentence, pink emphasis for demo/game titles)
- A meaningful quote in a gradient blockquote
- Key milestones as a bulleted list in a dark card
- Notable works as responsive cards in a grid
- Closing tribute with monospace stars line
- Links section
- RIP section (OUTSIDE the main wrapper) with flower image and "Rest in Peace [Name]"

If image URLs are provided in the sources, embed the most relevant ones (1-3 max) as screenshots
inside the works cards using the image_container and image styles.

Output ONLY the HTML content (the complete <section> wrapper + RIP div). No markdown, no explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    content = message.content[0].text
    title = _extract_title(content, all_data)
    tags = _build_tags(all_data)

    # Generate handle logo and prepend to content
    handle = ""
    for d in all_data:
        if d.get("handle"):
            handle = d["handle"]
            break
    if handle:
        try:
            from logo_generator import generate_handle_logo
            logo = generate_handle_logo(handle)
            if logo:
                logo_html = (
                    f'<div style="text-align:center;margin:0 0 1.5rem;padding:0">'
                    f'<img src="{logo["data_uri"]}" alt="{handle}" '
                    f'style="display:inline-block;max-width:100%;height:auto;'
                    f'image-rendering:pixelated;border-radius:8px;'
                    f'box-shadow:0 4px 16px rgba(0,0,0,0.6)">'
                    f'</div>'
                )
                # Insert logo at the very start (before or inside the first <section>)
                if content.strip().startswith("<section"):
                    # Insert after the opening <section> tag
                    content = re.sub(
                        r'(<section[^>]*>)',
                        r'\1\n' + logo_html,
                        content, count=1
                    )
                else:
                    content = logo_html + "\n" + content
        except Exception:
            pass  # Logo is optional — don't fail the whole post

    # Extract real name for RIP section
    real_name = ""
    for d in all_data:
        if d.get("real_name"):
            real_name = d["real_name"]
            break

    return {
        "content": content,
        "title": title,
        "tags": tags,
        "real_name": real_name,
        "profile_info": profile_summary,
    }


def restyle_post(current_html, supplementary_sources=None, real_name="", title=""):
    """Restyle a fetched WordPress post to match the 8bit Legends dark cinematic theme.

    Preserves all existing text, images, and links while restructuring into
    the styled template sections with proper inline CSS.
    """
    extra_info = ""
    if supplementary_sources:
        all_data = []
        for source in supplementary_sources:
            data = detect_and_scrape(source.strip())
            all_data.append(data)
        extra_info += f"\n\nAdditional information from supplementary sources:\n{_format_all_sources(all_data)}"

    # Real name for RIP section — always include this block so Claude never skips it
    rip_name = real_name if real_name else "extract the person's first/real name from the content"

    template_html = get_template_html()

    prompt = f"""Restyle this existing memorial post to match the 8bit Legends dark cinematic theme.

EXISTING POST CONTENT (preserve ALL information, images, links, and text):

{current_html}
{extra_info}

Post title: {title}
Person's real name for RIP section: {rip_name}

TARGET TEMPLATE (use these EXACT inline styles and section structure):
{template_html}

INSTRUCTIONS:
- Restructure the content into the proper sections: header, biography, quote, milestones, works grid, closing, links, RIP
- Apply ALL inline styles from the template exactly
- PRESERVE every piece of text, every image URL, every link from the original
- If the original has images, place them appropriately (header area or works cards)
- Extract dates, handle, group info from the original to fill the header
- Create milestones from chronological facts in the original
- Create works cards from any demos/releases/games mentioned
- If information for a non-essential section (quote, milestones, works) isn't available, you may omit it
- The RIP section is MANDATORY — NEVER omit it. It goes OUTSIDE the main <section> wrapper as a separate <div>
- The RIP section MUST include "Rest in Peace {rip_name}" with the flower image
- Use the flower image URL: https://amigac64.wordpress.com/wp-content/uploads/2015/04/flower6.png

Output ONLY the complete HTML (the <section> wrapper + RIP div). No markdown, no explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    content = message.content[0].text
    title = _extract_title(content, [])

    return {
        "content": content,
        "title": title if title else "",
    }


def _build_profile_summary(all_data):
    """Build a short summary of what was found across all sources."""
    parts = []
    handle = ""
    for d in all_data:
        if d.get("handle"):
            handle = d["handle"]
        if d.get("real_name"):
            parts.append(d["real_name"])
        if d.get("groups"):
            parts.append("/".join(d["groups"]))
        source_name = d.get("source", "")
        if source_name and source_name != "handle":
            parts.append(source_name)

    if handle:
        parts.insert(0, handle)
    return " — ".join(dict.fromkeys(parts))  # dedupe while preserving order


def _format_all_sources(all_data):
    """Format all scraped source data into text for Claude."""
    sections = []
    for i, data in enumerate(all_data, 1):
        lines = [f"--- Source {i}: {data.get('source', 'Unknown')} ---"]
        if data.get("url"):
            lines.append(f"URL: {data['url']}")
        if data.get("handle"):
            lines.append(f"Handle: {data['handle']}")
        if data.get("real_name"):
            lines.append(f"Real name: {data['real_name']}")
        if data.get("groups"):
            lines.append(f"Groups: {', '.join(data['groups'])}")
        if data.get("country"):
            lines.append(f"Country: {data['country']}")
        if data.get("page_title"):
            lines.append(f"Page title: {data['page_title']}")
        if data.get("description"):
            lines.append(f"Description: {data['description']}")
        if data.get("works_count"):
            lines.append(f"Works/images found: {data['works_count']}")
        if data.get("image_urls"):
            lines.append(f"Available images ({len(data['image_urls'])} found):")
            for idx, img in enumerate(data["image_urls"], 1):
                lines.append(f"  Image {idx}: {img}")
        elif data.get("image_url"):
            lines.append(f"Profile image: {data['image_url']}")
        if data.get("error"):
            lines.append(f"(Scraping error: {data['error']})")
        if data.get("page_text"):
            lines.append(f"\nPage content:\n{data['page_text']}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _extract_title(content, all_data):
    """Extract a post title from profile data."""
    handle = ""
    groups = []
    real_name = ""
    for d in all_data:
        if d.get("handle") and not handle:
            handle = d["handle"]
        if d.get("groups") and not groups:
            groups = d["groups"]
        if d.get("real_name") and not real_name:
            real_name = d["real_name"]

    if handle and groups:
        return f"{handle}/{groups[0]} has left us"
    elif handle and real_name:
        return f"{real_name} ({handle}) has passed away"
    elif handle:
        return f"{handle} has left us"
    else:
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        if h1_match:
            return re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        return "Memorial Post"


def _build_tags(all_data):
    """Build tags from scraped data."""
    tags = ["c64", "commodore", "Commodore 64", "demoscene", "retro", "retrogaming"]
    for d in all_data:
        if d.get("groups"):
            for g in d["groups"][:3]:
                if g not in tags:
                    tags.append(g)
        if d.get("handle") and d["handle"] not in tags:
            tags.append(d["handle"])
    return tags


# ── Legacy/Utility Functions ──────────────────────────────────


# Keep backward compat alias
def create_post_from_source(source):
    """Single-source wrapper for backward compatibility."""
    return create_post_from_sources([source])


def generate_memorial_content(name, handle, group, role="coder",
                               contributions="", extra_context=""):
    """Generate memorial content from manual fields."""
    from post_generator import generate_post
    template_draft = generate_post(name, handle, group, role,
                                    contributions or "amazing demos and intros")

    prompt = f"""Write a memorial post for:
- Real name: {name}
- Scene handle: {handle}
- Group/crew: {group}
- Role: {role}
- Known for: {contributions or 'their contributions to the scene'}
{f'- Additional context: {extra_context}' if extra_context else ''}

Generate the post as HTML with inline styles following the 8bit Legends dark cinematic format.
Include: dark gradient wrapper, biography, quote, milestones, works cards, closing tribute, links.
End with a separate RIP section using the flower image and "Rest in Peace {name or handle}".
Output ONLY the HTML content."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "content": message.content[0].text,
        "title": template_draft["title"],
        "tags": template_draft["tags"],
    }


def enhance_text(text, instruction="Make this more detailed and heartfelt"):
    """Enhance a selected portion of text."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{instruction}:\n\n{text}\n\nOutput ONLY the enhanced HTML. No explanation."}]
    )
    return message.content[0].text


def chat_modify_post(current_html, instruction):
    """Modify the post HTML according to user's free-form instruction.

    Returns dict with 'content' (modified HTML) and 'summary' (short description).
    """
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT + "\n\nYou are modifying an existing memorial post. "
            "Apply the user's instruction to the HTML content. "
            "Return ONLY the modified HTML. Keep all inline styles intact. "
            "Do not add markdown, explanations, or code fences.",
        messages=[{"role": "user", "content":
            f"Current post HTML:\n\n{current_html}\n\n"
            f"Instruction: {instruction}\n\n"
            "Apply this instruction and return the complete modified HTML. "
            "Keep all inline styles. Output ONLY HTML, no explanation."}]
    )
    return {
        "content": message.content[0].text,
        "summary": f"Applied: {instruction}",
    }
