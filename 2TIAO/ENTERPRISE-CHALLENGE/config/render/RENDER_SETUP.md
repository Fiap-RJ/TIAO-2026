# Genera Intelligence — Render Deployment Guide

This guide walks through deploying Genera Intelligence on [Render](https://render.com), a cloud platform that automatically reads `render.yaml` from your repository.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Deployment](#step-by-step-deployment)
3. [Environment Variables](#environment-variables)
4. [Adding PostgreSQL (Optional)](#adding-postgresql-optional)
5. [Enabling PaddleOCR (Optional)](#enabling-paddleocr-optional)
6. [Troubleshooting](#troubleshooting)
7. [Cost Estimation](#cost-estimation)

---

## Prerequisites

- **GitHub account** with the Genera Intelligence repository pushed to a public or private repo
- **Render account** (create free at https://render.com)
- **API keys** ready to paste:
  - Google Gemini API key (https://aistudio.google.com/apikey)
  - OpenAI API key (optional, https://platform.openai.com/account/api-keys)
  - AWS credentials (only if using Textract for OCR)

---

## Step-by-Step Deployment

### Step 1: Connect GitHub to Render

1. Go to [Render Dashboard](https://render.com/dashboard)
2. Click **"New +"** → **"Blueprint"**
3. (If prompted) Authenticate with GitHub
4. Select your Genera Intelligence repository
5. Render auto-detects `render.yaml` at the repo root
6. Review the three services:
   - `genera-backend` (FastAPI, port 8000)
   - `genera-frontend` (React + Nginx, port 80)
   - `genera-paddle-ocr` (optional, port 8001)

### Step 2: Configure Environment Variables

Before clicking "Deploy", set the secrets. Render shows a form with all variables from `render.yaml`.

#### Required Secrets

1. **GOOGLE_API_KEY** (required for Gemini provider)
   - Go to https://aistudio.google.com/apikey
   - Click "Create API Key"
   - Paste the key in Render's environment form

2. **OCR_TOKEN** (required for /api/ocr/ endpoint)
   - Generate a strong random string (e.g., `openssl rand -hex 32`)
   - Paste in Render's environment form
   - Save this token; you'll need it to call the OCR endpoint

#### Optional Secrets

- **OPENAI_API_KEY** (only if `LLM_PROVIDER=openai`)
  - Get from https://platform.openai.com/account/api-keys
  - Set on Render if using OpenAI models

- **AWS_ACCESS_KEY_ID** + **AWS_SECRET_ACCESS_KEY** (only if `OCR_PROVIDER=textract`)
  - Get from AWS IAM console
  - Set on Render if using Textract for document OCR

### Step 3: Review Service Settings

Render displays each service's configuration:

| Service | Port | Start Time | Disk |
|---------|------|-----------|------|
| genera-backend | 8000 | ~2min (FAISS seeding) | 2 GB |
| genera-frontend | 80 | ~1min | none |
| genera-paddle-ocr | 8001 | ~3min (model download) | 3 GB |

### Step 4: Deploy

1. Click **"Create Blueprint"** or **"Deploy"**
2. Render provisions the services and starts building Docker images
3. Check the logs:
   - **Backend log**: Watch for "Índice FAISS gerado" → service healthy
   - **Frontend log**: Watch for "nginx" startup → service healthy
   - **PaddleOCR log** (if enabled): Watch for "Uvicorn running" → service healthy

### Step 5: Verify Deployment

Once all services are green (healthy):

1. **Backend health check**
   ```bash
   curl https://genera-backend.onrender.com/health
   ```
   Expected response:
   ```json
   {"status": "healthy"}
   ```

2. **Frontend access**
   - Go to `https://genera-frontend.onrender.com`
   - You should see the Genera Intelligence chat interface

3. **Chat endpoint test**
   ```bash
   curl -X POST https://genera-backend.onrender.com/api/chat/ \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "query": "What is my genetic risk?"}'
   ```

4. **OCR endpoint test** (if PaddleOCR enabled)
   ```bash
   curl -X POST https://genera-paddle-ocr.onrender.com/ocr/ \
     -H "Authorization: Bearer YOUR_OCR_TOKEN" \
     -F "file=@report.pdf"
   ```

---

## Environment Variables

### Backend (`genera-backend`)

All backend configuration is in `config/render/backend.env` (template) and set on Render dashboard.

#### Critical Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | Provider: `gemini` or `openai` |
| `GOOGLE_API_KEY` | (secret) | Google Gemini API key |
| `OCR_PROVIDER` | `paddle_local` | OCR: `paddle_local` or `textract` |
| `OCR_TOKEN` | (secret) | Bearer token for /api/ocr/ |
| `DB_TYPE` | `sqlite` | Database: `sqlite` or `postgres` |

#### Changing Variables

1. Go to Render dashboard → genera-backend → Settings → Environment
2. Edit the variable (or add a new one)
3. Click "Save"
4. Render auto-redeploys the service (takes ~5–10 min)

**Note:** If you change `EMBEDDINGS_PROVIDER` or `EMBEDDINGS_MODEL`, the FAISS index becomes invalid. You'll need to manually trigger a rebuild (Push to GitHub or manually trigger deploy).

### Frontend (`genera-frontend`)

Frontend environment variables are in `config/render/frontend.env` (template).

The frontend communicates with the backend via:
- **Nginx reverse proxy** (in frontend container) forwards `/api/*` to `genera-backend:8000`
- **Frontend code** calls `POST /api/chat/` (relative path, reverse-proxied by Nginx)

No additional frontend env vars typically needed; frontend auto-discovers backend via internal DNS.

---

## Adding PostgreSQL (Optional)

By default, Genera uses SQLite (`DB_TYPE=sqlite`) which persists to `/app/data/history.db` on the backend's disk.

For production, use PostgreSQL:

### Enable PostgreSQL Add-on

1. Go to Render dashboard → genera-backend → Settings
2. Scroll to "Add-ons" section
3. Click "Create add-on" → Select "PostgreSQL"
4. Render provisions a managed PostgreSQL database
5. Auto-generates `DATABASE_URL` environment variable

### Link PostgreSQL to Backend

1. Go to genera-backend → Settings → Environment
2. Find `DATABASE_URL` (auto-generated by Render)
3. Copy the value (should be `postgresql://user:password@host:5432/database`)
4. Set `DB_TYPE=postgres`
5. Click "Save"

### Initialize Database Schema

On first connection, the backend automatically creates tables via SQLAlchemy. No manual migration needed.

To verify:
```bash
# Inside backend container or via psql:
psql $DATABASE_URL
\dt  # List tables (should see "chat_history" and others)
```

---

## Enabling PaddleOCR (Optional)

By default, the PaddleOCR service is disabled (it's marked with `profiles: [ocr]` in `render.yaml`).

### Enable PaddleOCR Service

1. Go to Render dashboard → "New +" → "Blueprint"
2. Re-deploy from GitHub (Render re-reads `render.yaml`)
3. Before clicking "Deploy", uncheck the **"Skip genera-paddle-ocr"** option (if shown)
4. Or manually edit the backend's `OCR_PROVIDER=paddle_local` and trigger a redeploy

### Verify PaddleOCR Health

```bash
curl https://genera-paddle-ocr.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test OCR Endpoint

```bash
curl -X POST https://genera-paddle-ocr.onrender.com/ocr/ \
  -H "Authorization: Bearer YOUR_OCR_TOKEN" \
  -F "file=@genetic_report.pdf"
```

---

## Troubleshooting

### Backend stuck in "Building" or "Deploying"

**Cause:** FAISS index seeding is taking too long.

**Fix:**
1. Check logs: Render dashboard → genera-backend → Logs
2. Look for "Índice FAISS" messages
3. If seeding takes >30 min, the data file may be too large
4. Consider using a smaller test dataset for initial deployment

### Backend health check failing

**Cause:** Backend is crashing or not responding to `/health`.

**Fix:**
1. Check logs for errors (Python exceptions, etc.)
2. Verify `GOOGLE_API_KEY` is set and valid
3. Verify `/health` endpoint is not blocked by firewall (unlikely on Render)

### Frontend not connecting to backend

**Cause:** Nginx reverse proxy misconfigured or backend not healthy.

**Fix:**
1. Check frontend Nginx config: `src/frontend/nginx.conf`
2. Verify backend is healthy: `curl https://genera-backend.onrender.com/health`
3. Check frontend logs for errors

### OCR endpoint returns 401 Unauthorized

**Cause:** Bearer token missing or incorrect.

**Fix:**
```bash
# Correct usage:
curl -X POST https://genera-paddle-ocr.onrender.com/ocr/ \
  -H "Authorization: Bearer YOUR_OCR_TOKEN" \
  -F "file=@report.pdf"

# Your OCR_TOKEN was set during deployment.
# If you forgot it, regenerate:
# - Go to Render dashboard → genera-paddle-ocr → Settings → Environment
# - Update OCR_TOKEN to a new value
# - Save and redeploy
```

### FAISS index not found / seeding failed

**Cause:** Data file missing or corrupted.

**Fix:**
1. Verify `proposta_estrutura_de_dados.json` exists at EC root
2. Check backend logs for FAISS seeding errors
3. If index is corrupted, delete it from Render disk:
   - Go to genera-backend → "Delete Disk" (careful: deletes all data)
   - Redeploy; backend will reseed the index

### Out of memory during FAISS seeding

**Cause:** Vector store is too large for free/starter tier.

**Fix:**
1. Upgrade backend to higher Render plan (Standard or Pro)
2. Or reduce the data size (subset of genetic markers)
3. Or increase disk size to allow index caching

---

## Cost Estimation

**Render Pricing** (as of 2024):
- **Web Services (compute)**: $7/month per service (starter plan)
- **Disks (storage)**: $0.25/GB/month
- **PostgreSQL** (managed): $12/month (starter)
- **Bandwidth**: First 100 GB/month free; $0.10/GB after

### Example Configuration

| Component | Cost |
|-----------|------|
| Backend service (starter) | $7 |
| Frontend service (starter) | $7 |
| PaddleOCR service (if enabled) | $7 |
| Backend disk (2 GB) | $0.50 |
| PaddleOCR disk (3 GB) | $0.75 |
| PostgreSQL (if enabled) | $12 |
| **Total** (all services + PostgreSQL) | **~$34/month** |
| **Minimal** (backend + frontend, SQLite) | **~$14/month** |

---

## Next Steps

1. **Post-Deployment**: Update `document/script-video-sprint4.md` with Render URLs for demo recording
2. **GitHub Actions**: Set up CI/CD workflow in `.github/workflows/` to auto-deploy on push
3. **Monitoring**: Configure Render alerts for service health
4. **Custom Domain**: (Optional) Bind your domain to Render services

For support, consult:
- Render docs: https://render.com/docs
- Genera Intelligence architecture: `document/arquitetura.md`
- Backend README: `src/backend/README.md`

