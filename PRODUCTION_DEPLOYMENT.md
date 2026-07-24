# 🛡️ QuishGuard — Production Deployment Guide

## Complete guide to deploying on **Render** (backend) + **Vercel** (frontend)

---

## 🗺️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                      │
│                                                         │
│  ┌─────────────────┐     ┌──────────────────────┐       │
│  │  Vercel (Free)   │     │  Render ($32/month)  │       │
│  │  Next.js Frontend│────▶│  FastAPI Backend     │       │
│  │  quishguard.app  │     │  quishguard-api      │       │
│  └─────────────────┘     │                      │       │
│                          │  ├─ PostgreSQL ($7)   │       │
│                          │  ├─ Persistent Disk   │       │
│                          │  │  ($0.50 for 5GB)   │       │
│                          │  ├─ PyTorch ML Engine │       │
│                          │  └────────────────────│       │
│                          └──────────────────────┘       │
│                                                         │
│  Total cost: ~$32.50/month                              │
│  Free tier available for testing!                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Cost Breakdown

| Service | Plan | Cost | What It Provides |
|---------|------|------|-----------------|
| **Vercel** | Hobby (Free) | $0/mo | Next.js hosting, CDN, auto-deploy |
| **Render PostgreSQL** | Starter | $7/mo | Managed PostgreSQL 15 database |
| **Render Web Service** | Standard | $25/mo | 2GB RAM (needed for PyTorch) |
| **Render Persistent Disk** | 5GB | $0.50/mo | Uploads + ML model weights storage |
| **Total** | — | **~$32.50/mo** | Full production stack |

> 💡 **Free tier option**: Use Render Free plan (512MB RAM) + SQLite. PyTorch will run but slowly. Good for testing before upgrading.

---

## 🚀 Step-by-Step Deployment

### STEP 1: Push Code to GitHub

Your code is already on GitHub at:
```
https://github.com/basgenix4u/quishguard
```

If you made changes locally, push them:
```bash
cd quishguard
git add -A
git commit -m "production deployment configs"
git push origin main
```

---

### STEP 2: Deploy Backend on Render

#### 2A. Create Render Account
1. Go to **https://render.com**
2. Sign up with your GitHub account

#### 2B. Create PostgreSQL Database
1. In Render Dashboard → **New** → **PostgreSQL**
2. Settings:
   - **Name**: `quishguard-db`
   - **Plan**: Starter ($7/month)
   - **Region**: Oregon (or closest to your users)
   - **PostgreSQL Version**: 15
