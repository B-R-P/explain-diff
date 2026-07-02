# explain-diff

`explain-diff` is an agent-facing skill that turns Git diffs, pull requests, branch comparisons, or commit histories into self-contained HTML review documents.

## What is in this repo

```text
SKILL.md                    # Instructions agents should follow
scripts/html_wrap.py         # Converts an HTML snippet into a complete document
scripts/README.md            # Script-specific notes
references/html-structure.md # Required HTML structure for generated reviews
references/test-scenarios.md # Scenarios for checking agent behavior
```

## What agents produce

When an agent uses this skill, it should create an HTML review with:

- An executive summary
- A before/after impact table
- Expandable file breakdowns
- A risk callout, even when the risk is “None identified”

## Running the wrapper manually

The wrapper expects an HTML snippet and adds the full document shell, metadata, and default styles:

```bash
python scripts/html_wrap.py snippet.html -o review.html --title "PR Review"
```

It also accepts stdin:

```bash
cat snippet.html | python scripts/html_wrap.py - -o review.html --title "PR Review"
```

Useful options:

- `--style FILE` replaces the default stylesheet.
- `--append-style FILE` appends extra CSS.
- `--serve` previews the document locally.
- `--no-open` prevents browser launch with `--serve`.
- `--minify` trims snippet boundary whitespace.

## Notes for maintainers

- Keep detailed agent instructions in `SKILL.md`, not this README.
- Keep full HTML requirements in `references/html-structure.md`.
- Do not remove `scripts/html_wrap.py`; the skill treats it as required.
