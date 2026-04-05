# 8bit Legends WordPress CLI

Python CLI tool for managing memorial posts on [8bitlegends.com](https://8bitlegends.com) — a demoscene memorial site honoring Commodore 64 and retro computing legends.

## Project Structure

- `main.py` — CLI entry point (fetch, list, new, publish commands)
- `wp_client.py` — WordPress API client (public REST API for reading, XML-RPC for writing)
- `post_generator.py` — Template-based post generator with demoscene vocabulary
- `template.md` — Default markdown template for new memorial posts
- `posts/` — Local markdown files with YAML frontmatter (fetched or drafted)
- `.env` — WordPress credentials (WP_SITE, WP_USERNAME, WP_APP_PASSWORD)

## Commands

```
python main.py fetch                    # Download all posts from WordPress
python main.py list                     # List local posts
python main.py new "Post Title"         # Create draft from template
python main.py publish <file.md>        # Upload as draft
python main.py publish --live <file.md> # Publish immediately
```

## Key Details

- **Site**: 8bitlegends.com (WordPress.com, site ID 81368875)
- **Category**: All posts go to "memories" category
- **Auth**: XML-RPC with application password (stored in `.env`, never commit)
- **Reading**: Public WordPress.com REST API v1.1 (no auth needed)
- **Writing**: XML-RPC (`wp.newPost`, `wp.uploadFile`)
- **Posts format**: Markdown with YAML frontmatter (title, status, tags, featured_image)

## Dependencies

- `requests` — HTTP client for REST API
- `python-dotenv` — Load `.env` credentials
- `markdown` — Convert post markdown to HTML before publishing
