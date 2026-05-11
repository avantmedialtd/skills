---
name: e2e-testing
description: E2E and visual regression testing with Playwright. Use when writing tests, running E2E tests, debugging test failures, or working with visual baselines. Contains test commands, patterns, and debugging tips.
---

# E2E Testing

Playwright-based E2E and visual regression tests, run inside Docker for environment isolation. The Docker setup uses a separate test database so dev work continues uninterrupted in parallel.

## Why Docker

Two reasons that compound:

1. **DB isolation** — the dev DB typically has PROD-synced data; the test DB has deterministic fixtures. Separate database instances on separate containers, separate compose profile.
2. **Visual baseline reproducibility** — fonts and Chromium versions are pinned, so visual snapshots are stable across machines.

The procedure runs as direct `docker compose` calls so it is fully visible and the runner can recover from infrastructure issues without elevated permissions or project-specific wrappers.

## Standard run

Tear down stale state, build, run, fetch report, tear down. One sequence (paste as a single Bash invocation):

```bash
dc() { docker compose -f docker-compose.yml -f docker-compose.test.yml --profile testing "$@"; }
dc down -v --remove-orphans \
  && dc up -d --build --wait \
  && dc exec -T e2e sh -c "npm run e2e -- --reporter=list,html"
e=$?
dc cp e2e:/workspace/playwright-report ./playwright-report 2>/dev/null || true
[ "$e" -ne 0 ] && dc cp e2e:/workspace/test-results ./test-results 2>/dev/null
dc down -v --remove-orphans
exit $e
```

`--remove-orphans` on every `down` is what makes the runner self-healing — a previous crashed run never blocks the next attempt.

## Filter variants

Replace the `npm run e2e --` portion in the `dc exec` line:

| Goal                        | Replace with                                                               |
| --------------------------- | -------------------------------------------------------------------------- |
| Full suite, parallel        | `npm run e2e -- --workers 2 --max-failures=1 --reporter=list,html`         |
| Single test by name         | `npm run e2e -- --grep "test name" --reporter=list,html`                   |
| Single file                 | `npm run e2e -- tests/Feature.spec.ts --reporter=list,html`                |
| Multiple files              | `npm run e2e -- tests/A.spec.ts tests/B.spec.ts --reporter=list,html`      |
| Update all visual baselines | `npm run e2e -- --update-snapshots --reporter=list,html`                   |
| Update one baseline         | `npm run e2e -- --grep "homepage" --update-snapshots --reporter=list,html` |

**Pipes inside `--grep` are eaten by the shell** because the `dc exec -T e2e sh -c "..."` wraps the command in `sh -c`. `--grep "MCP|Expense"` is parsed as a pipeline. Use multiple file arguments instead, or run two separate `dc exec` calls.

## Fast iteration (no rebuild)

When only test specs under `e2e/` changed (no app source, no Dockerfile), skip the rebuild:

```bash
dc() { docker compose -f docker-compose.yml -f docker-compose.test.yml --profile testing "$@"; }
dc down -v --remove-orphans
dc up -d --no-build --wait
dc exec -T e2e sh -c "npm run e2e -- --grep 'pattern' --reporter=list,html"
e=$?
dc cp e2e:/workspace/playwright-report ./playwright-report 2>/dev/null || true
[ "$e" -ne 0 ] && dc cp e2e:/workspace/test-results ./test-results 2>/dev/null
dc down -v --remove-orphans
exit $e
```

`--no-build` reuses existing images. If they don't exist (first run on a fresh checkout), Docker errors clearly and you can rerun the standard path.

## Long-running runs in the background

E2E full runs take minutes. Redirect to a log and use Bash `run_in_background`:

