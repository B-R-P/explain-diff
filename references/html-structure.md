# HTML Structure Rules for Diff Reviews

## Allowed Top-Level Tags (root document fragment)

Use ONLY `<section>` as the root wrapper. Never `<div>`, `<article>`, or `<main>`.

```html
<!-- ✅ CORRECT -->
<section>
  ...
</section>

<!-- ❌ WRONG -->
<div class="review">
  ...
</div>
```

## Semantic Tag Mapping

| Purpose | Tag | Required Attributes |
|---------|-----|---------------------|
| Executive summary header | `<header>` | — |
| Section heading | `<h2>` | — |
| Sub-heading | `<h3>` | — |
| Paragraph | `<p>` | — |
| Impact table | `<table class="impact">` | `class="impact"` |
| File accordion | `<details>` | — |
| File path label | `<summary><var>path</var></summary>` | — |
| Change list | `<ul><li>` | — |
| Risk callout | `<aside class="warn">` | `class="warn"` |
| Risk heading | `<h4>` | — |

## Badge Classes

```html
<span class="badge badge-danger">Breaking</span>
<span class="badge badge-success">Feature</span>
<span class="badge badge-info">Refactor</span>
<span class="badge badge-warning">Minor</span>
<span class="badge badge-neutral">Chore</span>
```

## Inline Code Semantics

```html
<var>FileComponent.jsx</var>       <!-- file paths, function names, variables -->
<kbd>max-height: 65vh</kbd>        <!-- config values, constants, CLI args -->
<code>{ initial, limit }</code>    <!-- inline code snippets -->
<pre><code>                       <!-- multi-line code blocks -->
git log --oneline -5
</code></pre>
```

## Impact Table Shape

Always 3 columns: Metric | Before | After.

```html
<table class="impact">
  <thead>
    <tr>
      <th>Metric</th>
      <th>Before</th>
      <th>After</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Load-More behavior</strong></td>
      <td>All-or-nothing toggle</td>
      <td>Incremental chunked loading (CHUNK_SIZE=10)</td>
    </tr>
  </tbody>
</table>
```

Limit to 3-7 rows. Every row must contrast a single behavioural or architectural difference.

## Risk Aside Shape

```html
<aside class="warn">
  <h4>Risks &amp; Considerations</h4>
  <ul>
    <li><strong>Decoder form pre-fill removed</strong> — description of the risk…</li>
  </ul>
</aside>
```

Place immediately after the file breakdown section — never inside a `<details>`.

For zero-risk reviews, keep the `<aside>` with a single "None identified" entry:

```html
<aside class="warn">
  <h4>Risks &amp; Considerations</h4>
  <ul>
    <li><strong>None identified</strong> — This change is well-covered by existing tests and has no external impact.</li>
  </ul>
</aside>
```

## Details Accordion Shape

```html
<details>
  <summary><var>src/components/BwDataTable/BwDataTable.jsx</var></summary>
  <ul>
    <li><strong>Chunked load-more logic</strong> — description…</li>
    <li><strong>Guard changed</strong> — description…</li>
  </ul>
</details>
```

One `<details>` per file by default. **Merge** when files are pure-propagation passthroughs (e.g., forwarding a prop through 3 components, or 15 files with the same mechanical import rename — no independent logic per file). Use `<h3>` inside merged accordions to separate per-file details. Keep each bullet to 1 line if possible.

## Diff Stats in Summary

Add the line-count change as a badge inside `<summary>` to let readers quickly see which files had the most churn:

```html
<details>
  <summary><var>src/components/ChartGeneration/UserProgressChart/index.jsx</var> <span class="badge badge-success">+283/−18</span></summary>
  <ul>
    <li>…</li>
  </ul>
</details>
```

Badge class follows the same convention as the top-level badge (`.badge-success`, `.badge-info`, etc.) but should match the *overall character of the changes in that file* — not necessarily the PR's top-level scope.

## Sub-headings in Accordions

For files with many changes across distinct subsystems, group bullets under `<h3>` sub-headings inside the `<details>`:

```html
<details>
  <summary><var>src/components/ChartGeneration/UserProgressChart/index.jsx</var> <span class="badge badge-success">+283/−18</span></summary>
  <h3>Email Modal</h3>
  <ul>
    <li><strong>Recipient field</strong> — …</li>
    <li><strong>Preview image</strong> — …</li>
  </ul>
  <h3>Chart Capture</h3>
  <ul>
    <li><strong>Off-screen canvas</strong> — …</li>
  </ul>
</details>
```

Use this sparingly — only when 6+ bullets would otherwise make a flat list hard to scan.

## Executive Summary Shape

```html
<header>
  <span class="badge badge-warning">Minor</span>
  <h2>Incremental grouped-row loading, table scroll containment, …</h2>
  <p>One or two sentences explaining what the PR achieves and its business impact.</p>
</header>
```

The first sentence must stand alone — readers expand nothing and still understand the change.

## Dark Mode Compatibility

The default `html_wrap.py` stylesheet includes `@media (prefers-color-scheme: dark)`. Any custom styles added via `--style` must include a dark mode variant or the document will break on dark-themed browsers.

## Forbidden Patterns

- `<div>` used as a heading container — use `<header>` or `<section>`
- Inline `<style>` blocks in the snippet — the wrapper script injects all styles
- Nested `<section>` without a heading in the parent — each `<section>` should have a logical heading or be preceded by one
- Empty `<details>` — if a file has no meaningful changes to list, skip it
- Using `<br>` for layout — use flexbox classes or CSS instead
