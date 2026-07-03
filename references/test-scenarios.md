# Test Scenarios — explain-diff

## Scenario 1: Medium PR with 5 files

**Setup:** Provide an agent with the output of `git diff --stat HEAD~3..HEAD` showing 5 files changed (2 JSX, 2 CSS, 1 config) across ~200 lines.

**Expected behavior:**
- Agent requests `git diff` to read full changes
- Produces an HTML snippet (not Markdown, not plain text)
- Snippet has all required sections: executive summary (with stats bar), impact table, file breakdown (5 `<details>`), caveats & tradeoffs aside
- Agent uses `html_wrap.py` to wrap it
- Final output has `<title>`, `<meta viewport>`, and stylesheet

**Failure signals:**
- Returns plain Markdown
- Writes `<html>` by hand instead of using the script
- Omits the caveats aside
- Groups files with **independent logic** changes into one `<details>` accordion

## Scenario 2: Single-file hotfix

**Setup:** `git show HEAD` for a 1-file, 15-line change.

**Expected behavior:**
- Agent still produces the full HTML structure (exec summary, impact table, file breakdown, caveats aside)
- Impact table has 1-2 rows
- Caveats aside may be empty but still present with "None identified"

**Failure signals:**
- "This is too small for HTML" rationalization
- Drops back to Markdown "because it's simpler"
- Produces HTML but without `<aside class="note">`

## Scenario 3: Breaking API change with no tests

**Setup:** A PR that renames a core data model, updates 8 consumers, but has 0 test changes.

**Expected behavior:**
- Caveats aside notes missing test coverage as a tradeoff
- Impact table shows the Before/After of the model shape
- File breakdown has exactly 8 `<details>`

**Failure signals:**
- Omits the missing-tests caveat
- Collapses all 8 consumer changes into one `<details>`

## Scenario 4: No `html_wrap.py` available

**Setup:** Agent is on a machine or in a context where `scripts/html_wrap.py` does not exist.

**Expected behavior:**
- Agent detects missing dependency
- Tells the user "Script not found at path, create it or install it first"
- Does NOT hand-write a full HTML document as fallback

**Failure signals:**
- Silently writes a full `<html>` document inline
- Claims "I'll adapt the process" without informing the user

## Scenario 5: Large refactor (15+ files, mechanical)

**Setup:** A PR that renames an import path across 15+ files, with no behavioral changes (pure find-and-replace).

**Expected behavior:**
- Executive summary describes the change scope (e.g., "Renamed X to Y across 15 files")
- Impact table has 1-2 rows: "Renamed import" Before/After
- File breakdown merges related files into grouped accordions (e.g., one `<details>` for "All component imports" with a `<ul>` listing the remapped files under `<h3>`)
- Caveats aside notes "None identified" since the change is mechanical

**Failure signals:**
- Lists all 15+ files in separate `<details>` accordions
- Omits the executive summary or impact table
- No `<h3>` sub-grouping inside merged accordions

## Scenario 6: Multi-commit diff with a revert in history

**Setup:** A 10-commit branch where commit 5 is `revert: feature-x changes` and commit 6 re-lands the feature differently.

**Expected behavior:**
- Caveats aside mentions the revert as context, with a brief explanation
- Impact table and file breakdown treat the net change (not the intermediate revert)
- Executive summary does not mention the revert

**Failure signals:**
- No mention of the revert in the caveats section
- Impact table includes the revert as a distinct row (confusing for readers)

## Scenario 7: Trivial change (config-only, well-tested)

**Setup:** A 2-file PR that updates a CI config version and bumps a dependency. Tests exist, no behavior change.

**Expected behavior:**
- Impact table has 1-2 rows showing the version bump
- Caveats aside is present with the text "None identified"
- File breakdown has 2 `<details>` accordions

**Failure signals:**
- Omits the caveats `<aside>` entirely
- Manufactures fake caveats to avoid an empty section
- Lists no impact table rows
