---
name: explain-diff
description: >
  Use when explaining code changes from git diffs, pull requests, branch
  comparisons, or commit histories to stakeholders who benefit from formatted
  documentation. Use when the output needs progressive disclosure (expandable
  file sections), semantic HTML structure, before/after comparison tables, and
  caveats & tradeoffs asides. Not for raw terminal output or quick inline
  explanations, single-file typos, or trivial config commits.
allowed-tools: Bash(git:*) Bash(python:*) Read Write
metadata:
  author: explain-diff
  version: "1.0.0"
---

# Explain Diff

## Overview

Explain code changes by generating a self-contained HTML document with progressive disclosure — stakeholders can scan the executive summary, expand file details on demand, and immediately see risks. Uses a Python wrapper script to convert an authored HTML snippet into a complete, styled document.

**REQUIRED TOOL:** [`scripts/html_wrap.py`](./scripts/html_wrap.py) (inside this skill directory)

## When to Use

- Presenting PR or commit changes to product managers, QA, or other non-terminal audiences
- Creating shareable artifacts that survive beyond the chat window
- Any situation where the reader needs an executive summary before deciding to drill into file-level details
- The output must be beautiful enough to attach to a ticket or email

**Do NOT use for:**
- One-line commits that need no explanation
- Terminal-only debugging sessions
- Cases where plain Markdown in the chat is sufficient
- Internal engineering notes that will never be shared externally

## Workflow

1. **Analyze the diff** — read commit logs and full diff, categorise each change
2. **Structure the content** — organise into executive summary, impact table, file breakdown, risks
3. **Write the HTML snippet** — author a `<section>` fragment with semantic tags
4. **Wrap with script** — run `html_wrap.py` to produce a complete HTML document
5. **Verify the output** — open in browser, check accordions, table, and caveats aside

### Phase 1 — Analyze the Diff

1. Run `git log --oneline <ref>` to understand commit scope. For merge commits, use `<ref>^` (first parent) as the comparison base. Count only non-merge commits in the branch range — use `git log --oneline --no-merges <ref>^1..<ref>^2` for merge commits. If the count includes merge commits, annotate as `X feature commits (+Y merges)`. Save the commit subjects — they form the evolution arc in the output header.
2. Run `git log --format="--- %h %s%n%b" <range>` to read full commit bodies (description, rationale, ticket links, breaking change notes). On Unix, pipe through `head -200` to limit output; on Windows (PowerShell), use `Select-Object -First 200`.
3. Run `git diff <range>` or `git show --stat <commit>` to see files changed and line counts. For merge commits, diff against the first parent: `git diff <ref>^..<ref>`.
4. Read full diff. Categorise each change:
   - **Feature logic** — new functionality or modified behaviour
   - **Refactor** — restructuring without behaviour change
   - **Revert** — the change undoes previous work; flag in risks
   - **Style/UI** — visual or CSS changes
   - **Bug fix** — defect correction
   - **Infrastructure** — build, config, CI, dependencies

   **Additional checks during diff reading:**
   - For guard/condition changes in async contexts: compare timing semantics of old vs new guard expressions. Could there be a window where neither guard is true but work is still in flight?
   - If the diff includes `\ No newline at end of file` markers, compare both old and new sections before claiming a trailing-newline fix — the marker appears on both sides.

5. **Audit commit history (subjects + bodies) for red flags**:
   - **Reverts** — indicate churn or mistaken approach; investigate and flag in risks
   - **WIP / stash commits** — suggest incomplete work; verify nothing is missing
   - **Missing test commits** — if logic changes but no tests, flag in risks
   - **Merge commits into the feature branch** — normal; just note the branch had to catch up with dev

6. **Check if the diff reaches beyond itself** — for each meaningful change, verify your understanding is complete:

   a. **Import paths changed** — do the new modules still export what the old ones did? If not, the change is incomplete.

   b. **Function/API signature changed** — were all call sites updated? A renamed parameter or reordered argument silently breaks every call site outside the diff.

   c. **Type/interface shape changed** — were all property accesses updated? A removed property on a shared type breaks at runtime even if the diff looks correct in isolation.

   d. **Something was removed** — is anything still referencing it? Safe if unreferenced. A breaking change if references remain.

   e. **Config/environment variable changed** — does every consumer expect the same shape?

   f. **Permission/access-control guard changed** — what is the guard protecting? Could the new logic widen or bypass it?

