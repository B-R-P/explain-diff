---
name: explain-diff
description: >
  Use ONLY when the user explicitly asks for a self-contained HTML document
  explaining a git diff, PR, or commit history — e.g. requests mentioning
  "HTML report", "shareable doc", or an artifact to attach to a ticket/email.
  Do NOT use for plain diff summaries, branch overviews, or review requests
  where a chat/markdown answer suffices.
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

The last two are the important guardrails — a model-invoked skill must not fire on trivial or ephemeral requests.

## Tone — Ask the User First

Before writing anything, ask the user which tone the HTML should use. Offer these options (put the recommended one first and append " (Recommended)"):

- **Highly technical, understandable** (recommended) — keeps real function names, APIs, and mechanism detail, but written so a smart non-author can follow; every term that matters is explained in context.
- **Deeply technical** — assumes a working engineer audience; raw symbols, exact call flows, tradeoffs in full detail; minimal translation to plain language.
- **Accessible / business-focused** — leads with user-facing impact, minimizes code identifiers, uses plain-language descriptions and analogies.

**The same change, all three tones** — the calibration target for every section:

> **Deeply technical:** `processPayment()` is split into `validateCart()` → `chargeCustomer()` → `createOrder()`. The old single-function path caught `PaymentError` internally and returned `{ success: false }`; the split path lets `chargeCustomer()` throw, so callers that relied on the return shape will now see uncaught exceptions.
> **Highly technical, understandable:** `processPayment()` is now three separate steps: validate the cart, charge the customer, then create the order. Before, all three ran inside one function and errors were swallowed into a `success: false` return. Now the charge step throws exceptions, so code that checked the return value needs to catch errors instead.
> **Accessible / business-focused:** The checkout flow is now three stages — cart validation, payment, and order creation. Previously, payment failures were silently absorbed; now they surface as clear errors, so automation that depended on the old flat response needs updating.

Hold the chosen register across every section — executive summary, impact table, file breakdown, and caveats. If the user declines to choose, default to **highly technical, understandable**.

## Workflow

