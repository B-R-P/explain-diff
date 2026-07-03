# explain-diff

`explain-diff` is an agent skill that turns Git diffs, pull requests, branch comparisons, or commit histories into self-contained HTML review documents.

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
- A caveats & tradeoffs callout, even when it states “None identified”

