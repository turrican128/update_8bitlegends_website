#!/usr/bin/env python3
"""Inline CSS style definitions for 8bit Legends memorial posts.

Dark cinematic theme based on the Rebecca Heineman memorial page —
radial gradients, glassmorphic borders, responsive card grids.
Styles are embedded directly in the post HTML so posts render
correctly in any WordPress theme without depending on external CSS.
"""

# Color palette — dark cinematic (Rebecca Heineman page reference)
COLORS = {
    # Backgrounds
    "bg_gradient_start": "#27293b",
    "bg_gradient_mid": "#141521",
    "bg_gradient_end": "#0a0b12",
    "bg_card": "rgba(8,8,18,0.8)",
    "bg_card_gradient": "radial-gradient(circle at top,rgba(80,70,150,0.55),rgba(10,10,22,0.96))",
    "bg_quote_gradient": "linear-gradient(120deg,rgba(255,255,255,0.09),rgba(110,90,214,0.16))",
    "bg_rip_gradient": "linear-gradient(135deg,rgba(38,41,56,0.92),rgba(22,23,32,0.9))",
    # Text
    "text_primary": "#f5f5f7",
    "text_body": "#e9e9f4",
    "text_secondary": "#bbbbcc",
    "text_muted": "#b9b9c9",
    "text_card_sub": "#d0cfe9",
    "text_card_body": "#ececf8",
    "text_milestone": "#dadaf2",
    "white": "#ffffff",
    # Accents
    "emphasis": "#ffe1ff",       # soft pink for game/demo titles
    "accent_blue": "#9be8ff",    # monospace footer, links
    "accent_tribute": "#f3f3ff",
    # Borders
    "border_glass": "rgba(170,170,210,0.3)",
    "border_glass_light": "rgba(190,190,240,0.4)",
    "border_quote": "rgba(255,255,255,0.45)",
    # Shadows
    "shadow_main": "0 22px 40px rgba(0,0,0,0.55)",
    "shadow_card": "0 16px 26px rgba(0,0,0,0.7),0 0 14px rgba(135,200,255,0.25)",
    "shadow_image": "0 10px 22px rgba(0,0,0,0.8),0 0 8px rgba(180,220,255,0.35)",
    "shadow_rip": "0 12px 28px rgba(0,0,0,0.45)",
    # Flower image
    "flower_url": "https://amigac64.wordpress.com/wp-content/uploads/2015/04/flower6.png",
}

FONT_STACK = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"

