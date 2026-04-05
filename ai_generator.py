#!/usr/bin/env python3
"""Claude API integration for generating memorial post content."""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from post_generator import generate_post

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are writing memorial posts for 8bitlegends.com, a demoscene memorial site \
honoring Commodore 64 and retro computing legends who have passed away.

Write in a heartfelt but not overly sentimental tone. Use demoscene vocabulary naturally \
(scener, handle, crew/group, demo, intro, crack, SID music, pixel art, etc.).

Structure: Opening announcement, their contributions, personal memories/community impact, \
closing tribute. 3-5 paragraphs. Use markdown formatting (bold for names/handles).

Do NOT invent specific dates, events, or quotes. If you don't know something specific, \
write placeholder text in [brackets] for the user to fill in."""


def generate_memorial_content(name, handle, group, role="coder",
                               contributions="", extra_context=""):
    """Generate enhanced memorial content using Claude."""
    template_draft = generate_post(name, handle, group, role,
                                    contributions or "amazing demos and intros")

    prompt = f"""Write a memorial post for:
- Real name: {name}
- Scene handle: {handle}
- Group/crew: {group}
- Role: {role}
- Known for: {contributions or 'their contributions to the scene'}
{f'- Additional context: {extra_context}' if extra_context else ''}

Here is a template-generated draft for reference (enhance and expand this):
{template_draft['content']}

Write the enhanced memorial post body in markdown. Do not include frontmatter or title."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "content": message.content[0].text,
        "title": template_draft["title"],
        "tags": template_draft["tags"],
    }


def enhance_text(text, instruction="Make this more detailed and heartfelt"):
    """Enhance a selected portion of text."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{instruction}:\n\n{text}"}]
    )
    return message.content[0].text
