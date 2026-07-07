# Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing a full `<html>` document by hand | Write only the `<section>` fragment; let the script wrap it |
| Using `<div>` for everything | Use semantic tags: `<header>`, `<section>`, `<details>`, `<aside>` |
| Burying caveats & tradeoffs inside a file accordion | Pull them into a top-level `<aside class="note">` — they're important context for anyone touching this code later |
| Forgetting `class="impact"` on the table | The default stylesheet only styles `table.impact` — plain `<table>` gets no formatting |
| One massive `<ul>` with all 40 changes | Group by file with `<details>` — one accordion per file |
| Using `style="..."` for everything | Use the semantic classes (`.badge-*`, `.note`) — they come with dark mode support |
| Describing the main feature as disconnected bullet points without showing how pieces connect | Use prose or numbered steps showing the end-to-end flow (trigger → state → output) |
| Listing only what changed without anchoring what stayed the same | End the executive summary paragraph with **Out of scope:** followed by what's not affected |
| Writing impact rows for a pure refactor as if behavior changed | State "no user-facing change" and focus impact on API/developer metrics instead |
| Misreading `\ No newline at end of file` as an EOF fix | Compare both old and new sections of the diff — the marker appears on both sides; neither side may have changed |
| Inline `<style>` blocks in the snippet | The wrapper script injects all styles — never embed `<style>` tags in the snippet |
| Empty `<details>` accordion | If a file has no meaningful changes to list, skip it |
| `<br>` for layout | Use CSS or flexbox instead |
| Nested `<section>` without a parent heading | Each `<section>` should have a logical heading or be preceded by one |
