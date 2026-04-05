#!/usr/bin/env python3
"""8bit Legends Web Editor - Flask app for managing memorial posts."""

import os
import re
import json
import tempfile
from datetime import datetime

import markdown
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_from_directory
)
from dotenv import load_dotenv

from wp_client import WordPressClient
from post_generator import generate_post, COMMON_TAGS, COMMON_GROUPS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "8bit-legends-dev-key")

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


def build_frontmatter(title, tags, status="draft", featured_image=""):
    """Build YAML frontmatter string."""
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    lines = [
        "---",
        f'title: "{title}"',
        f"status: {status}",
        f"tags: {json.dumps(tags)}",
        f"featured_image: {featured_image}",
        "---",
    ]
    return "\n".join(lines)


def get_all_local_posts():
    """Read all posts from posts/ directory."""
    ensure_posts_dir()
    posts = []
    files = sorted(
        (f for f in os.listdir(POSTS_DIR) if f.endswith(".md")),
        reverse=True
    )
    for f in files:
        filepath = os.path.join(POSTS_DIR, f)
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()
        meta, body = parse_frontmatter(text)
        posts.append({
            "filename": f,
            "title": meta.get("title", f),
            "status": meta.get("status", "fetched"),
            "tags": meta.get("tags", []),
            "date": f[:10] if len(f) >= 10 else "",
            "excerpt": body.strip()[:150] + "..." if len(body.strip()) > 150 else body.strip(),
        })
    return posts


# ── Routes ─────────────────────────────────────────────────────


@app.route("/")
def index():
    """Dashboard - list all local posts."""
    posts = get_all_local_posts()
    return render_template("index.html", posts=posts)


@app.route("/new")
def new_post():
    """New post editor with template."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_text = f.read()
    meta, body = parse_frontmatter(template_text)
    return render_template(
        "editor.html",
        filename=None,
        title=meta.get("title", ""),
        tags=", ".join(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else meta.get("tags", ""),
        featured_image=meta.get("featured_image", ""),
        body=body,
        common_tags=COMMON_TAGS,
        common_groups=COMMON_GROUPS,
        is_new=True,
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
    tags = meta.get("tags", [])
    if isinstance(tags, list):
        tags = ", ".join(tags)

    return render_template(
        "editor.html",
        filename=filename,
        title=meta.get("title", ""),
        tags=tags,
        featured_image=meta.get("featured_image", ""),
        body=body,
        common_tags=COMMON_TAGS,
        common_groups=COMMON_GROUPS,
        is_new=False,
    )


@app.route("/save", methods=["POST"])
def save_post():
    """Save post to posts/ directory."""
    ensure_posts_dir()

    data = request.get_json() if request.is_json else request.form
    title = data.get("title", "Untitled")
    tags = data.get("tags", "")
    featured_image = data.get("featured_image", "")
    body = data.get("body", "")
    filename = data.get("filename", "")

    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    frontmatter = build_frontmatter(title, tags, "draft", featured_image)
    full_content = frontmatter + "\n\n" + body

    if not filename:
        date = datetime.now().strftime("%Y-%m-%d")
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{date}-{slug}.md"

    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    if request.is_json:
        return jsonify({"ok": True, "filename": filename, "message": f"Saved: {filename}"})

    flash(f"Saved: {filename}", "success")
    return redirect(url_for("edit_post", filename=filename))


@app.route("/preview/<filename>")
def preview_post(filename):
    """Render markdown as HTML preview."""
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        flash(f"File not found: {filename}", "error")
        return redirect(url_for("index"))

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    meta, body = parse_frontmatter(text)
    body_clean = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    content_html = markdown.markdown(body_clean, extensions=["extra"])

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

    body_clean = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    content_html = markdown.markdown(body_clean, extensions=["extra"])

    client = WordPressClient()

    featured_image_id = None
    if featured_image_path and os.path.isfile(featured_image_path):
        result = client.upload_image(featured_image_path)
        featured_image_id = result.get("id")

    post_id = client.create_post(
        title=title,
        content_html=content_html,
        tags=tags,
        status=status,
        featured_image_id=featured_image_id,
    )

    admin_url = f"https://wordpress.com/post/{client.site}/{post_id}"

    return jsonify({
        "ok": True,
        "post_id": post_id,
        "status": status,
        "admin_url": admin_url,
        "message": f"Published as {status}! Post ID: {post_id}",
    })


@app.route("/ai/generate", methods=["POST"])
def ai_generate():
    """Generate memorial content via Claude API."""
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
    for post in posts:
        date = post.get("date", "")[:10]
        slug = post.get("slug", "untitled")
        filename = f"{date}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)

        md_content = client.post_to_markdown(post)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        count += 1

    return jsonify({"ok": True, "message": f"Synced {count} posts from WordPress"})


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
    print("Starting 8bit Legends Web Editor...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
