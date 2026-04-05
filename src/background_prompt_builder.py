import json


def build_long_background_prompt(topic: str, script_text: str, channel: dict) -> str:
    niche = channel.get("niche", "")
    tone = channel.get("tone", "")
    audience = channel.get("target_audience", "")

    return f"""
Create a cinematic, emotionally resonant background image for a faceless YouTube video.

Topic: {topic}
Niche: {niche}
Tone: {tone}
Audience: {audience}

Requirements:
- No text
- No logos
- No watermarks
- No readable signage
- No split panels or collage
- Clean composition with negative space for captions
- Emotionally fitting for the topic
- Safe for Christian / encouragement content
- High visual quality
- Soft cinematic lighting
- Suitable as a background for a horizontal YouTube video
- Avoid extreme close-up faces
- Prefer symbolic, atmospheric, or scenic imagery over identifiable people

Style:
cinematic, moody, soft light, emotionally uplifting, polished, realistic

Script context:
{script_text[:2000]}
""".strip()


def build_short_background_prompt(title: str, script_text: str, channel: dict) -> str:
    niche = channel.get("niche", "")
    tone = channel.get("tone", "")

    return f"""
Create a cinematic vertical-friendly background image for a faceless short-form video.

Short title: {title}
Niche: {niche}
Tone: {tone}

Requirements:
- No text
- No logos
- No watermarks
- No readable signage
- Clean center composition for captions
- Strong emotional clarity
- Vertical-video friendly composition
- Suitable for TikTok, Instagram Reels, Facebook Reels, and YouTube Shorts
- Avoid extreme close-up faces
- Prefer symbolic, atmospheric, or scenic imagery over identifiable people

Style:
cinematic, dramatic but tasteful, soft lighting, polished, realistic

Short script context:
{script_text[:1200]}
""".strip()
