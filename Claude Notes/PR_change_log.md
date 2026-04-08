# Change Log - 8bit Legends Memorial Editor

## 2026-04-08 - WordPress Block Styles in Editor

### Fixed
- **WordPress block styles rendering**: Synced posts with light-background sections (e.g. `background:#f4f4f4; color:#222`) had invisible/washed-out text because editor CSS forced light text colors globally. Added `color: inherit` rules for light-bg containers so child elements (p, strong, h2, a, blockquote) respect the parent's dark text color.
- **WordPress block class support**: Added CSS for `has-pale-ocean-gradient-background`, `has-background`, `has-medium-font-size`, `wp-block-columns`, `wp-block-column`, `wp-block-heading` so fetched WP content renders correctly in TinyMCE.

### Files Modified
- `static/editor-content.css` - Light-bg inherit rules, WordPress block class styles
- `templates/base.html` - Cache bust v4
- `templates/editor.html` - Cache bust v4 for TinyMCE content_css

---

## 2026-04-08 - WordPress Sync Fix (HTML Preservation)

### Fixed
- **Sync preserves HTML**: `post_to_local()` (renamed from `post_to_markdown()`) now keeps original WordPress HTML content instead of stripping to plain text via `html_to_text()`.
- **Sync tracks post IDs**: Synced posts now include `wp_post_id`, `status: fetched`, `format: html`, and `real_name:` in frontmatter — matching editor-created posts.
- **Sync saves as `.html`**: New synced files use `.html` extension instead of `.md`.
- **Sync skips existing files**: Won't overwrite local edits during re-sync.

### Files Modified
- `wp_client.py` - `post_to_local()` preserves HTML, editor-compatible frontmatter
- `app.py` - `sync_from_wordpress()` uses `.html`, skips existing files

---

## 2026-04-08 - Logo Generator, AI Chat, Deploy Updates

### Added
- **Demoscene Handle Logo Generator**: Renders handles using logo-o-matic spritesheet fonts (25 C64/Amiga fonts). Font picker dropdown, size slider (20-100%), preview and insert-into-post. Server-side rendering with Pillow from PNG spritesheets + JSON coordinate mappings.
- **AI Chat Assistant**: Free-form text input below editor where user types instructions (e.g. "add more images", "expand the biography") and AI modifies post content directly in TinyMCE.
- **Real Name field**: New metadata field for person's real name, used in RIP section generation.
- **Deploy update support**: Posts with `wp_post_id` use `wp.editPost` instead of `wp.newPost` — no more duplicates. Button text changes to "UPDATE" / "UPDATE LIVE" for already-published posts.
- **Logo upload to WordPress**: Logos are uploaded as media files via XML-RPC instead of base64 data URIs (which WordPress strips).

### Fixed
- **XML-RPC parse errors**: HTML entities (`&middot;`, `&ndash;`) broke XML-RPC encoding. Fixed by `html.unescape()` before sending.
- **Local status not updating after publish**: Publish route now updates frontmatter `status` in local file.
- **AI Chat div ID shadowing**: `<div id="aiChat">` shadowed the `aiChat()` JS function. Renamed to `aiChatPanel`.

### Files Modified
- `logo_generator.py` (new) - Spritesheet font renderer
- `fonts/fonts.json` (new) - Character coordinate data for 164 fonts
- `fonts/spritesheets/*.png` (new) - 25 font spritesheets
- `app.py` - Logo routes, AI chat route, deploy update logic, real_name support
- `ai_generator.py` - Logo integration, `chat_modify_post()`, real_name extraction
- `templates/editor.html` - Logo bar, AI chat panel, real name field, deploy/update UI
- `static/app.js` - Logo functions, AI chat, save/publish updates
- `static/style.css` - Logo bar, AI chat, real name field styles
- `templates/base.html` - Cache bust v3

---

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