# Inline styles for each post element
POST_STYLES = {
    "wrapper": (
        f"max-width:880px;margin:0 auto 4rem auto;padding:2.5rem 2rem 3rem;"
        f"font-family:{FONT_STACK};line-height:1.8;color:{COLORS['text_primary']};"
        f"background:radial-gradient(circle at top,{COLORS['bg_gradient_start']} 0%,"
        f"{COLORS['bg_gradient_mid']} 45%,{COLORS['bg_gradient_end']} 100%);"
        f"border-radius:16px;box-shadow:{COLORS['shadow_main']};"
        "position:relative;overflow:hidden"
    ),
    "memorial_header": (
        "text-align:center;margin-bottom:2rem;position:relative;z-index:1"
    ),
    "person_name": (
        "font-size:2.2rem;margin:0 0 0.4rem;letter-spacing:0.04em;"
        f"color:{COLORS['white']}"
    ),
    "person_handle": (
        f"font-size:0.98rem;font-weight:600;letter-spacing:0.2em;"
        f"text-transform:uppercase;color:{COLORS['text_secondary']};margin:0"
    ),
    "person_dates": (
        f"font-size:0.95rem;font-weight:600;letter-spacing:0.12em;"
        f"text-transform:uppercase;color:{COLORS['text_secondary']};margin:0"
    ),
    "section_heading": (
        f"margin:0 0 0.85rem;font-size:1.25rem;color:{COLORS['white']}"
    ),
    "paragraph": (
        f"margin:0 0 1rem;color:{COLORS['text_body']};font-size:0.98rem"
    ),
    "paragraph_strong": (
        f"color:{COLORS['white']}"
    ),
    "paragraph_em": (
        f"color:{COLORS['emphasis']};font-style:normal"
    ),
    "image": (
        "display:block;width:100%;height:auto;border-radius:10px;"
        f"box-shadow:{COLORS['shadow_image']}"
    ),
    "image_container": (
        "position:relative;border-radius:10px;overflow:hidden;"
        f"margin-bottom:0.6rem;background:#000;box-shadow:{COLORS['shadow_image']}"
    ),
    "image_caption": (
        f"font-size:0.8rem;color:{COLORS['text_muted']};"
        "text-align:center;font-style:italic;margin:5px 0 20px 0"
    ),
    "blockquote": (
        f"margin:2.5rem 0 2.25rem;padding:1.5rem 1.6rem;"
        f"border-left:4px solid {COLORS['border_quote']};"
        f"background:{COLORS['bg_quote_gradient']};"
        f"font-style:italic;color:{COLORS['accent_tribute']};"
        "border-radius:8px;position:relative;overflow:hidden"
    ),
    "blockquote_mark": (
        "position:absolute;top:-26px;right:12px;font-size:4.5rem;"
        "color:rgba(255,255,255,0.06);font-style:normal"
    ),
    "milestones_section": (
        f"margin:0 0 2.25rem;padding:1.5rem 1.7rem 1.7rem;"
        f"background-color:{COLORS['bg_card']};"
        f"border-radius:12px;border:1px solid {COLORS['border_glass']}"
    ),
    "milestones_list": (
        f"line-height:1.7;margin:0;padding-left:1.1rem;"
        f"font-size:0.95rem;color:{COLORS['text_milestone']}"
    ),
    "milestones_bold": (
        f"color:{COLORS['white']}"
    ),
    "works_grid": (
        "display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));"
        "gap:1.1rem;margin-top:0.5rem"
    ),
    "works_card": (
        f"background:{COLORS['bg_card_gradient']};"
        f"border-radius:14px;padding:0.9rem 0.9rem 1rem;"
        f"border:1px solid {COLORS['border_glass_light']};"
        f"box-shadow:{COLORS['shadow_card']}"
    ),
    "works_card_title": (
        f"font-weight:700;font-size:0.98rem;color:{COLORS['white']};"
        "margin:0 0 0.15rem"
    ),
    "works_card_subtitle": (
        f"font-size:0.8rem;color:{COLORS['text_card_sub']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.35rem"
    ),
    "works_card_body": (
        f"font-size:0.9rem;color:{COLORS['text_card_body']};margin:0"
    ),
    "closing_tribute": (
        "text-align:center;margin-top:2.4rem"
    ),
    "closing_tribute_text": (
        f"font-weight:600;font-size:1.02rem;color:{COLORS['accent_tribute']};"
        "margin-bottom:0.6rem"
    ),
    "closing_tribute_stars": (
        "font-family:'Courier New',monospace;font-size:0.78rem;"
        f"letter-spacing:0.16em;text-transform:uppercase;color:{COLORS['accent_blue']};"
        "opacity:0.9"
    ),
    "links_section": (
        f"margin-top:2rem;padding-top:1.5rem;"
        f"border-top:1px solid {COLORS['border_glass']}"
    ),
    "links_heading": (
        f"font-size:0.85rem;color:{COLORS['text_muted']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.6rem"
    ),
    "link": (
        f"color:{COLORS['accent_blue']};text-decoration:underline"
    ),
    "rip_section": (
        f"text-align:center;margin:2.8rem auto 2rem;padding:1.8rem 1rem;"
        f"background:{COLORS['bg_rip_gradient']};"
        f"border-radius:14px;max-width:720px;box-shadow:{COLORS['shadow_rip']}"
    ),
    "rip_heading": (
        f"font-size:2.1rem;margin:0;color:{COLORS['accent_tribute']};"
        "font-weight:600;letter-spacing:0.03em"
    ),
    "rip_subtitle": (
        f"margin-top:1rem;font-size:0.95rem;color:{COLORS['text_muted']};"
        "letter-spacing:0.08em;text-transform:uppercase"
    ),
    "video_embed": (
        "position:relative;padding-bottom:56.25%;height:0;"
        "overflow:hidden;max-width:100%;margin:20px 0"
    ),
}


# ── C64 Retro Preset ─────────────────────────────────────────

