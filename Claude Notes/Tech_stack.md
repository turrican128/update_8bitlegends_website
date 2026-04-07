# Tech Stack - 8bit Legends Memorial Editor

## Backend
- **Python 3** with **Flask** web framework
- **Anthropic Claude API** (claude-sonnet-4) for AI memorial post generation
- **WordPress XML-RPC** for publishing posts to 8bitlegends.com (WordPress.com, site ID 81368875)
- **WordPress.com REST API v1.1** for reading/fetching posts (no auth needed)

## Frontend
- **TinyMCE 7** (CDN) - WYSIWYG HTML editor with oxide-dark skin
- Vanilla JavaScript (no frameworks)
- Custom CSS with retro-inspired design (Press Start 2P, VT323, IBM Plex Mono fonts)

## Post Format
- HTML with inline CSS (self-contained, theme-independent)
- YAML frontmatter (title, status, format, tags, featured_image)
- Stored as `.html` files in `posts/` directory
- Legacy `.md` posts auto-convert to HTML on edit (lazy migration)

## Style System
- `post_styles.py` defines all inline CSS as a Python dict (`POST_STYLES`)
- Color palette: warm earthy tones (#8b7355 accent, #1a1a2e dark, Georgia serif)
- `static/editor-content.css` mirrors styles inside TinyMCE iframe for WYSIWYG fidelity

## AI Generation Pipeline
1. User pastes source URLs (CSDB, Pouet, C64GFX.com, Facebook, generic)
2. Domain-detecting scrapers extract handle, groups, real name, country, page text, images
3. CSDB release screenshots extracted via URL pattern: `csdb.dk/gfx/releases/{floor}/{id}.png`
4. All data formatted and sent to Claude Sonnet with styled HTML template
5. Claude generates complete memorial post with inline styles, embedded images, RIP flower section
6. User edits in TinyMCE, then publishes as WordPress draft via XML-RPC

## Dependencies (requirements.txt)
- `requests` - HTTP client
- `python-dotenv` - .env credential loading
- `markdown` - Legacy markdown-to-HTML conversion
- `flask` - Web framework
- `anthropic` - Claude API SDK

## Auth & Credentials (.env, never committed)
- `WP_SITE` - WordPress site URL
- `WP_USERNAME` - WordPress username
- `WP_APP_PASSWORD` - WordPress application password
- `ANTHROPIC_API_KEY` - Claude API key
- `FLASK_SECRET` - Flask session secret
