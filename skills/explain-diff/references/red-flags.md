# Red Flags & Rationalizations

| Rationalization | Redirect |
|----------------|----------|
| "The diff is small, markdown is fine" | HTML with progressive disclosure is always better for non-terminal audiences. The script makes it zero effort. |
| "The HTML rules are too much for a small diff" | All phases apply regardless of diff size — impact table has fewer rows, caveats may be "None identified." |
| "I can inline all styles since the user won't notice" | Use semantic classes (`.badge-*`, `.note`) — they include dark mode support. The script injects the stylesheet. |
| "This change is simple enough to skip the executive summary" | The executive summary is the first thing stakeholders read. Without it, the review has no anchor. |
| "I'll skip the evolution arc — the stats bar / commit subjects already tell the story" | The arc gives the development sequence at a glance without forcing the reader to reconstruct it from raw hashes and subjects. Only omit for single-commit diffs. |
| "I already explained it in chat" | The HTML document survives beyond the chat. Stakeholders can open, forward, and re-read. |
| "A trailing sentence about scope is fine, the **Out of scope:** marker feels mechanical" | The bold marker makes the boundary scannable in under a second. A plain sentence gets buried. |
| "I don't need the wrapper script / the script path doesn't resolve — I'll hand-write the HTML" | Hand-writing full HTML duplicates the script's work and introduces inconsistency. The script is at `scripts/html_wrap.py` relative to the skill directory; if it truly doesn't exist, stop and inform the user — do not adapt. |
| "I'll put the caveats note inside a file details block" | Pull caveats into a top-level `<aside class="note">` — they're important context for anyone touching this code later. |
| "The summary table takes too long to write" | 3-5 rows take 2 minutes and save readers 10x that in comprehension time. |
| "Caveats section is negative / I don't want to highlight tradeoffs" | The caveats section builds trust. Omitting it makes the review look incomplete. |
| "This merge adds..." (for feature-branch merges) | Use "This branch" or "This change set" — the merge commit didn't do the work. |