C64_COLORS = {
    "bg_main": "#4040e0",
    "bg_dark": "#2020a0",
    "bg_card": "rgba(32,32,120,0.85)",
    "bg_card_gradient": "linear-gradient(180deg,rgba(64,64,224,0.9),rgba(32,32,120,0.95))",
    "bg_quote": "linear-gradient(120deg,rgba(160,160,255,0.15),rgba(64,64,224,0.25))",
    "bg_rip": "linear-gradient(135deg,rgba(32,32,120,0.92),rgba(16,16,80,0.9))",
    "text_primary": "#a0a0ff",
    "text_body": "#c0c0ff",
    "text_secondary": "#8080d0",
    "text_muted": "#9090c0",
    "white": "#ffffff",
    "emphasis": "#70f0ff",
    "accent": "#70f0ff",
    "border": "rgba(160,160,255,0.5)",
    "border_light": "rgba(160,160,255,0.6)",
    "shadow_main": "0 22px 40px rgba(0,0,80,0.6)",
    "shadow_card": "0 12px 20px rgba(0,0,80,0.7)",
    "shadow_image": "0 8px 18px rgba(0,0,80,0.7)",
    "shadow_rip": "0 12px 28px rgba(0,0,80,0.5)",
    "flower_url": "https://amigac64.wordpress.com/wp-content/uploads/2015/04/flower6.png",
}

C64_FONT = "'C64 Pro Mono','Courier New',monospace"

