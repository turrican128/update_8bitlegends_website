# Change Log - 8bit Legends Memorial Editor

## 2026-05-28 - App Launcher, Modals, Publish Robustness & Inline-Image Fix

### Added
- **One-command app launcher**: `python app.py` now auto-frees a stuck port (kills a stale process holding it), auto-opens the browser, and supports flags (`--port`, `--host`, `--no-browser`, `--keep-port`, `--no-debug`). UTF-8 stdout so arrows/emoji don't crash a cp1255 console. `launch.bat` added for double-click launching.
- **Delete confirmation modal**: Deleting a post on the dashboard now opens a styled yes/no modal (was the browser `confirm()`). Matches the publish modal look.
- **Unsaved-changes modal in editor**: Clicking POSTS / NEW / logo with unsaved edits opens a styled modal (Cancel / Save & Leave / Leave Without Saving) instead of TinyMCE's native browser "Leave site?" dialog. `savePost()` now returns `Promise<boolean>` so "Save & Leave" waits for the save to succeed.
- **Duplicate-post guard**: `WordPressClient.find_post_id_by_title()` — when publishing a post with no local `wp_post_id`, the publish route looks up WordPress by exact title and *updates* the existing post instead of creating a duplicate (covers the case where a prior publish created the post but failed to write the id back locally).
- **Inline image upload on publish**: `upload_inline_images()` uploads any inline base64 `data:` image to WordPress media and swaps in the URL before publishing.

### Fixed
- **Dead DEPLOY modal buttons (dashboard & preview)**: `publishPost()` never wired the SAVE AS DRAFT / PUBLISH LIVE buttons or recorded which post to publish, so publishing from a card did nothing. Now wired to the selected post.
- **Broken images on the live site**: WordPress strips the `data:` scheme from img src on save (KSES), turning `data:image/png;base64,…` into the invalid `image/png;base64,…`. Inline base64 images (e.g. C64-style handle logos) now upload as media instead. Also repaired the already-broken "In Memory of TSN" post (uploaded its logo, relinked it).
- **Invisible DELETE button**: `.btn-danger` was a near-invisible transparent `×`; now a clearly visible, labelled red button pushed to the card's right edge.
- **TSN post local/WordPress mismatch**: Reconciled local frontmatter (`status: publish`, `wp_post_id: 70971`) after a publish write-back failure.

### Changed
- **UPDATE vs DEPLOY wording**: Dashboard cards and the publish/preview modals now say UPDATE ON WORDPRESS / UPDATE LIVE / UPDATE AS DRAFT for posts already on WordPress (have a `wp_post_id`), matching the editor; new posts still say DEPLOY / PUBLISH LIVE.
- **POSTS nav link** hidden on the dashboard itself (redundant there); still shown on editor/preview.
- Static cache-bust bumped v11 → v14.

### Files Modified
- `app.py` — launcher (`main()`/`_free_port()`/`_pids_on_port()`/`_port_in_use()`), `upload_inline_images()`, duplicate-guard in publish route, `wp_post_id` exposed in post list + preview route, UTF-8 stdout
- `wp_client.py` — `find_post_id_by_title()`
- `static/app.js` — delete-confirm modal, publish-button wiring + UPDATE/DEPLOY wording, `savePost()` returns a promise, generalized modal close handlers
- `static/style.css` — visible DELETE button, card-action `flex-wrap`
- `templates/index.html` — delete modal, DELETE label, UPDATE/DEPLOY button, publish modal title id
- `templates/preview.html` — UPDATE/DEPLOY wording
- `templates/editor.html` — unsaved-changes modal + leave-guard JS, `autosave_ask_before_unload: false`
- `templates/base.html` — POSTS nav conditional, cache-bust v12→v14
- `launch.bat` (new) — double-click launcher

---

## 2026-04-08 - Per-Post WP Fetch, Inline SVG Watermarks, Editor Fixes

### Added
- **Per-post FETCH WP button**: New button in editor toolbar (visible when post has `wp_post_id`) fetches the latest version of that single post from WordPress into the editor. Replaces the old bulk "SYNC WP" dashboard button which risked overwriting local edits.
- **Inline SVG watermark elements**: C64 and Amiga presets now inject real SVG DOM elements (position:absolute, low opacity) scattered throughout the post as retro silhouettes:
  - C64 preset (8 elements): breadbin+monitor, SID 6581 chip, datasette, joystick, 1541 floppy drive, PETSCII stars, power LED, floppy disk
  - Amiga preset (9 elements): A500+monitor, RGB bars, Amiga checkmark, Boing ball, mouse, Guru Meditation box, copper gradient bars, mini Boing ball, floppy disk
- **New endpoint**: `GET /fetch-wp/<post_id>` — fetches single post from WP REST API, returns title/tags/featured_image/body as JSON

### Fixed
- **TinyMCE stripping WordPress HTML**: Removed `extended_valid_elements` (was overriding `valid_elements:'*[*]'` and stripping `class` from elements). Added `verify_html:false`, `remove_trailing_brs:false`, `custom_elements:'figure,figcaption'`.
- **setContent raw mode**: WP fetch uses `setContent(html, {format:'raw'})` to bypass TinyMCE's HTML parser — preserves all WP block classes, figures, and structure.
- **WordPress background color classes**: Added CSS for all WP background classes found across the site: `has-pale-cyan-blue`, `has-cyan-bluish-gray`, `has-light-green-cyan`, `has-luminous-vivid-amber`, `has-pale-pink`, `has-vivid-green-cyan`, `has-white`, `has-blush-light-purple-gradient`. All get dark text (#222) and dark links (#1565c0).
- **Tracking pixel images hidden**: 1x1 GIFs and tracking pixels (`display:none` in editor CSS).
- **Image sizing**: Changed `width:100%` to `max-width:100%` so images respect natural dimensions.
- **SVG watermarks (previously broken)**: Replaced failed CSS `background-image` data URI approach with real inline `<svg>` DOM elements — 100% reliable rendering.

### Removed
- Bulk "SYNC WP" button from dashboard (replaced by per-post fetch in editor)
- Old `/sync` endpoint

### Files Modified
- `app.py` — New `/fetch-wp/<post_id>` endpoint, removed `/sync` endpoint
- `post_styles.py` — `C64_WATERMARK_SVGS` and `AMIGA_WATERMARK_SVGS` inline SVG strings (replaced data URI approach)
- `ai_generator.py` — SVG injection via DOM insertion instead of CSS background
- `static/app.js` — `fetchFromWordPress()`, `setEditorContent()` raw mode support
- `static/editor-content.css` — All WP background color classes, tracking pixel hiding, wp-block styles
- `templates/editor.html` — FETCH WP button, TinyMCE config fixes (verify_html, custom_elements)
- `templates/index.html` — Removed SYNC WP button
- `templates/base.html` — Cache bust v11

---

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
