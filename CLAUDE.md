# 8bit Legends Memorial Editor

Web-based WYSIWYG editor + CLI for managing memorial posts on [8bitlegends.com](https://8bitlegends.com) — a demoscene memorial site honoring Commodore 64 and retro computing legends.

## Running

```
python app.py                           # Start web editor on http://localhost:5000
python main.py fetch                    # CLI: Download all posts from WordPress
python main.py list                     # CLI: List local posts
python main.py new "Post Title"         # CLI: Create draft from template
python main.py publish <file.md>        # CLI: Upload as draft
python main.py publish --live <file.md> # CLI: Publish immediately
```

## Project Structure

### Web Editor (Flask)
- `app.py` — Flask web app (routes for editor, save, publish, sync, AI endpoints)
- `templates/base.html` — Base layout with nav, TinyMCE CDN, cache-busted static assets
- `templates/editor.html` — WYSIWYG editor page (TinyMCE, AI panel, logo generator, metadata fields)
- `templates/index.html` — Dashboard listing drafts and published posts
- `static/app.js` — Client-side JS (save, publish, AI create/restyle/enhance/chat, logo generator)
- `static/style.css` — Dark retro theme styles
- `static/editor-content.css` — TinyMCE iframe styles (matches WordPress rendering + WP block classes)

### AI & Content Generation
- `ai_generator.py` — Claude-powered post generation, restyling, enhancement, and chat modification
- `post_styles.py` — Inline CSS style definitions (`POST_STYLES` dict) and `get_template_html()`
- `template.html` — HTML post template with inline-styled sections

### Logo Generator
- `logo_generator.py` — Renders demoscene handle logos from spritesheet fonts (Pillow)
- `fonts/fonts.json` — Character coordinate mappings for 164 fonts
- `fonts/spritesheets/*.png` — 25 C64/Amiga font spritesheets

### WordPress Integration
- `wp_client.py` — WordPress API client (REST API for reading, XML-RPC for writing/updating)
- `main.py` — CLI entry point (fetch, list, new, publish commands)

### Data
- `posts/` — Local HTML/MD files with YAML-like frontmatter
- `.env` — WordPress credentials (WP_SITE, WP_USERNAME, WP_APP_PASSWORD) — never commit

## Key Details

- **Site**: 8bitlegends.com (WordPress.com, site ID 81368875)
- **Category**: All posts go to "memories" category
- **Auth**: XML-RPC with application password (stored in `.env`, never commit)
- **Reading**: Public WordPress.com REST API v1.1 (no auth needed)
- **Writing**: XML-RPC (`wp.newPost` for create, `wp.editPost` for update, `wp.uploadFile` for media)
- **Post tracking**: `wp_post_id` in frontmatter links local files to WordPress posts (prevents duplicates on deploy)
- **Posts format**: HTML with inline CSS + YAML-like frontmatter (title, status, tags, featured_image, real_name, wp_post_id, format)
- **Editor**: TinyMCE 7 with oxide-dark skin, content CSS mirrors the dark cinematic WordPress theme
- **AI model**: Claude Sonnet (`claude-sonnet-4-20250514`) for all generation/modification

## Web Editor Features

- **WYSIWYG editing** with TinyMCE (dark cinematic theme preview)
- **AI Create Post**: Paste CSDB/Pouet/C64GFX/generic URLs → scrapes and generates full styled memorial
- **AI Restyle**: For fetched WordPress posts — restyles existing content to dark cinematic theme
- **AI Enhance Selection**: Enhance selected text in the editor
- **AI Chat**: Free-form instructions to modify post content (e.g. "add more images", "expand the biography")
- **Handle Logo Generator**: Renders demoscene handles using C64/Amiga spritesheet fonts, uploads to WordPress as media
- **WordPress Sync**: Fetches all posts from WordPress preserving original HTML content
- **Deploy/Update**: Publishes to WordPress as draft or live; updates existing posts via wp_post_id

## Dependencies

- `flask` — Web framework
- `requests` — HTTP client for REST API and scraping
- `python-dotenv` — Load `.env` credentials
- `anthropic` — Claude AI API client
- `Pillow` — Image processing for logo generator
- `beautifulsoup4` — HTML scraping for CSDB/Pouet/C64GFX
- `markdown` — Legacy markdown-to-HTML conversion
