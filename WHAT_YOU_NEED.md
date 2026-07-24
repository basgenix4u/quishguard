# 🛡️ QuishGuard — What You Need For Production

## The Simple Answer

**You only need TWO things: Render + Vercel. No extra keys required to start.**

Here's the breakdown:

---

## ✅ REQUIRED (to go live right now)

| What | Service | Cost | Why |
|------|---------|------|-----|
| **Backend hosting** | Render Standard ($25/mo) | $25/mo | Runs FastAPI + PyTorch ML engine |
| **Database** | Render PostgreSQL Starter | $7/mo | Stores scan results & API keys |
| **Storage** | Render Persistent Disk (5GB) | $0.50/mo | Stores uploaded images + heatmaps |
| **Frontend hosting** | Vercel Hobby (FREE) | $0/mo | Serves the Next.js web app |

**Total: ~$32.50/month — and that's everything.**

You deploy, users start scanning, the app works. No API keys, no extra services.

---

## 🎯 OPTIONAL (to make detection better later)

These are **enhancements**, not requirements. The app works without them.

| What | Service | Cost | What It Adds | When To Add |
|------|---------|------|-------------|-------------|
| **Google Safe Browsing** | Google Cloud API | FREE (10K checks/day) | Tier 3 threat intel — checks URLs against Google's malware database | When you want more accurate phishing detection |
| **urlscan.io** | urlscan.io | FREE (100 scans/day) | Tier 2 threat intel — scans suspicious URLs in a sandbox | When you want more URL verification |
| **Custom domain** | Any registrar (Namecheap, GoDaddy) | ~$10/year | Use quishguard.com instead of quishguard.vercel.app | When you want a professional URL |

---

## 📊 How It Works WITHOUT API Keys

```
Image uploaded →
  ├── AI-Image Detection ✅ (always works, no key needed)
  │     EfficientNet-B4 + FFT + Noise analysis
  │
  └── Quishing Detection ✅ (works without keys)
        ├── Tier 1: Local ML classifier ✅ (always runs, no key)
        ├── Tier 2: urlscan.io ❌ (skipped — no key)
        └── Tier 3: Google Safe Browsing ❌ (skipped — no key)
        │
        └── Still gives you a verdict based on Tier 1 alone!
            URL lexical features + brand impersonation + suspicious TLD
```

**Even without API keys, the app detects:**
- ✅ AI-generated/synthetic images (full accuracy)
- ✅ Phishing URL patterns (keyword analysis, entropy, IP addresses, suspicious TLDs)
- ✅ QR code visual tampering (overlay, logo injection, color mods)
- ✅ Brand impersonation URLs (PayPal, Google, Amazon, etc.)

**With API keys added later, you ALSO get:**
- ✅ Google's authoritative malware database check
- ✅ urlscan.io sandbox scan of the actual webpage

---

## 🚀 Step-by-Step: Deploy RIGHT NOW (No Keys Needed)

### 1. Go to https://render.com → Sign up with GitHub

### 2. Create PostgreSQL Database
- New → PostgreSQL → Name: `quishguard-db` → Plan: Starter → Create

### 3. Create Backend Web Service
- New → Web Service → Connect repo: `basgenix4u/quishguard`
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt && bash scripts/render_startup.sh`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Standard (2GB RAM)
- **Disk**: Add 5GB disk → Mount at `/data`
- **Env vars**: Link your PostgreSQL database (DATABASE_URL auto-set)
- Create

### 4. Go to https://vercel.com → Sign up with GitHub

### 5. Deploy Frontend
- New Project → Import `basgenix4u/quishguard`
- **Root Directory**: `frontend`
- **Env var**: `NEXT_PUBLIC_API_URL` = your Render backend URL + `/api/v1`
- Deploy

### 6. Update CORS on Render
- In Render → quishguard-api → Environment
- Add: `CORS_ORIGINS` = your Vercel URL (e.g., `https://quishguard.vercel.app`)
- Save → auto-redeploys

### 7. Done! 🎉
- Open your Vercel URL → upload an image → scan works!

---

## 🔑 Later: Adding Threat Intel Keys (Optional Enhancement)

### Google Safe Browsing (FREE)
1. Go to https://console.cloud.google.com
2. Enable "Safe Browsing API"
3. Create API key
4. In Render → Environment → add `GOOGLE_SAFE_BROWSING_API_KEY`
5. Save → auto-redeploys

### urlscan.io (FREE)
1. Go to https://urlscan.io → Register
2. Get your API key
3. In Render → Environment → add `URLSCAN_API_KEY`
4. Save → auto-redeploys

---

## 💡 Summary

| Question | Answer |
|----------|--------|
| **Do I need API keys to launch?** | **NO.** The app works fully without them. |
| **Do I need Render + Vercel?** | **YES.** That's your hosting. ~$32.50/month. |
| **Can I add keys later?** | **YES.** Just add env vars in Render dashboard. Auto-applies. |
| **What if I want free hosting first?** | Use Render Free plan (512MB RAM, slow ML). $0 for testing. |
| **What about storage?** | Render persistent disk (5GB, $0.50/mo). Or upgrade later. |