7. **Gather supplementary context** — Check whether the current session or available documents contain useful information beyond the diff: rationale from discussion, ticket IDs, related changes, deployment notes. Only include context that is directly verifiable (commit body, user statement, referenced document) and relevant. Discard anything that conflicts with the diff or can't be sourced. If nothing is available or verifiable, skip this step — do not fabricate.

### Phase 1.5 — Scan for Risk Signals

For every diff, flag any of these risk signals in the caveats section:

- **New external dependency** — verify it's from a known publisher
- **User input flowing into sensitive operations** — SQL, shell, file paths, HTML output. Check whether it's validated, parameterized, or escaped before use.
- **Authorization or permission logic changed** — role checks, route guards, conditional rendering flags. Could the new logic open a path that was previously closed?
- **Secrets or credentials in the diff** — API keys, tokens, passwords — these should never appear in version control.
- **Rate limiting, CSRF, or validation removed from a handler** — removing safety layers without replacement is a regression, not a refactor.

Skip this phase only for purely cosmetic or documentation diffs.

### Phase 2 — Structure the Content

Organise the explanation into these sections (in order):

| Section | Purpose |
|---------|---------|
| Executive summary | 2-sentence what + why. First line a badge for change scope, followed by a stats bar (files · +N/−M · commits). |
| Impact table | Before-vs-After comparison for key architectural/behavioural metrics. Limit to 3-7 rows — one behavioural difference per row. Prioritize user-facing behavior changes over internal refactors. If stuck, choose rows that answer "what does a user or API consumer notice?" For very small diffs (1 file, <20 lines), 2-4 rows is appropriate. If the diff has no user-facing behavior change (pure refactor, rename, config-only, revert), state that explicitly in the executive summary and focus the impact table on developer-facing metrics (API shape, import paths, build steps). Limit to 2-4 rows. Each row should reference the file(s) that drive the change using `<var>`. |
| Commit evolution | Prose summary of the commit sequence (e.g., `added field → migrated data → removed old logic`). Placed between the stats bar and the `<h2>` in the header as `<p class="evolution-arc">`. Gives the reader the development arc at a glance — no individual hashes. For merge commits, summarize only the feature branch commits (non-merge). |
| File breakdown | One `<details>` accordion per file (or per group of related files) with bulleted change list. Preceded by an architectural layers overview that names which layers were touched (in dependency order). See grouping guidance below. |
| Caveats & Tradeoffs | `<aside class="note">` design decisions made, tradeoffs accepted, alternatives considered, and footguns for future editors touching this code. If a bullet describes intended behavior without a risk angle, it's not a caveat. If no meaningful caveats apply, include the `<aside>` with the text "None identified" — the section must still be present. For very small diffs, limit to 1-2 real caveats — do not manufacture them just to fill space. |

**Executive summary framing for merge commits:** If the diff is from a merge commit that merges a feature branch, begin the executive summary with "This branch" or "This change set" — not "This merge" — to avoid implying one commit did all the work.

Before writing, **group related files by concern**:
- **Pure-propagation passthroughs** (e.g., forwarding a prop through 3 components, or 15 files with the same mechanical import rename) — merge into a single `<details>` accordion. Use `<h3>` sub-headings to separate per-file details.
- **Files with independent logic changes** — each gets its own `<details>` accordion.
- When deciding: if the change is the same mechanical operation repeated across files, merge them. If each file has unique logic changes, keep them separate.
- If supporting files serve entirely different architectural concerns (data layer vs navigation vs configuration), split them or use `<h3>` sub-headings naming each concern explicitly. A generic label like "Supporting layer" invites the reader to skip over an important nav/routing change.
- When a change moves from a computed/view-derived value to a data-source value, call that out explicitly: "This decouples the component from internal computation and ties the behavior to the data model."

For the file with the most significant logic change, describe the end-to-end flow rather than a flat bullet list. Use prose or numbered steps showing the progression (trigger → state transition → side effect → output). Reserve bullets for supporting details.

### Phase 3 — Write the HTML Snippet

Write a fragment beginning with `<section>` — no `<html>`, `<head>`, `<body>` tags. Apply these semantic rules:

