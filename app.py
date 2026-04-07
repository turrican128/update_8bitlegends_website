#!/usr/bin/env python3
"""8bit Legends Web Editor v2.0 - Flask app with WYSIWYG TinyMCE editor."""

import os
import re
import json
import html as html_mod
import tempfile
from datetime import datetime

import markdown
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_from_directory, Response
)
from dotenv import load_dotenv

from wp_client import WordPressClient
from post_generator import generate_post, COMMON_TAGS, COMMON_GROUPS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "8bit-legends-dev-key")

POSTS_DIR = os.path.join(os.path.dirname(__file__), "posts")
TEMPLATE_HTML_PATH = os.path.join(os.path.dirname(__file__), "template.html")
TEMPLATE_MD_PATH = os.path.join(os.path.dirname(__file__), "template.md")


def ensure_posts_dir():
    os.makedirs(POSTS_DIR, exist_ok=True)


def parse_frontmatter(text):
    """Parse YAML-like frontmatter from a markdown or HTML file."""
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


def build_frontmatter(title, tags, status="draft", featured_image="", fmt="html", real_name="", wp_post_id=""):
    """Build YAML frontmatter string."""
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    lines = [
        "---",
        f'title: "{title}"',
        f"status: {status}",
        f"format: {fmt}",
        f"tags: {json.dumps(tags)}",
        f"featured_image: {featured_image}",
        f"real_name: {real_name}",
        f"wp_post_id: {wp_post_id}",
        "---",
    ]
    return "\n".join(lines)


def get_all_local_posts():
    """Read all posts from posts/ directory (both .md and .html files)."""
    ensure_posts_dir()
    posts = []
    files = sorted(
        (f for f in os.listdir(POSTS_DIR) if f.endswith((".md", ".html"))),
        reverse=True
    )
    for f in files:
        filepath = os.path.join(POSTS_DIR, f)
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()
        meta, body = parse_frontmatter(text)

        # For display, strip HTML tags from excerpt
        excerpt_text = re.sub(r"<[^>]+>", "", body).strip()
        excerpt = excerpt_text[:150] + "..." if len(excerpt_text) > 150 else excerpt_text

        posts.append({
            "filename": f,
            "title": meta.get("title", f),
            "status": meta.get("status", "fetched"),
            "tags": meta.get("tags", []),
            "format": meta.get("format", "markdown" if f.endswith(".md") else "html"),
            "date": f[:10] if len(f) >= 10 else "",
            "excerpt": excerpt,
        })
    return posts


def convert_md_to_html(md_body):
    """Convert markdown body to HTML (for legacy post migration)."""
    body_clean = re.sub(r"<!--.*?-->", "", md_body, flags=re.DOTALL)
    return markdown.markdown(body_clean, extensions=["extra"])


# ── Routes ─────────────────────────────────────────────────────


@app.route("/")
def index():
    """Dashboard - show drafts + 6 most recent posts."""
    all_posts = get_all_local_posts()
    # Show all drafts/new posts + up to 6 most recent fetched/published
    drafts = [p for p in all_posts if p["status"] == "draft"]
    others = [p for p in all_posts if p["status"] != "draft"][:6]
    posts = drafts + others
    return render_template("index.html", posts=posts)


