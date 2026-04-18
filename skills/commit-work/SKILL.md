---
name: commit-work
description: Commit all changes with the OpenSpec proposal title and ID as a git trailer. Use when the user says "commit this", "commit work", or wants to commit the current batch of changes with structured OpenSpec trailers. Auto-archives the change first if it has not been archived yet.
---

# Commit Work

Commit all changes with the OpenSpec proposal title as the commit message and the change ID as a git trailer. Archives the change first if it is still active.

## When to use

- The user wants to commit the current work with OpenSpec metadata attached.
- An active OpenSpec change exists and should be archived as part of committing.
- The user explicitly invokes `/commit-work` or asks to "commit this change".

## Steps

1. **Determine OpenSpec ID and title:**
   - If arguments are provided, use them
   - If you are currently working on an OpenSpec, use that ID and title
   - Otherwise:
     1. Run `openspec list` to find active changes
     2. If exactly one active change exists, use that ID
     3. If multiple changes exist, ask the user which one to use
     4. If no changes exist, ask the user for the ID and title
     5. Extract the title from the first heading in `openspec/changes/<id>/proposal.md`

2. **Archive the OpenSpec change (if not already archived):**
   - Check if `openspec/changes/<id>/` directory exists
   - If it exists, invoke `/opsx:archive <id>`
   - If the directory does not exist (already archived), skip this step

3. Run the following commands to stage all changes and create a commit with the OpenSpec ID as a git trailer:
   ```bash
   git add -A
   git commit -m "<title>" --trailer "OpenSpec-Id=<openspec-id>"
   ```

## Reference

- Run `git commit --help` for commit options (see especially `--trailer`)