C64_STYLES = {
    "wrapper": (
        f"max-width:880px;margin:0 auto 4rem auto;padding:2.5rem 2rem 3rem;"
        f"font-family:system-ui,-apple-system,sans-serif;line-height:1.8;color:{C64_COLORS['text_primary']};"
        f"background:{C64_COLORS['bg_main']};"
        f"border:3px solid {C64_COLORS['border']};border-radius:4px;"
        f"box-shadow:{C64_COLORS['shadow_main']};position:relative;overflow:hidden"
    ),
    "memorial_header": (
        "text-align:center;margin-bottom:2rem;position:relative;z-index:1;"
        f"border-bottom:2px solid {C64_COLORS['border']};padding-bottom:1.5rem"
    ),
    "person_name": (
        f"font-size:2rem;margin:0 0 0.4rem;letter-spacing:0.08em;text-transform:uppercase;"
        f"color:{C64_COLORS['white']}"
    ),
    "person_handle": (
        f"font-size:0.95rem;font-weight:600;letter-spacing:0.2em;"
        f"text-transform:uppercase;color:{C64_COLORS['text_secondary']};margin:0"
    ),
    "person_dates": (
        f"font-size:0.95rem;font-weight:600;letter-spacing:0.12em;"
        f"text-transform:uppercase;color:{C64_COLORS['text_secondary']};margin:0"
    ),
    "section_heading": (
        f"margin:0 0 0.85rem;font-size:1.25rem;color:{C64_COLORS['white']};"
        "text-transform:uppercase;letter-spacing:0.08em"
    ),
    "paragraph": (
        f"margin:0 0 1rem;color:{C64_COLORS['text_body']};font-size:0.98rem"
    ),
    "paragraph_strong": f"color:{C64_COLORS['white']}",
    "paragraph_em": f"color:{C64_COLORS['emphasis']};font-style:normal",
    "image": (
        "display:block;width:100%;height:auto;border-radius:2px;"
        f"border:2px solid {C64_COLORS['border']};box-shadow:{C64_COLORS['shadow_image']}"
    ),
    "image_container": (
        "position:relative;border-radius:2px;overflow:hidden;"
        f"margin-bottom:0.6rem;background:#000;box-shadow:{C64_COLORS['shadow_image']}"
    ),
    "image_caption": (
        f"font-size:0.8rem;color:{C64_COLORS['text_muted']};"
        "text-align:center;font-style:italic;margin:5px 0 20px 0"
    ),
    "blockquote": (
        f"margin:2.5rem 0 2.25rem;padding:1.5rem 1.6rem;"
        f"border-left:4px solid {C64_COLORS['accent']};"
        f"background:{C64_COLORS['bg_quote']};"
        f"font-style:italic;color:{C64_COLORS['white']};"
        "border-radius:2px;position:relative;overflow:hidden"
    ),
    "blockquote_mark": (
        "position:absolute;top:-26px;right:12px;font-size:4.5rem;"
        "color:rgba(160,160,255,0.1);font-style:normal"
    ),
    "milestones_section": (
        f"margin:0 0 2.25rem;padding:1.5rem 1.7rem 1.7rem;"
        f"background-color:{C64_COLORS['bg_card']};"
        f"border-radius:4px;border:2px solid {C64_COLORS['border']}"
    ),
    "milestones_list": (
        f"line-height:1.7;margin:0;padding-left:1.1rem;"
        f"font-size:0.95rem;color:{C64_COLORS['text_body']}"
    ),
    "milestones_bold": f"color:{C64_COLORS['white']}",
    "works_grid": (
        "display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));"
        "gap:1.1rem;margin-top:0.5rem"
    ),
    "works_card": (
        f"background:{C64_COLORS['bg_card_gradient']};"
        f"border-radius:4px;padding:0.9rem 0.9rem 1rem;"
        f"border:2px solid {C64_COLORS['border_light']};"
        f"box-shadow:{C64_COLORS['shadow_card']}"
    ),
    "works_card_title": (
        f"font-weight:700;font-size:0.98rem;color:{C64_COLORS['white']};"
        "margin:0 0 0.15rem;text-transform:uppercase"
    ),
    "works_card_subtitle": (
        f"font-size:0.8rem;color:{C64_COLORS['text_secondary']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.35rem"
    ),
    "works_card_body": (
        f"font-size:0.9rem;color:{C64_COLORS['text_body']};margin:0"
    ),
    "closing_tribute": "text-align:center;margin-top:2.4rem",
    "closing_tribute_text": (
        f"font-weight:600;font-size:1.02rem;color:{C64_COLORS['white']};"
        "margin-bottom:0.6rem"
    ),
    "closing_tribute_stars": (
        f"font-family:'Courier New',monospace;font-size:0.78rem;"
        f"letter-spacing:0.16em;text-transform:uppercase;color:{C64_COLORS['accent']};"
        "opacity:0.9"
    ),
    "links_section": (
        f"margin-top:2rem;padding-top:1.5rem;"
        f"border-top:2px solid {C64_COLORS['border']}"
    ),
    "links_heading": (
        f"font-size:0.85rem;color:{C64_COLORS['text_muted']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.6rem"
    ),
    "link": f"color:{C64_COLORS['accent']};text-decoration:underline",
    "rip_section": (
        f"text-align:center;margin:2.8rem auto 2rem;padding:1.8rem 1rem;"
        f"background:{C64_COLORS['bg_rip']};"
        f"border:2px solid {C64_COLORS['border']};"
        f"border-radius:4px;max-width:720px;box-shadow:{C64_COLORS['shadow_rip']}"
    ),
    "rip_heading": (
        f"font-size:2.1rem;margin:0;color:{C64_COLORS['white']};"
        "font-weight:600;letter-spacing:0.03em"
    ),
    "rip_subtitle": (
        f"margin-top:1rem;font-size:0.95rem;color:{C64_COLORS['text_muted']};"
        "letter-spacing:0.08em;text-transform:uppercase"
    ),
    "video_embed": (
        "position:relative;padding-bottom:56.25%;height:0;"
        "overflow:hidden;max-width:100%;margin:20px 0"
    ),
}


# ── Amiga Demo Preset ────────────────────────────────────────

AMIGA_COLORS = {
    "bg_main_gradient": "linear-gradient(180deg,#1a1a2e 0%,#16213e 40%,#0f3460 100%)",
    "bg_card": "rgba(15,52,96,0.7)",
    "bg_card_gradient": "linear-gradient(180deg,rgba(30,60,114,0.9),rgba(15,30,60,0.95))",
    "bg_quote": "linear-gradient(120deg,rgba(255,165,0,0.1),rgba(30,60,114,0.25))",
    "bg_rip": "linear-gradient(135deg,rgba(26,26,46,0.92),rgba(15,52,96,0.9))",
    "text_primary": "#e0e0ff",
    "text_body": "#d0d0f0",
    "text_secondary": "#a0a0d0",
    "text_muted": "#9090b0",
    "white": "#ffffff",
    "emphasis": "#ffa500",
    "accent": "#ff6600",
    "accent_copper": "#ff8c00",
    "accent_light": "#ffb347",
    "border": "rgba(255,140,0,0.4)",
    "border_light": "rgba(255,160,0,0.5)",
    "shadow_main": "0 22px 40px rgba(0,0,30,0.6)",
    "shadow_card": "0 12px 20px rgba(0,0,30,0.7),0 0 10px rgba(255,140,0,0.15)",
    "shadow_image": "0 8px 18px rgba(0,0,30,0.7)",
    "shadow_rip": "0 12px 28px rgba(0,0,30,0.5)",
    "flower_url": "https://amigac64.wordpress.com/wp-content/uploads/2015/04/flower6.png",
}

