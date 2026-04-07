# Change Log - 8bit Legends Memorial Editor

## 2026-04-07 - CSDB Image Extraction + RIP Flower Section

### Added
- **RIP Flower Section**: Every memorial post now ends with a centered "RIP [First Name]" section with rose emoji. Added `rip_flower` style to `post_styles.py`, updated `template.html` and `get_template_html()`, and instructed Claude to always generate this as the last element.
- **CSDB Release Screenshot Extraction**: `scrape_csdb()` now extracts up to 8 release screenshot URLs from scener profiles using the CSDB URL pattern (`/gfx/releases/{floor}/{id}.png`). Previously extracted zero images.
- **C64GFX.com Image Extraction**: `scrape_c64gfx()` now extracts actual artwork image URLs (was only counting `<img>` tags before).
- **Multi-image Support in AI Prompt**: `_format_all_sources()` passes numbered image URL lists to Claude when available. `SYSTEM_PROMPT` instructs Claude to embed 1-3 relevant images with captions using the `image` and `image_caption` styles.

### Fixed
- **CSDB Handle/Groups Extraction**: Rewrote `scrape_csdb()` to parse handle and groups from the `<title>` tag (`[CSDb] - Handle/Group1/Group2`) instead of broken `<h2>` regex. Now reliably extracts handle, groups, and country.

### Files Modified
- `post_styles.py` - Added `rip_flower` style, updated `get_template_html()`
- `template.html` - Added RIP flower HTML section
- `ai_generator.py` - CSDB/C64GFX image extraction, SYSTEM_PROMPT updates, RIP instructions in all prompts

---

## 2026-04-06 - WYSIWYG Editor Redesign (v2.0)

### Added
- **TinyMCE WYSIWYG Editor**: Replaced EasyMDE markdown editor with TinyMCE 7 (oxide-dark skin). Posts now stored as HTML with inline CSS.
- **post_styles.py** (new): Central inline CSS style definitions for memorial posts. Color palette, Georgia serif, all post elements.
- **static/editor-content.css** (new): CSS for TinyMCE iframe to match final WordPress rendering.
- **template.html** (new): HTML post template with YAML frontmatter and inline-styled sections.
- **Simplified AI Panel**: Below-editor panel with multi-URL textarea + CREATE POST / ENHANCE SELECTION buttons. Replaced complex 4-input + 4-button + 3-column layout.
- **Multi-Source Scraper**: Domain-detecting scraper system (`detect_and_scrape()`) routing to specialized scrapers for CSDB, Pouet, C64GFX.com, and generic URLs.
- **One-Shot AI Generation**: Paste URL(s), get complete styled memorial post. Endpoint: `POST /ai/create-post`.
- **Dashboard Limiting**: Shows all drafts + 6 most recent published posts (not all 37).
- **Lazy Markdown Migration**: Legacy `.md` posts auto-convert to HTML when opened in editor.
- **HTML Format Support**: `save_post()`, `preview_post()`, `publish_post()` all handle `format: html` in frontmatter.

### Removed
- EasyMDE editor and all related CSS overrides
- CRT scanline overlay effect from base.html
- Complex AI sidebar with research/image panels
- Old AI functions (aiGenerate, aiResearch, aiImages, renderSuggestions, toggleExtraFields)

### Files Modified
- `templates/base.html` - TinyMCE CDN, removed CRT overlay, version bump to v2.0
- `templates/editor.html` - Full rewrite for TinyMCE + AI panel
- `static/style.css` - Removed EasyMDE/sidebar styles, added TinyMCE/AI panel styles
- `static/app.js` - Full rewrite for TinyMCE interaction + new AI flow
- `app.py` - HTML format support, dashboard limiting, new `/ai/create-post` route
- `ai_generator.py` - Full rewrite with multi-source scrapers and styled HTML generation