1. **Confirm the tone** — ask the user which tone the HTML should use (see [Tone — Ask the User First](#tone--ask-the-user-first)); default if they decline
2. **Analyze the diff** — read commit logs and full diff, categorise each change
3. **Structure the content** — organise into executive summary, impact table, file breakdown, risks
4. **Write the HTML snippet** — author a `<section>` fragment with semantic tags
5. **Wrap with script** — run `html_wrap.py` to produce a complete HTML document
6. **Verify the output** — open in browser, check `<details>` accordions, table, and caveats aside

### Phase 1 — Analyze the Diff

1. Run `git log --oneline <ref>` to understand commit scope. For merge commits, use `<ref>^` (first parent) as the comparison base. Count only non-merge commits in the branch range — use `git log --oneline --no-merges <ref>^1..<ref>^2` for merge commits. If the count includes merge commits, annotate as `X feature commits (+Y merges)`. Save the commit subjects to a file (e.g. `git log --oneline <range> > commits.txt`) — they form the evolution arc in the output header.
2. Run `git log --format="--- %h %s%n%b" <range>` to read full commit bodies (description, rationale, ticket links, breaking change notes), saving to a file (e.g. `> commit-bodies.txt`). On Unix, pipe through `head -200` to limit output; on Windows (PowerShell), use `Select-Object -First 200`.
3. Run `git diff <range>` or `git show --stat <commit>` to see files changed and line counts, saving the full diff to a file (e.g. `> diff.txt`). For merge commits, diff against the first parent: `git diff <ref>^..<ref>`.
4. Read full diff. For files exceeding +200 lines, read imports and exports first to understand dependencies, then scan logical section breaks (component sub-headings, `if`/`switch` branches) before writing the breakdown. Categorise each change:
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

8. **Scan for risk signals** — flag any of these in the caveats section:
   - **New external dependency** — verify it's from a known publisher
   - **User input flowing into sensitive operations** — SQL, shell, file paths, HTML output. Check whether it's validated, parameterized, or escaped before use.
   - **Authorization or permission logic changed** — role checks, route guards, conditional rendering flags. Could the new logic open a path that was previously closed?
   - **Secrets or credentials in the diff** — API keys, tokens, passwords — these should never appear in version control.
   - **Rate limiting, CSRF, or validation removed from a handler** — removing safety layers without replacement is a regression, not a refactor.

   Skip this scan only for purely cosmetic or documentation diffs.

**Phase 1 is complete when:** every change is categorised, the beyond-itself checks above pass, and risk signals and supplementary context are either captured or explicitly skipped.

### Phase 2 — Structure the Content

Organise the explanation into these sections (in order):

| Section | Purpose |
|---------|---------|
| Executive summary | 2-sentence what + why. First line a badge for change scope, followed by a stats bar (files · +N/−M · commits). |
| Impact table | Before-vs-After comparison for key architectural/behavioural metrics. Limit to 3-7 rows — one behavioural difference per row. Prioritize user-facing behavior changes over internal refactors. If stuck, choose rows that answer "what does a user or API consumer notice?" For very small diffs (1 file, <20 lines), 2-4 rows is appropriate. If the diff has no user-facing behavior change (pure refactor, rename, config-only, revert), state that explicitly in the executive summary and focus the impact table on developer-facing metrics (API shape, import paths, build steps). Limit to 2-4 rows. Each row references the files that drive the change (the `<var>` syntax is specified in Phase 3). |
| Commit evolution | Prose summary of the commit sequence (e.g., `added field → migrated data → removed old logic`). Placed between the stats bar and the `<h2>` in the header as `<p class="evolution-arc">`. Gives the reader the development arc at a glance — no individual hashes. For merge commits, summarize only the feature branch commits (non-merge). |
| File breakdown | One `<details>` per file (or per group of related files) with bulleted change list. Preceded by an architectural layers overview that names which layers were touched (in dependency order). See grouping guidance below. |
| Caveats & Tradeoffs | `<aside class="note">` design decisions made, tradeoffs accepted, alternatives considered, and footguns for future editors touching this code. If a bullet describes intended behavior without a risk angle, it's not a caveat. For each caveat, ask: what happens when the assumption breaks? Surface failure modes and edge cases, not just maintenance inconvenience. If no meaningful caveats apply, include the `<aside>` with the text "None identified" — the section must still be present. For very small diffs, limit to 1-2 real caveats — do not manufacture them just to fill space. |

**Executive summary framing for merge commits:** If the diff is from a merge commit that merges a feature branch, begin the executive summary with "This branch" or "This change set" — not "This merge" — to avoid implying one commit did all the work.

Before writing, **group related files by concern**:
- **Pure-propagation passthroughs** (e.g., forwarding a prop through 3 components, or 15 files with the same mechanical import rename) — merge into a single `<details>`. Use `<h3>` sub-headings to separate per-file details.
- **Files with independent logic changes** — each gets its own `<details>`.
- When deciding: if the change is the same mechanical operation repeated across files, merge them. If each file has unique logic changes, keep them separate.
- If supporting files serve entirely different architectural concerns (data layer vs navigation vs configuration), split them or use `<h3>` sub-headings naming each concern explicitly. A generic label like "Supporting layer" invites the reader to skip over an important nav/routing change.
- When a change moves from a computed/view-derived value to a data-source value, call that out explicitly: "This decouples the component from internal computation and ties the behavior to the data model."

For the file with the most significant logic change, describe the end-to-end flow rather than a flat bullet list. Use prose or numbered steps showing the progression (trigger → state transition → side effect → output). Reserve bullets for supporting details.

**Exclusive accordions:** Give every file accordion the same `name="file-breakdown"` attribute. Opening one closes the others — keeps the file breakdown short on large PRs. The impact table's file references (`href="#file-N"`) jump straight to that accordion even when it's collapsed.

**Phase 2 is complete when:** every section is planned in order, files are grouped (merged only for pure-propagation passthroughs), and the most significant change has an identified end-to-end flow.

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
      <thead><tr><th scope="col">Metric</th><th scope="col">Before</th><th scope="col">After</th></tr></thead>
      <tbody>
        <tr><td>metric</td><td>before</td><td>after (<var><a href="#file-1">src/file.ts</a></var>)</td></tr>
      </tbody>
    </table>
  </section>

  <p>Layers affected: data layer &rarr; service layer &rarr; UI</p>

  <section>                            # file breakdown
      <details id="file-1" name="file-breakdown"><summary><var>path</var> <span class="badge badge-info">+N/−M</span></summary>
        <h3>Subsystem name</h3>           # optional: group related changes in large files
        <ul><li>...
    </details>
    </section>

  <aside class="note">                 # caveats & tradeoffs
    <h3>Caveats &amp; Tradeoffs</h3>
    <ul><li>...
  </aside>
</section>
```

The executive summary's description paragraph should be followed by a separate `<p class="scope-marker">` block: `<strong>Out of scope:</strong>` followed by what stayed the same (e.g., "<strong>Out of scope:</strong> Existing chart generation and clearing are unaffected."). This makes the boundary scannable — a cold reader can find it in seconds.

**Impact table — file references:** Append `<var><a href="#file-N">path/to/file.ts</a></var>` to each After cell to show which files drive the metric. Use commas for multiple files. Give each file accordion a matching `id="file-N"` so the references are clickable — this lets the reader jump from "what changed" to "where" without searching.

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

File-level badges: `badge-danger` is never used at file level — it is reserved for the PR scope header. Use `badge-success` for purely additive files (all new feature code), `badge-info` for refactors (the safe default), `badge-neutral` for removals, config, dependencies, and mechanical changes, and `badge-warning` for high bidirectional churn.

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
| File accordion | `<details>` | `id="file-N"` |
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

The wrapper script is the REQUIRED TOOL named in Overview — `scripts/html_wrap.py` relative to this skill directory.

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

Run through every check below; each must pass before the output is complete.

**Structural checks:**
1. Open the HTML file in a browser.
2. Confirm the executive summary reads correctly without expanding anything.
3. Confirm the badge class matches the change scope (see badge colour conventions).
4. Click every `<details>` — each opens and closes, and opening one closes the others.
5. Confirm `<aside class="note">` renders with the blue left border.
6. Confirm the `<table class="impact">` columns align.
7. Confirm the evolution arc accurately summarizes the commit sequence.
8. Confirm the architectural layers overview (below the impact table) correctly names the affected layers in dependency order.
9. Confirm every impact cell that references a file uses `<var><a href="#file-N">` and the link jumps to a matching `<details>` `id`.
10. Run print preview — confirm all file details are visible in print (`<details>` are forced open).

**Content-quality checks:**
1. Confirm every impact row contrasts exactly **one** behavioral or architectural difference.
2. Confirm every caveat is a real risk, downside, or future-edit footgun (not happy-path description).
3. Confirm the first sentence of the executive summary makes sense on its own.
4. Confirm any red flags from the commit audit (reverts, missing tests) are reflected in the caveats section.
5. Confirm the primary feature description explains the mechanism or flow, not just a checklist of added pieces.
6. Confirm the executive summary anchors scope with an **Out of scope:** marker stating what stayed the same.
7. **Permission/access-control scan:** Scan the diff for permission or access-control changes (role checks, route guards, conditional rendering flags); if present, confirm they are surfaced prominently. Even 1–2 line changes here often carry more behavioral weight than their diff size suggests.
8. **Accessibility scan:** If the diff introduces CSS transitions or animations, confirm the output includes or acknowledges `@media (prefers-reduced-motion: reduce)` support.
9. **Fact-check pass:** Re-read the diff to verify: file paths, line counts, variable names, code snippets, numeric counts, and formatting strings in the impact table and caveats are accurate. If a caveat references a specific constant or value, confirm it exists in the diff.

**Phase 5 is complete when:** every check above passes — resolve any failure before delivering the output.

## Common Mistakes

See [`references/common-mistakes.md`](./references/common-mistakes.md) for the catalog of HTML construction errors — what a wrong output looks like. The most common: writing a full `<html>` document instead of a `<section>` fragment; the wrapper script handles the shell.

## Red Flags & Rationalizations

See [`references/red-flags.md`](./references/red-flags.md) for the catalog of process rationalizations — the internal excuses for skipping a step, each paired with a redirect. The core guardrail: if the wrapper script doesn't exist at the expected path, stop and inform the user — never improvise the shell.
