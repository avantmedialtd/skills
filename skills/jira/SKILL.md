---
name: jira
description: Manage Jira issues from the command line. Use when working with Jira issues, creating tasks, updating status, assigning work, linking issues, managing versions, setting or reading custom fields (Story Points, Sprint, Severity, etc.), or searching for issues.
---

# Jira CLI

Command-line tool for managing Jira issues via `af jira`.

## Setup

Add the following environment variables to your project's `.env` file (preferred names first; legacy `JIRA_*` names are still accepted and fall back to these when unset):

- `ATLASSIAN_BASE_URL` — Your Atlassian instance URL (e.g., `https://company.atlassian.net`)
- `ATLASSIAN_EMAIL` — Your Atlassian account email
- `ATLASSIAN_API_TOKEN` — API token from https://id.atlassian.com/manage-profile/security/api-tokens

## Project Defaults

If the project instructions specify a default Jira project key (e.g., `Jira project: PROJ`), use it as the default for `--project`, `list`, `types`, and JQL queries. Explicit user input always overrides the default.

## Quick Reference

Run `af jira --help` for all options.

### Read Operations

- `af jira get <issue-key>` — Get issue details (renders a "Custom Fields" section when any are set)
- `af jira list <project> [--limit N] [--show-field a,b,c]` — List project issues; `--show-field` adds custom-field columns
- `af jira search "<jql>" [--show-field a,b,c]` — Search with JQL
- `af jira projects` — List projects
- `af jira types <project>` — List issue types
- `af jira fields [--project <key> --type <name>] [--refresh] [--verbose]` — List custom fields; with `--project`/`--type` marks required fields and shows allowed values
- `af jira transitions <issue-key>` — List available transitions
- `af jira comment <issue-key>` — List comments
- `af jira remote-link <issue-key>` — List remote links
- `af jira versions <project>` — List all versions in a project
- `af jira version <version-id>` — Get version details

### Write Operations

- `af jira create --project <key> --type <type> --summary "<text>" [--description "<text>"] [--priority <name>] [--labels a,b,c] [--parent <key>] [--estimate <time>] [--fix-version <v1,v2>] [--affected-version <v>] [--field name=value]... [--field-json '<json>']`
- `af jira update <issue-key> [--summary "<text>"] [--description "<text>"] [--priority <name>] [--labels a,b,c] [--estimate <time>] [--remaining <time>] [--fix-version <v1,v2>] [--affected-version <v>] [--field name=value]... [--field-json '<json>']`
- `af jira transition <issue-key> --to "<status>"`
- `af jira assign <issue-key> --to <email>` (use `--to none` to unassign)
- `af jira comment <issue-key> --add "<text>"`
- `af jira attach <issue-key> <file>` — Attach a file (images, PDFs, etc.)
- `af jira delete <issue-key>`

### Link Operations

- `af jira link <issue-key> --to <issue-key> [--type "<name>"]` — Link two issues (default type: "Blocks")
- `af jira unlink <issue-key> --from <issue-key>` — Remove a link
- `af jira remote-link <issue-key> --url "<url>" --title "<text>"` — Add a remote link
- `af jira remote-link <issue-key> --remove <link-id>` — Remove a remote link

### Version Operations

- `af jira version-create --project <key> --name "<text>" [--description "<text>"] [--start-date YYYY-MM-DD] [--release-date YYYY-MM-DD] [--released]`
- `af jira version-update <id> [--name "<text>"] [--description "<text>"] [--start-date YYYY-MM-DD] [--release-date YYYY-MM-DD] [--released] [--unreleased]`
- `af jira version-delete <id> [--move-fix-issues-to <id>] [--move-affected-issues-to <id>]`

## Output Formats

- Default: Markdown
- JSON: Add `--json` flag

## Common Workflows

### View my assigned issues

```bash
af jira search "assignee = currentUser() AND status != Done ORDER BY priority DESC"
```

### Start working on an issue

```bash
af jira get PROJ-123
af jira transition PROJ-123 --to "In Progress"
af jira comment PROJ-123 --add "Starting work"
```

### Complete an issue

```bash
af jira comment PROJ-123 --add "Done"
af jira transition PROJ-123 --to "Done"
```

### Create a bug with details

```bash
af jira create --project PROJ --type Bug --summary "Login fails on Safari" \
  --description "Users cannot log in using Safari 17. Error: 'Invalid session'" \
  --priority High --labels safari,auth,urgent
```

### Create a task with time estimate and version

```bash
af jira create --project PROJ --type Task --summary "Implement auth" \
  --estimate "4h" --fix-version "v1.0.0"
```

### Create a subtask

