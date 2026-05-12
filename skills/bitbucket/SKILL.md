---
name: bitbucket
description: Manage Bitbucket Cloud pull requests, comments, tasks, and pipelines from the command line. Use when working with PRs, reviewing code, leaving inline comments, creating PR tasks, triggering or inspecting Bitbucket Pipelines, or looking up reviewer account IDs.
---

# Bitbucket Cloud CLI

Command-line tool for managing Bitbucket Cloud via `af bitbucket` (alias `af bb`).

## Setup

Bitbucket Cloud authentication is **separate from Jira/Confluence**. Atlassian API tokens scoped for Jira do not authenticate against Bitbucket Cloud — they return 401. Add the following to your project's `.env`:

- `BITBUCKET_USERNAME` — Bitbucket username or workspace token label (falls back to `ATLASSIAN_EMAIL` / `JIRA_EMAIL`)
- `BITBUCKET_API_TOKEN` — Workspace API token or app password (`BITBUCKET_APP_PASSWORD` is also accepted as a legacy alias)

Generate credentials:

- **Workspace API token (recommended for automation)** — `https://bitbucket.org/<workspace>/workspace/settings/api-tokens`
- **App password** — `https://bitbucket.org/account/settings/app-passwords/`

## Workspace and Repo Resolution

The target workspace and repo are resolved in this order:

1. `--workspace W --repo R` flags (highest priority)
2. `af.json`:
    ```json
    {
        "bitbucket": {
            "workspace": "myws",
            "repo": "myrepo"
        }
    }
    ```
3. The git `origin` remote, if it points at `bitbucket.org`
4. Error with help text

## Quick Reference

Run `af bb --help` (or `af bb pr --help`, `af bb pipeline --help`) for all options.

### Pull Requests

- `af bb pr list [--state OPEN|MERGED|DECLINED|ALL] [--mine | --author Q]`
- `af bb pr get <id>`
- `af bb pr diff <id>`
- `af bb pr create --title T [--from B] [--to B] [--description / --description-file F] [--reviewers a,b] [--draft]`
- `af bb pr update <id> [--title T] [--description / --description-file F] [--reviewers a,b]`
- `af bb pr approve <id>`
- `af bb pr unapprove <id>`
- `af bb pr request-changes <id>`
- `af bb pr merge <id> [--strategy merge_commit|squash|fast_forward] [--close-source]`
- `af bb pr decline <id>`

Reviewers must be passed as Bitbucket Cloud **account IDs** (not usernames). Use `af bb members --query <name>` to look them up.

### PR Comments

Comment body shape is determined by flags on `add`:

- `af bb pr comment list <pr-id>`
- `af bb pr comment get <pr-id> <cid>`
- `af bb pr comment add <pr-id> --body / --body-file [--file PATH --line N] [--reply-to CID]`
    - `--file PATH --line N` makes the comment an inline anchor
    - `--reply-to CID` threads the comment as a reply
- `af bb pr comment update <pr-id> <cid> --body / --body-file`
- `af bb pr comment delete <pr-id> <cid>`

### PR Tasks

Tasks can stand alone or be anchored to a comment:

- `af bb pr task list <pr-id>`
- `af bb pr task add <pr-id> --body / --body-file [--on-comment CID]`
- `af bb pr task update <pr-id> <tid> [--body / --body-file] [--resolved | --unresolved]`
- `af bb pr task delete <pr-id> <tid>`

### Pipelines

- `af bb pipeline list [--branch B] [--status PENDING|IN_PROGRESS|SUCCESSFUL|FAILED|...]`
- `af bb pipeline get <uuid|build-number>`
- `af bb pipeline trigger [--branch B] [--commit SHA] [--custom NAME] [--var k=v]`
- `af bb pipeline stop <uuid>`
- `af bb pipeline steps <uuid>`
- `af bb pipeline logs <pipeline-uuid> <step-uuid> [--follow]`

### Member Lookup

- `af bb members [--query Q]` — Look up account IDs for use with `--reviewers`

## Output Formats

- Default: Markdown
- JSON: Add `--json` to any subcommand for raw API responses

## Common Workflows

### Review a PR

```bash
af bb pr get 42
af bb pr diff 42
af bb pr comment list 42
af bb pr task list 42
```

### Create a PR from current branch

```bash
af bb pr create --title "Add SonarQube support" \
  --description-file ./PR_DESCRIPTION.md \
  --reviewers 557058:abc-123,557058:def-456
```

### Leave an inline review comment

```bash
# Anchor a comment to a specific line of a file in the diff
af bb pr comment add 42 \
  --file src/auth/login.ts --line 87 \
  --body "This branch isn't covered by tests — can we add one?"

# Thread a reply
af bb pr comment add 42 --reply-to 9876543 --body "Good catch, fixing."
```

### Add and resolve PR tasks

```bash
# Standalone task
af bb pr task add 42 --body "Update CHANGELOG before merge"

# Task anchored to an existing comment
af bb pr task add 42 --on-comment 9876543 --body "Rename this variable"

# Resolve when done
af bb pr task update 42 12345 --resolved
```

### Approve and merge

```bash
af bb pr approve 42
af bb pr merge 42 --strategy squash --close-source
```

### Trigger and watch a pipeline

```bash
# Trigger a custom pipeline with variables
af bb pipeline trigger --branch main --custom deploy-prod --var ENV=prod

# Watch logs as the step runs
af bb pipeline list --branch main --status IN_PROGRESS
af bb pipeline steps <pipeline-uuid>
af bb pipeline logs <pipeline-uuid> <step-uuid> --follow
```

### Look up reviewer account IDs

```bash
# Reviewers must be account IDs, not usernames
af bb members --query "Jane"
af bb pr update 42 --reviewers 557058:abc-123
```

## Tips

- **Use the alias `af bb`** — every subcommand below also works under `af bitbucket`
- **Reviewers are account IDs only** — usernames silently fail; always resolve via `af bb members`
- **Workspace tokens beat app passwords** — they're scoped per-workspace and easier to rotate
- **`--json` for scripting** — pipe through `jq` for automation
- **PR descriptions from files** — `--description-file ./PR_BODY.md` avoids quoting hell in the shell

## Error Handling

- Errors print to stderr
- With `--json`: `{"error": "message"}`
- Exit codes: `0` success, `1` error, `401` typically means Bitbucket-Cloud-specific credentials are missing or a Jira-scoped Atlassian token was supplied
