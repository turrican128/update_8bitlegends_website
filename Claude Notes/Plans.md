# Future Plans & Ideas - 8bit Legends Memorial Editor

## Phase 3 - Deep Research Module
- Create dedicated `research.py` module with more robust CSDB/Pouet scraping
- CSDB: extract full release history, SID compositions, group memberships timeline, event participation
- Pouet: use JSON API for production credits, party results, BBS affiliations
- DeepSID integration: link to scener's SID music collection on deepsid.chordian.net
- Remix64 integration: link to remix/cover versions of their music
- Cross-reference scener across multiple databases for richer profiles

## Phase 4 - CLI & Sync Updates
- Update `wp_client.py` sync to save fetched posts as `.html` (currently saves `.md`)
- Update `main.py` CLI commands to handle HTML format natively
- `cmd_publish()`: detect format, skip markdown conversion for HTML
- `cmd_new()`: use HTML template instead of markdown
- `cmd_fetch()`: save as `.html` files
- Update `requirements.txt` with `beautifulsoup4`, `lxml` if needed
- Update `CLAUDE.md` to reflect v2.0 architecture

## Ideas for Future Development

### Content Enrichment
- Auto-detect DeepSID links for SID musicians and embed player widget
- Auto-detect YouTube/Vimeo demo captures and embed video with `video_embed` style
- Pull Facebook memorial group posts/comments as additional source material
- Instagram scraping for profile photos and memorial posts

### Editor Improvements
- Image upload directly from editor (drag & drop into TinyMCE)
- Template picker: choose from different memorial post styles/layouts
- Block library: save and reuse common sections across posts (e.g., standard demoscene group descriptions)
- Revision history: track edits with diff view
- Batch import: process multiple memorial posts from a CSV/list

### Publishing & Integration
- Preview in WordPress theme before publishing (iframe preview)
- Schedule posts for specific dates (memorial anniversaries)
- Social media sharing: auto-generate Facebook/Twitter posts with link
- RSS feed generation for the memorial site
- Email notification to subscribers when new memorial is published

### Data & Analytics
- Scener database: maintain a local database of known C64/Amiga sceners for auto-complete and cross-referencing
- Map view: show where sceners were from geographically
- Timeline view: chronological view of all memorials
- Statistics: count by country, group, role (coder/musician/artist/swapper)

### Source Expansion
- Discogs integration for musicians who crossed into commercial music (like Chosen Few)
- MobyGames for sceners who worked in the game industry
- Lemon64 forum threads about deceased sceners
- Demozoo API as additional demoscene database