```
<section>                              # root wrapper
  <header>                             # executive summary (badge + stats + evolution + h2 + p)
    <span class="badge badge-*">
    <p class="stats">                  # "3 files · +142/−31 · 2 commits"
    <p class="evolution-arc">          # evolution: added field → migrated data → removed old logic
    <h2>
    <p>                                # what changed + why
    <p class="scope-marker">           # **Out of scope:** what stayed the same
  </header>

  <section>                            # impact table
    <table class="impact">
      <thead><tr><th>Metric<th>Before<th>After
      <tbody>
        <tr><td>metric<td>before<td>after (<var>src/file.ts</var>)
  </section>

  <p>Layers affected: data layer &rarr; service layer &rarr; UI</p>

  <section>                            # file breakdown
      <details><summary><var>path</var> <span class="badge badge-info">+N/−M</span>
        <h3>Subsystem name</h3>           # optional: group related changes in large files
        <ul><li>...
    </section>

  <aside class="note">                 # caveats & tradeoffs
    <h3>Caveats &amp; Tradeoffs
    <ul><li>...
  </aside>
</section>
```

The executive summary's description paragraph should be followed by a separate `<p class="scope-marker">` block: `<strong>Out of scope:</strong>` followed by what stayed the same (e.g., "<strong>Out of scope:</strong> Existing chart generation and clearing are unaffected."). This makes the boundary scannable — a cold reader can find it in seconds.

**Impact table — file references:** Append `<var>path/to/file.ts</var>` to each After cell to show which files drive the metric. Use commas for multiple files. This lets the reader cross-reference from "what changed" to "where" without searching.

**Architectural layers overview:** Between the impact table and file breakdown, include a `<p>` summarizing which architecture layers were touched (e.g., "Layers affected: data layer → service layer → UI"). List them in dependency order (deepest first) so the reader builds a mental model of the change's reach before seeing individual files.

**Supplementary context (if gathered):** Weave small references (ticket links, rationale) into the executive summary paragraph. Place substantial context (related PR summary, deployment note) after the caveats section as a plain `<p>`, prefixed with an italic source label — e.g., `<em>From session:</em>`, `<em>From commit body:</em>`, `<em>From design doc:</em>` — so the reader can assess provenance at a glance.

**Badge colour conventions (PR scope header badge):**

| Scope | Class |
|-------|-------|
| Breaking / major rewrite | `badge badge-danger` |
| New feature | `badge badge-success` |
| Refactor | `badge badge-info` |
| Mixed | `badge badge-warning` |
| Bug fix / dependency | `badge badge-neutral` |

Prefer `badge-info` as a safe default for file-level badges. Avoid `badge-danger` at file level — it is reserved for the PR scope header. If a file is purely additive (all new feature code), `badge-success` may be more informative than a neutral badge.

For files with additions only (no deletions), state explicitly in the description: "All N lines are new — existing styles were untouched."

**Semantic tag mapping:**

| Purpose | Tag | Required Attributes |
|---------|-----|---------------------|
| Executive summary header | `<header>` | — |
| Stats bar | `<p class="stats">` | `class="stats"` |
| Commit evolution arc | `<p class="evolution-arc">` | `class="evolution-arc"` |
| Section heading | `<h2>` | — |
| Sub-heading | `<h3>` | — |
| Paragraph | `<p>` | — |
| Impact table | `<table class="impact">` | `class="impact"` |
| File accordion | `<details>` | — |
| File path label | `<summary><var>path</var></summary>` | — |
| Change list | `<ul><li>` | — |
| Caveats callout | `<aside class="note">` | `class="note"` |
| Caveats heading | `<h3>` | — |

**Inline element usage:**
- `<var>` for file paths, function names, variable names
- `<kbd>` for terminal commands, config values, literal constants
- `<code>` for inline code snippets (use `<pre><code>` for blocks)
- `<strong>` for emphasised concepts in bullet lists
- `<details><summary>` per file — never flatten all changes into one big list

### Phase 4 — Wrap with Script

The wrapper script is at [`scripts/html_wrap.py`](./scripts/html_wrap.py) (relative to this skill directory). Construct the full absolute path by joining the skill directory with `scripts/html_wrap.py`.

