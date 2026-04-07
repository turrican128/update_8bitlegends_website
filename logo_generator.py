"""
Logo generator using demoscene font spritesheets from logo-o-matic.
Renders handle text as a retro C64/Amiga-style PNG logo.
"""

import json
import base64
import io
import os
import random
from PIL import Image

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONTS_JSON = os.path.join(FONTS_DIR, "fonts.json")
SPRITESHEETS_DIR = os.path.join(FONTS_DIR, "spritesheets")

_font_data = None
_spritesheet_cache = {}


def _load_font_data():
    global _font_data
    if _font_data is None:
        with open(FONTS_JSON, "r") as f:
            _font_data = json.load(f)
    return _font_data


def _load_spritesheet(font_name):
    if font_name not in _spritesheet_cache:
        path = os.path.join(SPRITESHEETS_DIR, f"{font_name}.png")
        _spritesheet_cache[font_name] = Image.open(path).convert("RGBA")
    return _spritesheet_cache[font_name]


def get_available_fonts():
    """Return list of font names that have both data and spritesheets."""
    data = _load_font_data()
    available = []
    for name in data:
        if os.path.exists(os.path.join(SPRITESHEETS_DIR, f"{name}.png")):
            available.append(name)
    return sorted(available)


def get_font_info(font_name):
    """Return metadata for a font (height, maker, year, format)."""
    data = _load_font_data()
    if font_name not in data:
        return None
    font = data[font_name]
    return {
        "name": font_name,
        "height": font["height"],
        "maker": font.get("maker", ""),
        "year": font.get("year", ""),
        "format": font.get("format", ""),
        "has_spritesheet": os.path.exists(
            os.path.join(SPRITESHEETS_DIR, f"{font_name}.png")
        ),
    }


def render_text(text, font_name, spacing=2):
    """Render text using a demoscene font spritesheet.

    Returns a PIL Image (RGBA) of the rendered text, or None if font unavailable.
    """
    data = _load_font_data()
    if font_name not in data:
        return None

    font = data[font_name]
    chars = font["chars"]
    height = font["height"]
    sheet = _load_spritesheet(font_name)

    # Calculate total width
    total_width = 0
    valid_chars = []
    for ch in text.lower():
        if ch == " ":
            # Space = half the height
            total_width += height // 2
            valid_chars.append((" ", 0, height // 2))
        elif ch in chars:
            x_offset, char_width = chars[ch]
            total_width += char_width + spacing
            valid_chars.append((ch, x_offset, char_width))
        # Skip unsupported characters silently

    if not valid_chars:
        return None

    # Remove trailing spacing
    total_width -= spacing

    # Create output image (transparent background)
    output = Image.new("RGBA", (total_width, height), (0, 0, 0, 0))

    # Composite each character
    x_pos = 0
    for ch, x_offset, char_width in valid_chars:
        if ch == " ":
            x_pos += char_width
            continue

        # Crop character from spritesheet
        char_img = sheet.crop((x_offset, 0, x_offset + char_width, height))
        output.paste(char_img, (x_pos, 0), char_img)
        x_pos += char_width + spacing

    return output


def generate_handle_logo(handle, font_name=None, max_width=880, padding=20):
    """Generate a logo PNG for a handle, returned as a base64 data URI.

    Args:
        handle: The text to render
        font_name: Specific font name, or None for random
        max_width: Maximum width of the output image
        padding: Padding around the text

    Returns:
        dict with 'data_uri' (base64 PNG), 'font_name', 'width', 'height'
        or None if generation fails
    """
    available = get_available_fonts()
    if not available:
        return None

    if font_name and font_name in available:
        chosen_font = font_name
    elif font_name:
        # Font requested but not available, pick random
        chosen_font = random.choice(available)
    else:
        chosen_font = random.choice(available)

    text_img = render_text(handle, chosen_font)
    if text_img is None:
        return None

    text_w, text_h = text_img.size

    # Scale down if too wide
    scale = 1.0
    if text_w + padding * 2 > max_width:
        scale = (max_width - padding * 2) / text_w
        new_w = int(text_w * scale)
        new_h = int(text_h * scale)
        text_img = text_img.resize((new_w, new_h), Image.NEAREST)
        text_w, text_h = text_img.size

    # Create final image with dark background
    final_w = text_w + padding * 2
    final_h = text_h + padding * 2
    final = Image.new("RGBA", (final_w, final_h), (10, 11, 18, 255))

    # Center the text
    x = padding
    y = padding
    final.paste(text_img, (x, y), text_img)

    # Convert to base64 data URI
    buffer = io.BytesIO()
    final.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "data_uri": f"data:image/png;base64,{b64}",
        "font_name": chosen_font,
        "width": final_w,
        "height": final_h,
    }


def generate_logo_png(handle, font_name=None, max_width=880, padding=20):
    """Generate a logo and return raw PNG bytes (for Flask routes)."""
    available = get_available_fonts()
    if not available:
        return None, None

    if font_name and font_name in available:
        chosen_font = font_name
    else:
        chosen_font = random.choice(available) if not font_name else available[0]

    text_img = render_text(handle, chosen_font)
    if text_img is None:
        return None, None

    text_w, text_h = text_img.size
    if text_w + padding * 2 > max_width:
        scale = (max_width - padding * 2) / text_w
        text_img = text_img.resize(
            (int(text_w * scale), int(text_h * scale)), Image.NEAREST
        )
        text_w, text_h = text_img.size

    final_w = text_w + padding * 2
    final_h = text_h + padding * 2
    final = Image.new("RGBA", (final_w, final_h), (10, 11, 18, 255))
    final.paste(text_img, (padding, padding), text_img)

    buffer = io.BytesIO()
    final.save(buffer, format="PNG")
    return buffer.getvalue(), chosen_font


if __name__ == "__main__":
    # Quick test
    fonts = get_available_fonts()
    print(f"Available fonts: {len(fonts)}")
    for f in fonts:
        info = get_font_info(f)
        print(f"  {f}: {info['height']}px, by {info['maker']} ({info['year']})")

    result = generate_handle_logo("Street Tuff", font_name="phatfont")
    if result:
        print(f"\nGenerated logo: font={result['font_name']}, "
              f"size={result['width']}x{result['height']}")
        print(f"Data URI length: {len(result['data_uri'])} chars")
    else:
        print("Failed to generate logo")