AMIGA_STYLES = {
    "wrapper": (
        f"max-width:880px;margin:0 auto 4rem auto;padding:2.5rem 2rem 3rem;"
        f"font-family:system-ui,-apple-system,sans-serif;line-height:1.8;color:{AMIGA_COLORS['text_primary']};"
        f"background:{AMIGA_COLORS['bg_main_gradient']};"
        f"border-radius:12px;border:1px solid {AMIGA_COLORS['border']};"
        f"box-shadow:{AMIGA_COLORS['shadow_main']};position:relative;overflow:hidden"
    ),
    "memorial_header": (
        "text-align:center;margin-bottom:2rem;position:relative;z-index:1;"
        f"border-bottom:2px solid {AMIGA_COLORS['border']};padding-bottom:1.5rem"
    ),
    "person_name": (
        f"font-size:2.2rem;margin:0 0 0.4rem;letter-spacing:0.04em;"
        f"color:{AMIGA_COLORS['white']};"
        f"text-shadow:0 0 20px rgba(255,140,0,0.3)"
    ),
    "person_handle": (
        f"font-size:0.98rem;font-weight:600;letter-spacing:0.2em;"
        f"text-transform:uppercase;color:{AMIGA_COLORS['accent_light']};margin:0"
    ),
    "person_dates": (
        f"font-size:0.95rem;font-weight:600;letter-spacing:0.12em;"
        f"text-transform:uppercase;color:{AMIGA_COLORS['text_secondary']};margin:0"
    ),
    "section_heading": (
        f"margin:0 0 0.85rem;font-size:1.25rem;color:{AMIGA_COLORS['accent_light']}"
    ),
    "paragraph": (
        f"margin:0 0 1rem;color:{AMIGA_COLORS['text_body']};font-size:0.98rem"
    ),
    "paragraph_strong": f"color:{AMIGA_COLORS['white']}",
    "paragraph_em": f"color:{AMIGA_COLORS['emphasis']};font-style:normal",
    "image": (
        "display:block;width:100%;height:auto;border-radius:8px;"
        f"border:1px solid {AMIGA_COLORS['border']};box-shadow:{AMIGA_COLORS['shadow_image']}"
    ),
    "image_container": (
        "position:relative;border-radius:8px;overflow:hidden;"
        f"margin-bottom:0.6rem;background:#000;box-shadow:{AMIGA_COLORS['shadow_image']}"
    ),
    "image_caption": (
        f"font-size:0.8rem;color:{AMIGA_COLORS['text_muted']};"
        "text-align:center;font-style:italic;margin:5px 0 20px 0"
    ),
    "blockquote": (
        f"margin:2.5rem 0 2.25rem;padding:1.5rem 1.6rem;"
        f"border-left:4px solid {AMIGA_COLORS['accent_copper']};"
        f"background:{AMIGA_COLORS['bg_quote']};"
        f"font-style:italic;color:{AMIGA_COLORS['white']};"
        "border-radius:8px;position:relative;overflow:hidden"
    ),
    "blockquote_mark": (
        "position:absolute;top:-26px;right:12px;font-size:4.5rem;"
        "color:rgba(255,140,0,0.08);font-style:normal"
    ),
    "milestones_section": (
        f"margin:0 0 2.25rem;padding:1.5rem 1.7rem 1.7rem;"
        f"background-color:{AMIGA_COLORS['bg_card']};"
        f"border-radius:10px;border:1px solid {AMIGA_COLORS['border']}"
    ),
    "milestones_list": (
        f"line-height:1.7;margin:0;padding-left:1.1rem;"
        f"font-size:0.95rem;color:{AMIGA_COLORS['text_body']}"
    ),
    "milestones_bold": f"color:{AMIGA_COLORS['accent_light']}",
    "works_grid": (
        "display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));"
        "gap:1.1rem;margin-top:0.5rem"
    ),
    "works_card": (
        f"background:{AMIGA_COLORS['bg_card_gradient']};"
        f"border-radius:10px;padding:0.9rem 0.9rem 1rem;"
        f"border:1px solid {AMIGA_COLORS['border_light']};"
        f"box-shadow:{AMIGA_COLORS['shadow_card']}"
    ),
    "works_card_title": (
        f"font-weight:700;font-size:0.98rem;color:{AMIGA_COLORS['white']};"
        "margin:0 0 0.15rem"
    ),
    "works_card_subtitle": (
        f"font-size:0.8rem;color:{AMIGA_COLORS['accent_light']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.35rem"
    ),
    "works_card_body": (
        f"font-size:0.9rem;color:{AMIGA_COLORS['text_body']};margin:0"
    ),
    "closing_tribute": "text-align:center;margin-top:2.4rem",
    "closing_tribute_text": (
        f"font-weight:600;font-size:1.02rem;color:{AMIGA_COLORS['white']};"
        "margin-bottom:0.6rem"
    ),
    "closing_tribute_stars": (
        f"font-family:'Courier New',monospace;font-size:0.78rem;"
        f"letter-spacing:0.16em;text-transform:uppercase;color:{AMIGA_COLORS['accent']};"
        "opacity:0.9"
    ),
    "links_section": (
        f"margin-top:2rem;padding-top:1.5rem;"
        f"border-top:1px solid {AMIGA_COLORS['border']}"
    ),
    "links_heading": (
        f"font-size:0.85rem;color:{AMIGA_COLORS['text_muted']};"
        "text-transform:uppercase;letter-spacing:0.12em;margin:0 0 0.6rem"
    ),
    "link": f"color:{AMIGA_COLORS['accent_light']};text-decoration:underline",
    "rip_section": (
        f"text-align:center;margin:2.8rem auto 2rem;padding:1.8rem 1rem;"
        f"background:{AMIGA_COLORS['bg_rip']};"
        f"border:1px solid {AMIGA_COLORS['border']};"
        f"border-radius:12px;max-width:720px;box-shadow:{AMIGA_COLORS['shadow_rip']}"
    ),
    "rip_heading": (
        f"font-size:2.1rem;margin:0;color:{AMIGA_COLORS['accent_light']};"
        "font-weight:600;letter-spacing:0.03em"
    ),
    "rip_subtitle": (
        f"margin-top:1rem;font-size:0.95rem;color:{AMIGA_COLORS['text_muted']};"
        "letter-spacing:0.08em;text-transform:uppercase"
    ),
    "video_embed": (
        "position:relative;padding-bottom:56.25%;height:0;"
        "overflow:hidden;max-width:100%;margin:20px 0"
    ),
}


