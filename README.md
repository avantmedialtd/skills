# Avant Media Skills

Private agent skills for [Avant Media Ltd](https://avantmedia.co.uk). Opinionated development standards and workflows used across our projects.

## Installation

### Claude Code / skills.sh CLI

```bash
# Install all skills
npx skills add avantmedialtd/skills

# Install a specific skill
npx skills add avantmedialtd/skills --skill typescript-react-standards

# Install globally (available across all projects)
npx skills add avantmedialtd/skills -g
```

### Claude Desktop

Upload the `.skill` file from the `dist/` directory:

**Settings → Capabilities → Skills → Upload skill**

Or paste the contents of any `SKILL.md` into your project knowledge.

### Claude Code (manual)

```bash
# Project-level
cp -r skills/typescript-react-standards .claude/skills/

# User-level (all projects)
cp -r skills/typescript-react-standards ~/.claude/skills/
```

## Available Skills

| Skill                                                            | Description                                                                                                                    |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [commit-work](skills/commit-work/)                               | Commit all changes with the OpenSpec proposal title and ID as a git trailer; auto-archives first                               |
| [complete-work](skills/complete-work/)                           | Archive an OpenSpec change, commit with trailers, transition the Jira issue to Done, push, and verify CI                       |
| [confluence](skills/confluence/)                                 | Manage Confluence pages, spaces, comments, labels, attachments, and wiki search from the command line                          |
| [e2e-testing](skills/e2e-testing/)                               | E2E and visual regression testing with Playwright — test commands, patterns, and debugging tips                                |
| [jira](skills/jira/)                                             | Manage Jira issues, custom fields, links, and versions from the command line                                                   |
| [power-stack](skills/power-stack/)                               | Bun / Elysia / React / MUI monorepo blueprint — tech stack, conventions, and wiring patterns                                   |
| [start-work](skills/start-work/)                                 | Assign a Jira issue to yourself and convert it into an OpenSpec proposal; hands off to the OPSX workflow                       |
| [typescript-react-standards](skills/typescript-react-standards/) | Opinionated TypeScript and React conventions, project structure, and testing approach                                          |
| [autopilot](skills/autopilot/)                                   | Autonomously pick up a Jira issue and complete it end-to-end — plan, implement, test, verify, archive, commit, push, verify CI |

## Skill Format

Each skill follows the [Agent Skills specification](https://agentskills.io/):

```
skill-name/
├── SKILL.md           # Required — frontmatter + instructions
├── references/        # Optional — loaded on demand
└── scripts/           # Optional — executable helpers
```

Skills work with Claude Code, Cursor, Codex, and [35+ other agents](https://github.com/vercel-labs/skills#supported-agents).

## Building .skill packages for Claude Desktop

```bash
# Requires the skill-creator scripts (or manual zip)
python3 scripts/package_skill.py skills/typescript-react-standards dist/
```

## Contributing

This is a private repository. Skills reflect Avant Media's conventions and are not intended as universal best practices. If you're on the team, open a PR — the SKILL.md is the source of truth.

## Licence

MIT