```bash
python scripts/html_wrap.py snippet.html -o output.html --title "PR Review — <ref>"
```

**If the script does not exist at the resolved absolute path:** inform the user and stop — do NOT hand-write a full `<html>` document as fallback. The `"I can't find the script, I'll just write the HTML directly"` rationalization is a Red Flag — you must stop, not adapt.

The script:
- Injects a `<meta viewport>`, `<title>`, and default stylesheet
- Supports `--style path/to.css` for custom themes (replaces the default stylesheet entirely — you must include all base styles + dark mode variant or they will be lost)
- Supports `--append-style path/to.css` to layer custom styles on top of defaults (additive, does not replace anything)
- Supports `--open` to open the output file in the default browser (requires `-o`)
- Forwards stdin/stdout for pipe workflows: `cat snippet.html | python html_wrap.py - > out.html`

**Dark mode compatibility:** The default stylesheet includes `@media (prefers-color-scheme: dark)`. If you use `--style` to replace it, your custom CSS must include a dark mode variant.

### Phase 5 — Verify the Output

**Structural checks:**
- Open the HTML file in a browser.
- Confirm the executive summary reads correctly without expanding anything.
- Confirm the badge class matches the change scope (see badge colour conventions).
- Click every `<details>` accordion — each opens and closes.
- Confirm `<aside class="note">` renders with the blue left border.
- Confirm the `<table class="impact">` columns align.
- Does the evolution arc accurately summarize the commit sequence?
- Does the architectural layers overview (below the impact table) correctly name the affected layers in dependency order?
- Does every impact cell that references a file use `<var>` and match an existing accordion?

**Content-quality checks:**
- Does every impact row contrast exactly **one** behavioral or architectural difference?
- Is every caveat a real risk, downside, or future-edit footgun (not happy-path description)?
- Does the first sentence of the executive summary make sense on its own?
- Are any red flags from the commit audit (reverts, missing tests) reflected in the caveats section?
- Does the primary feature description explain the mechanism or flow, not just a checklist of added pieces?
- Does the executive summary anchor scope with an **Out of scope:** marker stating what stayed the same?
- **Permission/access-control scan:** Check if the diff contains permission or access-control changes (role checks, route guards, conditional rendering flags). Even 1–2 line changes here often carry more behavioral weight than their diff size suggests.
- **Accessibility scan:** If the diff introduces CSS transitions or animations, verify the output includes or acknowledges `@media (prefers-reduced-motion: reduce)` support.
- **Fact-check pass:** Re-read the diff to verify: file paths, line counts, variable names, code snippets, numeric counts, and formatting strings in the impact table and caveats are accurate. If a caveat references a specific constant or value, confirm it exists in the diff.

## Quick Reference

```bash
# Basic workflow
git log --oneline HEAD~3..HEAD > /tmp/commits.txt
git log --format="--- %h %s%n%b" HEAD~3..HEAD > /tmp/commit-bodies.txt
git diff HEAD~3..HEAD > /tmp/diff.txt

# Merge commit: feature branch commits (non-merge only)
git log --oneline --no-merges <ref>^1..<ref>^2 > /tmp/commits.txt

# Merge commit: full diff against first parent
git diff <ref>^..<ref> > /tmp/diff.txt

# Generate snippet → wrap → open
python scripts/html_wrap.py /tmp/snippet.html -o review.html --title "PR Review"
python scripts/html_wrap.py /tmp/snippet.html -o review.html --open
```

**Evolution arc:** From the saved commit subjects, produce a `→`-separated summary (e.g., `added field → migrated data → removed old logic`). Place it between the stats bar and `<h2>` as `<p class="evolution-arc">`. Omit for single-commit diffs.

**Out of scope:** Follow the description paragraph with `<p class="scope-marker"><strong>Out of scope:</strong> ...</p>` listing what stayed the same.

## Common Mistakes

See [`references/common-mistakes.md`](./references/common-mistakes.md) for the full catalog. The most important rule: always write a `<section>` fragment — never a full `<html>` document. The wrapper script handles the shell.

## Red Flags & Rationalizations

See [`references/red-flags.md`](./references/red-flags.md). The core rule: if the wrapper script doesn't exist at the expected path, stop and inform the user — do not hand-write a full HTML document.