3. Click **Create Database**
4. Wait ~2 minutes for it to provision
5. Copy the **Internal Database URL** (you'll need it later)

#### 2C. Create Backend Web Service
1. In Render Dashboard → **New** → **Web Service**
2. Settings:
   - **Name**: `quishguard-api`
   - **Runtime**: Python
   - **Plan**: Standard ($25/month) — **IMPORTANT: you need 2GB RAM for PyTorch**
   - **Region**: Oregon (same as your database)
   - **Branch**: main
   - **Root Directory**: `backend` ← **IMPORTANT!**
   - **Build Command**: `pip install -r requirements.txt && bash scripts/render_startup.sh`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. Add Environment Variables (click **Advanced** → **Add Environment Variable**):

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | *(auto from database)* | Click "From Database" → select quishguard-db |
| `SECRET_KEY` | *(auto-generated)* | Click "Generate Value" |
| `UPLOAD_DIR` | `/data/uploads` | Points to persistent disk |
| `AI_DETECTOR_MODEL_PATH` | `/data/models_pretrained/ai_detector_efficientnet_b4.pt` | Persistent disk path |
| `URL_CLASSIFIER_MODEL_PATH` | `/data/models_pretrained/url_classifier_xgboost.pkl` | Persistent disk path |
| `QR_TAMPERING_MODEL_PATH` | `/data/models_pretrained/qr_tampering_resnet18.pt` | Persistent disk path |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Your Vercel URL (set later) |
| `DEBUG` | `false` | Production mode |
| `PORT` | *(auto by Render)* | Don't set this — Render provides it |

4. Add **Persistent Disk**:
   - Click **Add Disk**
   - **Name**: `quishguard-data`
   - **Mount Path**: `/data`
   - **Size**: 5GB ($0.50/month)

5. Click **Create Web Service**

6. Wait ~5-10 minutes for first build and deploy

7. Once deployed, note your **backend URL**: 
   ```
   https://quishguard-api.onrender.com
   ```

---

### STEP 3: Deploy Frontend on Vercel

#### 3A. Create Vercel Account
1. Go to **https://vercel.com**
2. Sign up with your GitHub account

#### 3B. Import Project
1. In Vercel Dashboard → **Add New** → **Project**
2. Import from GitHub: **basgenix4u/quishguard**
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` ← **IMPORTANT!** Click "Edit" and set this
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (default)

4. Add Environment Variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://quishguard-api.onrender.com/api/v1` (your Render backend URL)

5. Click **Deploy**

6. Wait ~2-3 minutes for first build

7. Note your **frontend URL**:
   ```
   https://quishguard.vercel.app
   ```

---

### STEP 4: Connect Frontend → Backend (Update CORS)

1. Go back to **Render Dashboard** → `quishguard-api` → **Environment**
2. Update `CORS_ORIGINS` to your actual Vercel URL:
   ```
   https://quishguard.vercel.app
   ```
3. Save → Render will auto-redeploy

4. Verify the connection:
   ```bash
   # Test backend health
   curl https://quishguard-api.onrender.com/health
   
   # Test scan endpoint
   curl -X POST https://quishguard-api.onrender.com/api/v1/scans \
     -F "file=@test_image.png" \
     -F 'scan_options={"ai_check": true, "qr_check": true}'
   ```

---

### STEP 5: (Optional) Add Threat Intel API Keys

For maximum detection accuracy, add these in Render → Environment:

| Key | Where to Get | Cost |
|-----|-------------|------|
| `GOOGLE_SAFE_BROWSING_API_KEY` | https://console.cloud.google.com → Safe Browsing API | Free (10K req/day) |
| `URLSCAN_API_KEY` | https://urlscan.io → Register | Free (100 scans/day) |

---

## 🔄 Auto-Deploy Setup

Both Render and Vercel **auto-deploy on every git push**:

```bash
# Make a change, push, and both services update automatically
git add -A
git commit -m "update: new feature"
git push origin main
```

- **Vercel** deploys in ~1-2 minutes
- **Render** deploys in ~3-5 minutes

---

## 🗄️ Storage Architecture

### What Gets Stored Where

| Data Type | Location | Persistence |
|-----------|----------|-------------|
| **Scan results** | PostgreSQL database | ✅ Permanent (managed by Render) |
| **Uploaded images** | `/data/uploads/` (persistent disk) | ✅ Permanent (5GB disk) |
| **Heatmap images** | `/data/uploads/heatmaps/` (persistent disk) | ✅ Permanent |
| **ML model weights** | `/data/models_pretrained/` (persistent disk) | ✅ Permanent |
| **API keys** | PostgreSQL database | ✅ Permanent |

### Upgrading Storage

If you exceed 5GB:
1. In Render Dashboard → `quishguard-api` → **Disks**
2. Click **Edit** → increase size (max 100GB at $10/GB/month)
3. Or switch to **Cloudflare R2** (S3-compatible, $0.015/GB/month) — much cheaper for large volumes

---

## 📈 Scaling Options

### When You Need More Power

| Scenario | Action | Cost |
|----------|--------|------|
| **More users** | Upgrade Render to Pro ($85/mo, 4GB RAM) | $85/mo |
| **Faster scans** | Pre-train ML models and upload weights | Free (one-time) |
| **Large storage** | Switch to Cloudflare R2 or AWS S3 | ~$1/mo for 50GB |
| **High traffic** | Add Render worker instances | Variable |
| **Custom domain** | Add domain in Vercel + Render settings | Free (if you own domain) |

---

## 🔒 Security Checklist

Before going live, ensure these are set:

- [ ] `DEBUG=false` in Render environment
- [ ] `SECRET_KEY` is auto-generated (not default value)
- [ ] `CORS_ORIGINS` only includes your Vercel URL
- [ ] PostgreSQL database is on internal network (Render does this automatically)
- [ ] API keys are hashed (our code does this automatically)
- [ ] File upload validation (10MB limit, file type check — our code handles this)

---

## 🧪 Post-Deployment Verification

After everything is deployed, run these checks:

```bash
# 1. Backend health check
curl https://quishguard-api.onrender.com/health
# Expected: {"status": "healthy", "version": "0.1.0"}

# 2. Swagger docs accessible
# Open: https://quishguard-api.onrender.com/docs

# 3. Scan endpoint works
curl -X POST https://quishguard-api.onrender.com/api/v1/scans \
  -F "file=@test_image.png" \
  -F 'scan_options={"ai_check": true, "qr_check": true}'
# Expected: JSON response with verdict, confidence, etc.

# 4. Frontend loads
# Open: https://quishguard.vercel.app
# Expected: QuishGuard scanner UI

# 5. Frontend → Backend connection
# Upload an image on the frontend, verify results appear
```

---

## ❓ Troubleshooting Production Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Backend returns 500 | PostgreSQL not connected | Check DATABASE_URL env var in Render |
| Frontend shows "Network error" | CORS blocked or wrong API URL | Update NEXT_PUBLIC_API_URL in Vercel, CORS_ORIGINS in Render |
| PyTorch OOM error | RAM too low (Free plan = 512MB) | Upgrade to Standard plan (2GB RAM) |
| Images not persisting | Upload path wrong | Set UPLOAD_DIR=/data/uploads in Render |
| ML models not loading | Model path wrong | Set model paths to /data/models_pretrained/... |
| Build fails on Render | Missing libzbar | Add `apt-get install libzbar0` to build script |
| Build fails on Vercel | Missing dependency | Run `npm install` locally first |

---

## 💡 Alternative: All-in-One Render Deployment

If you prefer to keep everything on Render (no Vercel):

1. Create a **Static Site** on Render for the frontend:
   - Build Command: `cd frontend && npm install && npm run build && npm run export`
   - Publish Directory: `frontend/out`

2. Both backend and frontend on Render, same domain.

> ⚠️ Vercel is better for Next.js because it's built by the same team and has superior CDN/edge deployment.

---

## 🏷️ Custom Domain Setup

To use your own domain (e.g., `quishguard.yourdomain.com`):

### Vercel (Frontend)
1. Vercel Dashboard → Project → **Settings** → **Domains**
2. Add your domain → follow DNS instructions

### Render (Backend)
1. Render Dashboard → `quishguard-api` → **Settings**
2. Add custom domain → follow DNS instructions

---

**Your production URL structure:**
- Frontend: `https://quishguard.yourdomain.com`
- Backend: `https://api.quishguard.yourdomain.com` (or keep `quishguard-api.onrender.com`)
