---
name: sonar
description: Inspect SonarQube quality gates, issues, and measures for a Bitbucket pull request or main branch from the command line. Use when checking SonarQube gate status on a PR, reviewing new issues introduced by a branch, or wiring quality gates into CI scripts.
---

# SonarQube CLI

Read-only command-line tool for inspecting a self-hosted SonarQube instance via `af sonar`. Intentionally companion-shaped to `af bb pr` — the same numeric PR id identifies both sides.

## Setup

SonarQube uses its own bearer token. Atlassian and Bitbucket credentials are **not** interchangeable. Add the following to your project's `.env`:

- `SONAR_TOKEN` — User token from `<sonar>/account/security` (required)
- `SONAR_BASE_URL` — Sonar instance URL (optional; falls back to `sonar.host.url` in `sonar-project.properties`)

## Project Key Resolution

Walks the same path `sonar-scanner` does:

1. `--project <key>` flag (highest priority)
2. `sonar.projectKey` in `sonar-project.properties` (walking up from cwd)

There is intentionally no `af.json` block for Sonar — the properties file is the canonical source of truth.

## Quick Reference

Run `af sonar --help` for all options.

- `af sonar pr <id>` — Quality gate + top new issues + measures for a Bitbucket PR
- `af sonar pr` — Same, auto-detecting the PR id from the current branch's open Bitbucket PR
- `af sonar pr <id> --issues` — Full new-issues list (not just the top 4)
- `af sonar pr <id> --json` — Raw JSON for scripting
- `af sonar gate` — Quality gate status for the main branch
- `af sonar prs` — All PRs known to SonarQube

## Output Formats

- Default: Markdown summary with gate status, top issues, and key measures
- JSON: Add `--json` for raw SonarQube API responses

## Exit Codes

`af sonar pr` and `af sonar gate` exit **non-zero when the quality gate status is `ERROR`** — safe to drop into shell scripts and CI as a gate.

- `0` — Gate `OK` (or command completed successfully)
- `1` — Gate `ERROR`, or a command error

## Common Workflows

### Check the gate on a PR you're reviewing

```bash
# Explicit PR id — same number as af bb pr 42
af sonar pr 42

# Auto-detect from the current branch
git checkout feature/auth-rewrite
af sonar pr
```

### See the full list of new issues

```bash
# Default trims to the top 4 — pass --issues for everything
af sonar pr 42 --issues
```

### Gate the main branch

```bash
af sonar gate
# Exits 1 if the gate is red — wire into a deploy script
```

### Browse all PRs SonarQube has analysed

```bash
af sonar prs
```

### CI / script integration

```bash
# Block a deploy on red gate
if ! af sonar gate >/dev/null; then
  echo "Sonar gate is red — refusing to deploy"
  exit 1
fi

# Extract a specific measure with jq
af sonar pr 42 --json | jq '.measures.new_coverage'
```

## PR Auto-Detection

`af sonar pr` (no id) uses the bundled Bitbucket client to find the current git branch's open PR. It returns distinct errors for:

- Zero PRs open for the branch
- Multiple open PRs (ambiguous)
- Missing Bitbucket credentials
- Detached `HEAD`

Each error message suggests `af sonar pr <id>` as the explicit escape hatch. Auto-detection requires the same `BITBUCKET_*` env vars as the [[bitbucket]] skill.

## Tips

- **Pair with `af bb pr <id>`** — same numeric id, complementary views (code review vs. quality gate)
- **`--issues` for full noise** — the trimmed default is for at-a-glance review; reach for `--issues` when triaging
- **Exit codes are scriptable** — `af sonar pr 42 && echo ok || echo red` is idiomatic
- **No mutations** — this command is read-only by design; issue assign/transition and hotspot management are deferred

## Out of Scope

The following are intentionally not part of `af sonar`:

- SonarCloud support (self-hosted SonarQube only)
- Mutating operations (issue assign, transition, hotspot review)
- Scanner wrapping (`sonar-scanner` is invoked separately, typically in CI)
- Inline Sonar gate status in `af bb pr` output

## Error Handling

- Errors print to stderr
- With `--json`: `{"error": "message"}`
- Exit codes: `0` success / gate OK, `1` error / gate ERROR