@app.route("/new")
def new_post():
    """New post editor with HTML template."""
    # Try HTML template first, fall back to markdown template
    template_path = TEMPLATE_HTML_PATH if os.path.exists(TEMPLATE_HTML_PATH) else TEMPLATE_MD_PATH

    with open(template_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    meta, body = parse_frontmatter(template_text)

    # If it's a markdown template, convert to HTML
    fmt = meta.get("format", "markdown" if template_path.endswith(".md") else "html")
    if fmt == "markdown":
        body = convert_md_to_html(body)

    return render_template(
        "editor.html",
        filename=None,
        title=meta.get("title", ""),
        tags=", ".join(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else meta.get("tags", ""),
        featured_image=meta.get("featured_image", ""),
        real_name=meta.get("real_name", ""),
        wp_post_id=meta.get("wp_post_id", ""),
        body=body,
        format="html",
        common_tags=COMMON_TAGS,
        common_groups=COMMON_GROUPS,
        is_new=True,
        status="draft",
    )


@app.route("/edit/<filename>")
def edit_post(filename):
    """Edit an existing post."""
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        flash(f"File not found: {filename}", "error")
        return redirect(url_for("index"))

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    meta, body = parse_frontmatter(text)

    # Detect format and auto-convert markdown to HTML
    fmt = meta.get("format", "markdown" if filename.endswith(".md") else "html")
    if fmt == "markdown" or (not meta.get("format") and filename.endswith(".md")):
        body = convert_md_to_html(body)
        fmt = "html"

    tags = meta.get("tags", [])
    if isinstance(tags, list):
        tags = ", ".join(tags)

    return render_template(
        "editor.html",
        filename=filename,
        title=meta.get("title", ""),
        tags=tags,
        featured_image=meta.get("featured_image", ""),
        real_name=meta.get("real_name", ""),
        wp_post_id=meta.get("wp_post_id", ""),
        body=body,
        format=fmt,
        common_tags=COMMON_TAGS,
        common_groups=COMMON_GROUPS,
        is_new=False,
        status=meta.get("status", "draft"),
    )


@app.route("/save", methods=["POST"])
def save_post():
    """Save post to posts/ directory."""
    ensure_posts_dir()

    data = request.get_json() if request.is_json else request.form
    title = data.get("title", "Untitled")
    tags = data.get("tags", "")
    featured_image = data.get("featured_image", "")
    real_name = data.get("real_name", "")
    body = data.get("body", "")
    filename = data.get("filename", "")
    fmt = data.get("format", "html")

    # Preserve wp_post_id and status from existing file
    wp_post_id = ""
    existing_status = "draft"
    if filename:
        existing_path = os.path.join(POSTS_DIR, filename)
        if os.path.exists(existing_path):
            with open(existing_path, "r", encoding="utf-8") as f:
                existing_meta, _ = parse_frontmatter(f.read())
            wp_post_id = existing_meta.get("wp_post_id", "")
            existing_status = existing_meta.get("status", "draft")

    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    frontmatter = build_frontmatter(title, tags, existing_status, featured_image, fmt, real_name, wp_post_id)
    full_content = frontmatter + "\n\n" + body

    if not filename:
        date = datetime.now().strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        # Use .html extension for new posts
        filename = f"{date}-{slug}.html"

    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    if request.is_json:
        return jsonify({"ok": True, "filename": filename, "message": f"Saved: {filename}"})

    flash(f"Saved: {filename}", "success")
    return redirect(url_for("edit_post", filename=filename))


@app.route("/preview/<filename>")
def preview_post(filename):
    """Render post as HTML preview."""
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        flash(f"File not found: {filename}", "error")
        return redirect(url_for("index"))

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    meta, body = parse_frontmatter(text)

    # Detect format
    fmt = meta.get("format", "markdown" if filename.endswith(".md") else "html")
    if fmt == "markdown":
        body_clean = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
        content_html = markdown.markdown(body_clean, extensions=["extra"])
    else:
        content_html = body

    return render_template(
        "preview.html",
        title=meta.get("title", "Untitled"),
        tags=meta.get("tags", []),
        featured_image=meta.get("featured_image", ""),
        content_html=content_html,
        filename=filename,
    )


@app.route("/publish/<filename>", methods=["POST"])
def publish_post(filename):
    """Publish post to WordPress."""
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"ok": False, "error": f"File not found: {filename}"}), 404

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    meta, body = parse_frontmatter(text)

    title = meta.get("title", "Untitled")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    status = request.json.get("status", "draft") if request.is_json else request.form.get("status", "draft")
    featured_image_path = meta.get("featured_image", "")

    # Detect format — HTML goes direct, markdown gets converted
    fmt = meta.get("format", "markdown" if filename.endswith(".md") else "html")
    if fmt == "markdown":
        body_clean = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
        content_html = markdown.markdown(body_clean, extensions=["extra"])
    else:
        content_html = body

    # Unescape HTML entities to Unicode — prevents XML-RPC parse errors
    content_html = html_mod.unescape(content_html)
    content_html = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content_html)

    client = WordPressClient()

    featured_image_id = None
    if featured_image_path and os.path.isfile(featured_image_path):
        result = client.upload_image(featured_image_path)
        featured_image_id = result.get("id")

    # Check if post was previously published (has a WordPress post ID)
    wp_post_id = meta.get("wp_post_id", "")
    if wp_post_id:
        # Update existing post
        client.update_post(
            post_id=wp_post_id,
            title=title,
            content_html=content_html,
            tags=tags,
            status=status,
            featured_image_id=featured_image_id,
        )
        post_id = wp_post_id
        action = "Updated"
    else:
        # Create new post
        post_id = client.create_post(
            title=title,
            content_html=content_html,
            tags=tags,
            status=status,
            featured_image_id=featured_image_id,
        )
        action = "Created"

    admin_url = f"https://wordpress.com/post/{client.site}/{post_id}"

    # Update local file: status + wp_post_id
    with open(filepath, "r", encoding="utf-8") as f:
        local_text = f.read()
    local_text = re.sub(r'^(status:\s*).*$', f'\\1{status}', local_text, count=1, flags=re.MULTILINE)
    if f"wp_post_id:" in local_text:
        local_text = re.sub(r'^(wp_post_id:\s*).*$', f'\\1{post_id}', local_text, count=1, flags=re.MULTILINE)
    else:
        # Insert wp_post_id before the closing ---
        local_text = local_text.replace("\n---\n", f"\nwp_post_id: {post_id}\n---\n", 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(local_text)

    return jsonify({
        "ok": True,
        "post_id": post_id,
        "status": status,
        "admin_url": admin_url,
        "message": f"{action} as {status}! Post ID: {post_id}",
    })


@app.route("/ai/create-post", methods=["POST"])
def ai_create_post():
    """One-shot: scrape one or more URLs, generate full memorial post."""
    try:
        from ai_generator import create_post_from_sources
    except ImportError as e:
        return jsonify({"ok": False, "error": f"AI module not available: {e}"}), 500

    data = request.get_json()
    sources = data.get("sources", [])

    # Backward compat: accept single "source" string too
    if not sources and data.get("source"):
        sources = [data["source"].strip()]

    if not sources:
        return jsonify({"ok": False, "error": "Paste one or more URLs or type a handle"}), 400

    try:
        result = create_post_from_sources(sources)
        return jsonify({"ok": True, **result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/ai/restyle-post", methods=["POST"])
def ai_restyle_post():
    """Restyle a fetched post to match the 8bit Legends dark cinematic theme."""
    try:
        from ai_generator import restyle_post
    except ImportError as e:
        return jsonify({"ok": False, "error": f"AI module not available: {e}"}), 500

    data = request.get_json()
    content = data.get("content", "")
    sources = data.get("sources", [])

    if not content:
        return jsonify({"ok": False, "error": "No content to restyle"}), 400

    try:
        result = restyle_post(content, sources)
        return jsonify({"ok": True, **result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/ai/generate", methods=["POST"])
def ai_generate():
    """Generate memorial content via Claude API (legacy endpoint)."""
    try:
        from ai_generator import generate_memorial_content
    except ImportError as e:
        return jsonify({"ok": False, "error": f"AI module not available: {e}"}), 500

    data = request.get_json()
    name = data.get("name", "")
    handle = data.get("handle", "")
    group = data.get("group", "")
    role = data.get("role", "coder")
    contributions = data.get("contributions", "")
    extra_context = data.get("extra_context", "")

    if not name or not handle:
        return jsonify({"ok": False, "error": "Name and handle are required"}), 400

    result = generate_memorial_content(name, handle, group, role, contributions, extra_context)
    return jsonify({"ok": True, **result})


@app.route("/ai/enhance", methods=["POST"])
def ai_enhance():
    """Enhance selected text via Claude API."""
    try:
        from ai_generator import enhance_text
    except ImportError as e:
        return jsonify({"ok": False, "error": f"AI module not available: {e}"}), 500

    data = request.get_json()
    text = data.get("text", "")
    instruction = data.get("instruction", "Make this more detailed and heartfelt")

    if not text:
        return jsonify({"ok": False, "error": "No text provided"}), 400

    result = enhance_text(text, instruction)
    return jsonify({"ok": True, "content": result})


@app.route("/ai/research", methods=["POST"])
def ai_research():
    """Research a scener via CSDB, Pouet, and web. (Phase 3 stub)"""
    data = request.get_json()
    name = data.get("name", "")
    handle = data.get("handle", "")

    if not name and not handle:
        return jsonify({"ok": False, "error": "Name or handle required"}), 400

    # Phase 3 will implement research.py — return placeholder for now
    try:
        from research import search_scener
        results = search_scener(name, handle, data.get("group", ""))
        return jsonify({"ok": True, "results": results})
    except ImportError:
        return jsonify({
            "ok": True,
            "results": [
                {"source": "CSDB", "text": f"Research module not yet installed. Will search CSDB for '{handle or name}'."},
                {"source": "Pouet", "text": "Pouet search coming in Phase 3."},
            ]
        })


@app.route("/ai/images", methods=["POST"])
def ai_images():
    """Search for images of a scener. (Phase 3 stub)"""
    data = request.get_json()
    name = data.get("name", "")
    handle = data.get("handle", "")

    if not name and not handle:
        return jsonify({"ok": False, "error": "Name or handle required"}), 400

    # Phase 3 will implement image search — return placeholder for now
    try:
        from research import search_images
        images = search_images(name, handle, data.get("group", ""))
        return jsonify({"ok": True, "images": images})
    except ImportError:
        return jsonify({
            "ok": True,
            "images": []
        })


@app.route("/logo/<handle>")
def logo_preview(handle):
    """Generate and return a demoscene-style logo PNG for a handle."""
    from logo_generator import generate_logo_png, get_available_fonts
    font = request.args.get("font")
    max_width = request.args.get("max_width", 880, type=int)
    max_width = min(max(max_width, 100), 1200)
    png_data, used_font = generate_logo_png(handle, font_name=font, max_width=max_width)
    if png_data is None:
        return jsonify({"ok": False, "error": "No fonts available"}), 500
    return Response(png_data, mimetype="image/png",
                    headers={"X-Font-Used": used_font})


@app.route("/logo/fonts")
def logo_fonts():
    """Return list of available logo fonts."""
    from logo_generator import get_available_fonts, get_font_info
    fonts = get_available_fonts()
    return jsonify({"ok": True, "fonts": [get_font_info(f) for f in fonts]})


@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    """AI chat: modify post content based on free-form instruction."""
    try:
        from ai_generator import chat_modify_post
    except ImportError as e:
        return jsonify({"ok": False, "error": f"AI module not available: {e}"}), 500

    data = request.get_json()
    instruction = data.get("instruction", "").strip()
    content = data.get("content", "")

    if not instruction:
        return jsonify({"ok": False, "error": "No instruction provided"}), 400
    if not content:
        return jsonify({"ok": False, "error": "No content to modify"}), 400

    try:
        result = chat_modify_post(content, instruction)
        return jsonify({"ok": True, **result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/upload-image", methods=["POST"])
def upload_image():
    """Upload featured image to WordPress."""
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No file selected"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return jsonify({"ok": False, "error": "Invalid image format"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        client = WordPressClient()
        result = client.upload_image(tmp_path)
        return jsonify({
            "ok": True,
            "id": result.get("id"),
            "url": result.get("url"),
        })
    finally:
        os.unlink(tmp_path)


@app.route("/sync", methods=["POST"])
def sync_from_wordpress():
    """Fetch all posts from WordPress to local posts/ directory."""
    ensure_posts_dir()
    client = WordPressClient()
    posts = client.get_all_posts()

    count = 0
    skipped = 0
    for post in posts:
        date = post.get("date", "")[:10]
        slug = post.get("slug", "untitled")
        html_filename = f"{date}-{slug}.html"
        md_filename = f"{date}-{slug}.md"
        html_path = os.path.join(POSTS_DIR, html_filename)
        md_path = os.path.join(POSTS_DIR, md_filename)

        # Skip if already exists locally (don't overwrite local edits)
        if os.path.exists(html_path) or os.path.exists(md_path):
            skipped += 1
            continue

        local_content = client.post_to_local(post)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(local_content)
        count += 1

    msg = f"Synced {count} new posts from WordPress"
    if skipped:
        msg += f" ({skipped} already exist locally)"
    return jsonify({"ok": True, "message": msg})


@app.route("/delete/<filename>", methods=["POST"])
def delete_post(filename):
    """Delete a local post file."""
    filepath = os.path.join(POSTS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"ok": True, "message": f"Deleted: {filename}"})
    return jsonify({"ok": False, "error": "File not found"}), 404


if __name__ == "__main__":
    ensure_posts_dir()
    print("Starting 8bit Legends Web Editor v2.0...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
