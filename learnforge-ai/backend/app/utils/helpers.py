"""Utility helpers for LearnForge AI backend."""

import re
import uuid
from pathlib import Path


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix."""
    uid = str(uuid.uuid4()).replace("-", "")[:16]
    return f"{prefix}{uid}" if prefix else uid


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for GCS storage.
    Replaces unsafe characters with underscores.
    """
    name = Path(filename).stem
    ext = Path(filename).suffix
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    return f"{safe}{ext}"


def truncate_text(text: str, max_chars: int = 30000) -> str:
    """Truncate text to stay within Gemini context limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... content truncated ...]"


def format_conversation_history(messages: list[dict]) -> str:
    """Format a list of {role, content} messages into a readable string."""
    lines = []
    for msg in messages[-20:]:  # last 20 messages for context window
        role = "User" if msg.get("role") == "user" else "LearnForge"
        lines.append(f"{role}: {msg.get('content', '')}")
    return "\n".join(lines)