```bash
# inside Bash tool with run_in_background=true
{ dc() { docker compose -f docker-compose.yml -f docker-compose.test.yml --profile testing "$@"; }
  dc down -v --remove-orphans \
    && dc up -d --build --wait \
    && dc exec -T e2e sh -c "npm run e2e -- --workers 2 --reporter=list,html"
  e=$?
  dc cp e2e:/workspace/playwright-report ./playwright-report 2>/dev/null || true
  [ "$e" -ne 0 ] && dc cp e2e:/workspace/test-results ./test-results 2>/dev/null
  dc down -v --remove-orphans
  exit $e; } > /tmp/e2e.log 2>&1
```

Direct foreground runs exceed harness output limits and SIGPIPE (exit 141).

## Critical Requirements

- **ALWAYS use `--remove-orphans`** in `down` — without it, stale containers from a previous failed run will block the next attempt.
- **ALWAYS add E2E tests** for every feature change.
- **ALWAYS run the full suite** (no `--grep`) before finishing, to confirm nothing else broke.
- **NEVER use `waitForLoadState('networkidle')`** — it's unreliable and causes timeouts. Wait for a specific visible element instead.
- **NEVER run Playwright directly outside Docker** — it would touch the dev DB instead of the test DB.

## Recovery from a stuck Docker state

If `dc up` fails with `Conflict. The container name "/<project>-db-1" is already in use`, a previous crash left orphans. Try the standard `dc down -v --remove-orphans` first. If that also fails, list and remove the test containers explicitly. **Test profile only — never touch the dev-DB container** (e.g. one named `<project>-local-db-1` or similar; check `docker ps` first):

```bash
# Replace <project> with the compose project name (usually the repo dir name).
# The grep -v guard excludes the dev DB — adjust the pattern to match your dev container's name.
docker rm -f $(docker ps -aq --filter "name=<project>-" --filter "name=-1" | grep -v 'local-db')
docker network rm <project>_app-network 2>/dev/null || true
```

Then retry the standard run.

## Debugging Failures

The `list` reporter prints each test's outcome on a single line. Failures look like `[FAIL] tests/Feature.spec.ts > test name`.

1. **Read the reporter output first** — error messages and file paths land in the console.
2. **For deeper debugging**, read `./test-results/<test-folder>/error-context.md` for the full DOM snapshot at failure time. This file is auto-generated by Playwright when a test fails.
3. **HTML report** with traces: `./playwright-report/index.html`.
4. **Trace files**: `./test-results/<test-folder>/trace.zip` — open via `npx playwright show-trace`.

Common failure causes:

- **Strict mode violations** — multiple elements matched. Add `level` to headings, scope to a section, or use `.first()`.
- **Timeout** — element not found. Check the DOM snapshot for actual structure vs. expected selectors.
- **Visual diff** — screenshot mismatch. If the change is intentional, regenerate baselines with `--update-snapshots`.
- **Docker SIGSEGV / exit 255** — Chromium crash inside the container, infrastructure flake. Retry once before treating as a code failure.

## Output Directories

- `playwright-report/` — HTML report with traces. Always populated after a run.
- `test-results/` — Failure artifacts including `error-context.md` and `trace.zip`. Populated **only when at least one test failed** (the conditional copy in the run script).

## Visual Baselines

Visual snapshot files live under `e2e/tests/visual-baselines/` (or wherever the project keeps them) and are bind-mounted into the test container, so `--update-snapshots` writes back to the repo directly. **Do not** `docker compose cp` the baselines back — that nests `visual-baselines/visual-baselines/`.

Time-sensitive baselines (anything rendering the current date, calendars, or live counters) need regeneration after seed-data shifts. Mask dynamic regions where possible — see [PATTERNS.md](PATTERNS.md).

## Anti-patterns

- `waitForLoadState('networkidle')` — unreliable, use visible-element waits.
- Running Playwright directly outside Docker (would touch your dev DB).
- `if` statements in assertions — use proper matchers.
- Mock auth keys — use real generated keys from seed data.
- Hardcoded dates that conflict between test files — see PATTERNS.md for offset allocation.

For test code patterns, selectors, and visual testing guidance, see [PATTERNS.md](PATTERNS.md).