# ── Preset Registry ──────────────────────────────────────────

PRESETS = {
    "default": {"styles": POST_STYLES, "colors": COLORS},
    "c64": {"styles": C64_STYLES, "colors": C64_COLORS},
    "amiga": {"styles": AMIGA_STYLES, "colors": AMIGA_COLORS},
}

PRESET_DESCRIPTIONS = {
    "default": "Dark cinematic theme with radial gradients and glassmorphic borders",
    "c64": "Commodore 64 retro theme — iconic C64 blue (#4040e0), PETSCII-inspired borders, 8-bit aesthetic",
    "amiga": "Amiga demo scene theme — deep blue gradients with copper/orange accents, 1980s innovation feel",
}


def get_styles_for_preset(preset="default"):
    """Return the styles dict for a given preset name."""
    return PRESETS.get(preset, PRESETS["default"])["styles"]


def get_colors_for_preset(preset="default"):
    """Return the colors dict for a given preset name."""
    return PRESETS.get(preset, PRESETS["default"])["colors"]


def get_style(element_name):
    """Get inline style string for an element."""
    return POST_STYLES.get(element_name, "")


def wrap_with_style(html, element_name, tag="div"):
    """Wrap HTML content with a styled element."""
    style = get_style(element_name)
    return f'<{tag} style="{style}">{html}</{tag}>'


