# scripts/

The runtime code that powers the explain-diff skill lives here — SKILL.md instructs agents to call into it.

| File | Role |
|------|------|
| `html_wrap.py` | Wraps an AI-generated HTML snippet into a standalone review document with injected stylesheet, dark-mode support, and optional auto-open. |

This folder is part of the skill's runtime payload. Everything here is reachable at `scripts/<file>` relative to the skill directory.
