# GitHub Actions Setup

This document describes how to configure the Genera Intelligence project for GitHub Actions CI/CD workflows.

## Overview

Two workflows are defined:

1. **ci-push.yml** — Runs on every push to any branch:
   - Linting (Ruff)
   - Unit tests (pytest, fast tests only — no API calls)
   - Optional smoke eval (5 cases) if `GOOGLE_API_KEY` secret is available

2. **eval-manual.yml** — Triggered manually via GitHub UI:
   - Full eval (all ~30 test cases)
   - LLM-as-Judge evaluation
   - Report saved as artifact

## Required Secrets

For the workflows to function, configure the following secrets in your GitHub repository settings (**Settings** → **Secrets and variables** → **Actions**):

### Required (for most workflows)

- **GOOGLE_API_KEY**
  - Your Google Cloud API key for Gemini LLM and embeddings.
  - Used by smoke eval (push CI) and full eval (manual workflow).
  - If not set, smoke eval step is gracefully skipped.

### Optional (for extended testing)

- **OPENAI_API_KEY**
  - OpenAI API key for testing with GPT models.
  - Used only if `LLM_PROVIDER=openai` or `EMBEDDINGS_PROVIDER=openai`.
  - If not set, workflows default to Gemini.

## Workflow Details

### CI Push Workflow (`.github/workflows/ci-push.yml`)

**Trigger:** Any push to any branch

**Jobs:**

1. **lint** (always runs)
   - Sets up Python 3.12
   - Installs Poetry and dependencies
   - Runs `poetry run ruff check src/backend`

2. **test** (always runs)
   - Sets up Python 3.12
   - Installs Poetry and dependencies
   - Runs `poetry run pytest -v -m "not requires_api_key"` (fast tests only)
   - No real API calls or external service dependencies

3. **smoke-eval** (conditional)
   - Only runs if `GOOGLE_API_KEY` secret is set
   - Sets up Python 3.12
   - Runs `poetry run python -m eval` with `EVAL_LEVEL=smoke` (5 quick cases)
   - Completes in < 2 minutes

**Environment Variables (in workflow):**
- `EVAL_LEVEL=smoke` — Run only 5 cases for speed
- `LLM_PROVIDER=gemini` — Use Gemini for LLM
- `EMBEDDINGS_PROVIDER=gemini` — Use Gemini for embeddings

### Manual Eval Workflow (`.github/workflows/eval-manual.yml`)

**Trigger:** Manual via GitHub UI (Actions tab → "Eval (Manual, Full 30 Cases)" → "Run workflow")

**Jobs:**

1. **eval-full** (always runs when manually triggered)
   - Sets up Python 3.12
   - Installs Poetry and dependencies
   - Runs `poetry run python -m eval` with `EVAL_LEVEL=full` (all ~30 cases)
   - Captures output to `eval-reports/eval-result.txt`
   - Uploads report as artifact (30-day retention)
   - Displays result in workflow logs

**Environment Variables (in workflow):**
- `EVAL_LEVEL=full` — Run all cases
- `LLM_PROVIDER=gemini` — Use Gemini for LLM
- `EMBEDDINGS_PROVIDER=gemini` — Use Gemini for embeddings

**Artifacts:**
- Name: `eval-report-<run-id>`
- Location: `eval-reports/` directory
- Retention: 30 days

## Local Testing

Before pushing, verify workflows will pass:

```bash
# From EC root directory (2TIAO/ENTERPRISE-CHALLENGE)

# Lint
make lint

# Fast tests (no API calls)
make test

# Demo (local Docker)
make demo
```

## Monitoring Workflows

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **CI (Push)** or **Eval (Manual, Full 30 Cases)**
4. Click the workflow run to see logs and status

For **Eval (Manual)** results:
- Scroll to **Artifacts** section
- Download `eval-report-<run-id>` to view the full report locally

## Troubleshooting

### Smoke eval skipped in CI

This is expected if `GOOGLE_API_KEY` is not set. The step is conditional:

```yaml
if: secrets.GOOGLE_API_KEY != ''
```

To enable smoke eval, add `GOOGLE_API_KEY` as a secret.

### Tests fail with "requires_api_key" marker

This indicates a test that requires API credentials. The CI workflow skips these automatically via `-m "not requires_api_key"`. For local testing:

```bash
# Run only fast tests (no API keys needed)
poetry run pytest -v -m "not requires_api_key"

# Run all tests (requires GOOGLE_API_KEY in .env)
poetry run pytest -v
```

### Eval runs out of time

The full eval workflow runs ~30 cases with LLM calls. If it exceeds GitHub's 6-hour job limit, consider:
- Splitting eval into multiple smaller jobs
- Increasing timeout in `eval-manual.yml` (currently unlimited, capped by GitHub default)
- Running eval locally via `make eval` and committing results manually

### Artifacts not appearing

Check that the workflow step completed (scroll to end of logs). If `poetry run python -m eval` fails early, the artifact directory may not be created. The workflow captures output via `|| true` to ensure logs are saved even if eval fails.

## Secrets Security Notes

- **Never commit `.env` files** to the repository.
- **Never hardcode API keys** in workflow YAML files.
- Secrets are masked in logs automatically by GitHub.
- Store paid API keys (Gemini, OpenAI) only as GitHub Secrets.
- Render deployment will have its own secret management (see `render.yaml`).

## Next Steps

1. Add secrets to GitHub repository:
   - `GOOGLE_API_KEY` (required)
   - `OPENAI_API_KEY` (optional, for testing)

2. Push a test commit to a branch to verify **CI (Push)** runs.

3. Manually trigger **Eval (Manual)** from the Actions tab to verify full eval works.

4. Check logs and artifacts to confirm workflows are functioning correctly.

---

For more information on the eval system, see `src/backend/eval/README.md` (if present) or the inline comments in `eval/runner.py`.
