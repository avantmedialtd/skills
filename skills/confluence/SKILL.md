---
name: confluence
description: Manage Confluence pages from the command line. Use when working with Confluence pages, spaces, comments, labels, attachments, or searching wiki content.
---

# Confluence CLI

Command-line tool for managing Confluence pages via `af confluence`.

## Setup

Add the following environment variables to your project's `.env` file:
- `JIRA_BASE_URL` — Your Atlassian instance URL (e.g., `https://company.atlassian.net`)
- `JIRA_EMAIL` — Your Atlassian account email
- `JIRA_API_TOKEN` — API token from https://id.atlassian.com/manage-profile/security/api-tokens

Uses the same Atlassian credentials as the Jira skill.

## Project Defaults

If the project instructions specify a default Confluence space key (e.g., `Confluence space: TEAM`), use it as the default for `--space`, `list`, and CQL queries. Explicit user input always overrides the default.

## Quick Reference

Run `af confluence --help` for all options.

### Read Operations

- `af confluence get <page-id>` — Get page content and metadata
- `af confluence list <space-key> [--limit N]` — List pages in a space
- `af confluence search "<cql>"` — Search with CQL
- `af confluence tree <page-id>` — Show page and its children
- `af confluence comments <page-id>` — List comments on a page
- `af confluence labels <page-id>` — List labels on a page
- `af confluence attachments <page-id>` — List attachments on a page
- `af confluence spaces` — List all spaces
- `af confluence space <space-key>` — Get space details

### Write Operations

- `af confluence create --space <key> --title "<text>" [--body "<text>"] [--body-file <path>] [--parent <page-id>] [--status draft|current]`
- `af confluence update <page-id> [--title "<text>"] [--body "<text>"] [--body-file <path>] [--status draft|current] [--message "<text>"]`
- `af confluence delete <page-id>`
- `af confluence comment <page-id> --add "<text>"`
- `af confluence label <page-id> --add "<name>"`
- `af confluence label <page-id> --remove "<name>"`
- `af confluence attach <page-id> <file>` — Upload an attachment

## Output Formats

- Default: Markdown
- JSON: Add `--json` flag

## Common Workflows

### Publish a document from a file

```bash
af confluence create --space TEAM --title "Architecture Decision Record" \
  --body-file ./docs/adr-001.md
```

### Create a child page under an existing page

```bash
# Find the parent page ID first
af confluence search "title = 'Engineering Wiki' AND space = TEAM"

# Create child page
af confluence create --space TEAM --title "Onboarding Guide" \
  --body-file ./onboarding.md --parent 12345
```

### Update a page from a file with a version message

```bash
af confluence update 12345 --body-file ./updated-doc.md \
  --message "Revised after Q1 review"
```

### Create a draft page

```bash
af confluence create --space TEAM --title "RFC: New Auth System" \
  --body-file ./rfc.md --status draft
```

### Browse a page tree

```bash
# See a page and all its children
af confluence tree 12345
```

### Work with comments

```bash
# List comments
af confluence comments 12345

# Add a comment
af confluence comment 12345 --add "Reviewed — looks good to merge"
```

### Manage labels

```bash
# List labels
af confluence labels 12345

# Add a label
af confluence label 12345 --add "reviewed"

# Remove a label
af confluence label 12345 --remove "draft"

# Bulk label: add to multiple pages
for id in 12345 12346 12347; do
  af confluence label "$id" --add "q1-roadmap"
done
```

### Attach files

```bash
# Attach a diagram
af confluence attach 12345 ./architecture.png

# Attach multiple files
for f in ./diagrams/*.png; do
  af confluence attach 12345 "$f"
done
```

### Search examples

```bash
# Pages in a space
af confluence search "space = TEAM" --limit 20

# Pages by title
af confluence search "title = 'Meeting Notes'"

# Pages with a specific label
af confluence search "label = 'architecture'"

# Recently modified pages
af confluence search "space = TEAM AND lastModified > now('-7d')"

# Pages containing specific text
af confluence search "text ~ 'deployment process'"

# Pages by creator
af confluence search "creator = currentUser() AND space = TEAM"
```

## Tips

- **Discover first**: Run `af confluence spaces` to find space keys, `af confluence list <space>` to browse pages
- **Use `--body-file` for real content**: Inline `--body` is fine for short pages; use `--body-file` for anything substantial
- **Quote CQL queries**: Always wrap CQL in double quotes to handle spaces and operators
- **CQL syntax**: Uses `=` for exact match, `~` for contains, `AND`/`OR` for combining. See [Atlassian CQL docs](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/) for full syntax
- **Use `--json` for scripting**: Pipe output to `jq` for automation

## Error Handling

- Errors print to stderr
- With `--json`: `{"error": "message"}`
- Exit codes: `0` success, `1` error