def get_template_html(preset="default"):
    """Return the full styled HTML template with placeholder tokens."""
    S = get_styles_for_preset(preset)
    C = get_colors_for_preset(preset)
    return f'''<section style="{S['wrapper']}">

  <!-- Memorial Header -->
  <header style="{S['memorial_header']}">
    <h1 style="{S['person_name']}">In Memory of [Name]</h1>
    <p style="{S['person_handle']}">
      [Year of birth] &ndash; [Year of passing] &middot; [Handle] / [Group] &middot; [Role]
    </p>
  </header>

  <!-- Biography -->
  <div style="margin-bottom:2rem;position:relative;z-index:1">
    <article>
      <p style="{S['paragraph']}">
        <strong style="{S['paragraph_strong']}">[Name] ([Year] &ndash; [Year]) was a [role] in the [demoscene/retro computing] community.</strong>
        [Opening paragraph about the person and their significance.]
      </p>
      <p style="{S['paragraph']}">[Their early scene days, groups, and contributions.]</p>
      <p style="{S['paragraph']}">[Their notable works — demos, music, art, coding.]</p>
      <p style="{S['paragraph']}">[Their impact on the community and legacy.]</p>
    </article>
  </div>

  <!-- Highlighted Quote -->
  <div style="{S['blockquote']}">
    <span style="{S['blockquote_mark']}">&ldquo;</span>
    [A meaningful quote about or from the person, or a tribute from the community.]
  </div>

  <!-- Key Milestones -->
  <section style="{S['milestones_section']}">
    <h2 style="{S['section_heading']}">Key Milestones</h2>
    <ul style="{S['milestones_list']}">
      <li><strong style="{S['milestones_bold']}">[Year]:</strong> [Milestone description]</li>
      <li><strong style="{S['milestones_bold']}">[Year]:</strong> [Milestone description]</li>
      <li><strong style="{S['milestones_bold']}">[Year]:</strong> [Milestone description]</li>
    </ul>
  </section>

  <!-- Works / Releases Grid -->
  <section style="margin-bottom:2.25rem">
    <h2 style="{S['section_heading']}">Notable Works &amp; Releases</h2>
    <div style="{S['works_grid']}">
      <div style="{S['works_card']}">
        <div style="{S['works_card_title']}">[Demo/Release Name]</div>
        <div style="{S['works_card_subtitle']}">[Year] &middot; [Type]</div>
        <p style="{S['works_card_body']}">[Short description of the work.]</p>
      </div>
      <div style="{S['works_card']}">
        <div style="{S['works_card_title']}">[Demo/Release Name]</div>
        <div style="{S['works_card_subtitle']}">[Year] &middot; [Type]</div>
        <p style="{S['works_card_body']}">[Short description of the work.]</p>
      </div>
      <div style="{S['works_card']}">
        <div style="{S['works_card_title']}">[Demo/Release Name]</div>
        <div style="{S['works_card_subtitle']}">[Year] &middot; [Type]</div>
        <p style="{S['works_card_body']}">[Short description of the work.]</p>
      </div>
    </div>
  </section>

  <!-- Closing Tribute -->
  <footer style="{S['closing_tribute']}">
    <div style="{S['closing_tribute_text']}">
      [Closing line — e.g. "Their code may rest, but their influence will never fade."]
    </div>
    <div style="{S['closing_tribute_stars']}">
      &#9733; [handle] &middot; forever in our memories &#9733;
    </div>
  </footer>

  <!-- Links -->
  <div style="{S['links_section']}">
    <p style="{S['links_heading']}">Links</p>
    <p style="margin:0 0 6px 0"><a href="https://csdb.dk/scener/?id=XXXX" style="{S['link']}">CSDB Profile</a></p>
    <p style="margin:0 0 6px 0"><a href="https://www.pouet.net/user.php?who=XXXX" style="{S['link']}">Pouet Profile</a></p>
  </div>

</section>

<!-- RIP Section -->
<div style="{S['rip_section']}">
  <h2 style="{S['rip_heading']}">
    <em>Rest in Peace<br>[Name]</em>
  </h2>
  <img src="{C['flower_url']}" style="width:85px;margin-top:1rem;opacity:0.9" alt="Flower tribute">
  <p style="{S['rip_subtitle']}">
    [Year of birth] &ndash; [Year of passing] &middot; Forever in Our Memories
  </p>
</div>'''