```bash
af jira create --project PROJ --type Sub-task --summary "Write unit tests" \
  --parent PROJ-123
```

### Link issues

```bash
# Block another issue
af jira link PROJ-123 --to PROJ-456

# Use a specific link type
af jira link PROJ-123 --to PROJ-456 --type "Relates"

# Remove a link
af jira unlink PROJ-123 --from PROJ-456
```

### Remote links

```bash
# List remote links
af jira remote-link PROJ-123

# Add a remote link (e.g., design doc, PR, external resource)
af jira remote-link PROJ-123 --url "https://example.com/doc" --title "Design Doc"

# Remove a remote link
af jira remote-link PROJ-123 --remove 10042
```

### Manage versions

```bash
# List versions
af jira versions PROJ

# Create a version
af jira version-create --project PROJ --name "v1.0.0" --release-date 2024-06-01

# Mark a version as released
af jira version-update 12345 --released
```

### Update time tracking

```bash
af jira update PROJ-123 --estimate "8h" --remaining "2h"
```

### Custom fields

Custom fields are instance-specific (Story Points, Sprint, Severity, and any custom selectors configured by the Jira admin). Reference them by alias (from `af.json`), by display name (case-insensitive, must be unambiguous), or by raw `customfield_<digits>` id — in that precedence order.

```bash
# Discover fields — lists every custom field in the instance
af jira fields

# Project-and-type scope marks required fields with ✓ and lists allowed values
af jira fields --project PROJ --type Story

# Bust the cache (instance catalog is cached 24h, createmeta 1h)
af jira fields --refresh

# Create with required custom fields
af jira create --project PROJ --type Story --summary "Redesign login" \
  --field storyPoints=5 --field severity=High

# Update a custom field
af jira update PROJ-123 --field storyPoints=8

# Clear a custom field (empty value after `=`)
af jira update PROJ-123 --field severity=

# JSON escape hatch for complex shapes (cascading selects, raw overrides)
af jira create --project PROJ --type Story --summary "X" \
  --field-json '{"customfield_10050":{"value":"A","child":{"value":"A1"}}}'

# Show custom fields as extra columns when listing
af jira list PROJ --show-field storyPoints,severity
```

Encoding rules (applied per `--field`):

- `number` → numeric; `string`/`date`/`datetime` → raw string
- `option` → `{value: "..."}`; multi-select → array of those
- `user` → resolves email/name to `{accountId}` via `findUser`; multi-user splits on commas
- `version` → `{name: "..."}`; multi-version array
- sprint → numeric sprint ID only
- Epic Link → issue key string
- Empty value after `=` → `null` (clears the field)
- Unknown schema types pass through raw and warn to stderr — reach for `--field-json` if that doesn't encode correctly

Optional aliases live in `af.json` and make commands more ergonomic:

```json
{
    "jira": {
        "customFields": {
            "storyPoints": { "id": "customfield_10016" },
            "sprint":      { "id": "customfield_10020", "type": "sprint" },
            "severity":    { "id": "customfield_10099" }
        }
    }
}
```

The CLI does **not** pre-validate required fields on create. Run `af jira fields --project PROJ --type <type>` first to see what Jira will require; otherwise the error message from Jira's 400 surfaces unchanged.

### Attach files to an issue

```bash
# Attach a screenshot
af jira attach PROJ-123 ./screenshot.png

# Attach multiple files
for f in ./audit/*.png; do
  af jira attach PROJ-123 "$f"
done
```

### Search examples

```bash
# My open issues
af jira search "assignee = currentUser() AND status != Done"

# Recent bugs in project
af jira search "project = PROJ AND type = Bug ORDER BY created DESC" --limit 10

# Unassigned issues
af jira search "project = PROJ AND assignee IS EMPTY"

# Issues updated this week
af jira search "project = PROJ AND updated >= -7d"

# High priority blockers
af jira search "priority = Highest AND status != Done"
```

## Tips

- **Discover valid values first**: Run `af jira transitions <key>` before transitioning, `af jira types <project>` before creating, `af jira fields --project <key> --type <type>` before creating an issue that requires custom fields
- **Use `--json` for scripting**: Pipe output to `jq` for automation
- **Quote JQL queries**: Always wrap JQL in double quotes to handle spaces
- **Time format**: Use `"2h"`, `"1d"`, `"30m"` for estimates
- **Clearing flags**: `--fix-version ""` clears versions; `--field name=` clears a custom field
- **Alias custom fields in `af.json`** for nicer `--field` ergonomics; otherwise use the display name (case-insensitive, must be unambiguous) or the raw `customfield_<digits>` id

## Error Handling

- Errors print to stderr
- With `--json`: `{"error": "message"}`
- Exit codes: `0` success, `1` error
