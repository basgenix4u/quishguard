# 🛡️ QuishGuard — HOW TO USE

Complete guide to running and using QuishGuard on your machine.

---

## 📋 Prerequisites

You need these installed on your computer:

| Requirement | Install | Check |
|-------------|---------|-------|
| **Python 3.11+** | [python.org](https://python.org) | `python3 --version` |
| **Node.js 20+** | [nodejs.org](https://nodejs.org) | `node --version` |
| **Git** | [git-scm.com](https://git-scm.com) | `git --version` |
| **libzbar** (Linux) | `sudo apt install libzbar0` | — |
| **PostgreSQL** (optional) | [postgresql.org](https://postgresql.org) | `psql --version` |

> ⚡ **SQLite fallback works automatically** — you don't need PostgreSQL for local use.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/basgenix4u/quishguard.git
cd quishguard
```

### Step 2: Start the Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows

# Install all dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
✅ Using SQLite fallback: quishguard_local.db
✅ Database tables initialized
Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start the Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

You should see:
```
✓ Ready in 2s
http://localhost:3000
```

### Step 4: Open the App

Go to **http://localhost:3000** in your browser.

---

## 🖥️ Using the Web Interface

### Upload & Scan an Image

1. Open **http://localhost:3000**
2. **Drag & drop** an image, **paste** from clipboard, or **click to browse**
3. Choose scan options:
   - ✅ **AI-Image Detection** — detects if image is AI-generated
   - ✅ **QR Phishing Detection** — detects quishing attacks in QR codes
4. Click **"🛡️ Scan Image"**
5. View your results:
   - **AI Verdict**: REAL / FAKE / UNCERTAIN with confidence %
   - **Frequency Anomaly Score**: how unnatural the frequency spectrum is
   - **Noise Inconsistency Score**: how inconsistent the noise patterns are
   - **Artifact Heatmap**: visual map of suspicious regions
   - **QR Analysis**: decoded URL + phishing risk if QR code found

### View Scan History & Statistics

1. Click **"History"** in the navigation bar
2. See:
   - **4 stat cards** (total scans, AI-generated count, QR detected, quishing threats)
   - **Bar chart** of scan breakdown
   - **Pie charts** for AI verdict and quishing verdict distributions
   - **Paginated table** of all past scans

### View Individual Scan Detail

1. Click **"View"** button next to any scan in the history table
2. Or go directly to `http://localhost:3000/scan/{scan_id}`
3. See the full AI-Image report and Quishing report

---

## 🔗 Using the REST API Directly

The backend runs at **http://localhost:8000** with full Swagger docs at **http://localhost:8000/docs**.

### Submit a Scan

```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -F "file=@my_image.png" \
  -F 'scan_options={"ai_check": true, "qr_check": true}'
```

**Response (201 Created):**
```json
{
  "id": "59b4a0e8-3d4a-4755-a79f-f0ef6630c6df",
  "status": "completed",
  "image_hash": "sha256:75de4b...",
  "ai_image_analysis": {
    "verdict": "fake",
    "confidence": 0.89,
    "details": {
      "frequency_score": 0.90,
      "noise_score": 1.0,
      "artifact_heatmap_url": "/api/v1/scans/{id}/heatmap"
    }
  },
  "qr_analysis": {
    "qr_detected": false,
    "decoded_url": null,
    "quishing_verdict": null,
    "quishing_confidence": null,
    "details": { ... }
  },
  "created_at": "2026-07-24T19:53:24.185826Z"
}
```

### Get Scan by ID

```bash
curl http://localhost:8000/api/v1/scans/59b4a0e8-3d4a-4755-a79f-f0ef6630c6df
```

### Get Dashboard Stats

```bash
curl http://localhost:8000/api/v1/scans/stats
```

### Get Scan History (Paginated)

```bash
# Basic history
curl http://localhost:8000/api/v1/scans/history

# With filters
curl "http://localhost:8000/api/v1/scans/history?ai_verdict=fake&page=1&per_page=10"
```

### Get Artifact Heatmap Image

```bash
curl http://localhost:8000/api/v1/scans/{scan_id}/heatmap --output heatmap.png
```

### Create an API Key (for integration)

```bash
# First create a key manually via the DB or use the endpoint
# Then use it in subsequent requests:
curl -H "X-API-Key: qg_live_your_key_here" \
  http://localhost:8000/api/v1/scans/history
```

---

## 🐳 Using Docker (Production Deployment)

### One-command deployment:

```bash
docker-compose up --build
```

This starts 3 services:
- **PostgreSQL** on port 5432
- **FastAPI backend** on port 8000
- **Next.js frontend** on port 3000

### Access:
- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000/docs**

---

## 🧪 Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all 16 tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

Expected output:
```
16 passed in 2.18s ✅
```

---

## 📊 Understanding the Results

### AI-Image Detection Scores

| Score | Meaning |
|-------|---------|
| **Verdict: REAL** | Image appears to be an authentic photograph |
| **Verdict: FAKE** | Image shows strong AI-generation artifacts |
| **Verdict: UNCERTAIN** | Cannot confidently classify — borderline |
| **Frequency Score > 0.7** | Unusual frequency spectrum (GAN/diffusion artifact) |
| **Noise Score > 0.7** | Inconsistent noise patterns across image regions |
| **Confidence > 0.8** | Strong classification confidence |

### Quishing Detection Scores

| Score | Meaning |
|-------|---------|
| **Verdict: SAFE** | URL appears legitimate, no threat intel flags |
| **Verdict: SUSPICIOUS** | Some risk indicators detected |
| **Verdict: MALICIOUS** | High phishing probability, threat intel confirms |
| **URL Lexical Score** | ML classifier probability based on URL string features |
| **Visual Tampering Score** | QR code has visual modifications (overlay, logo injection) |
| **Google Safe Browsing: MALICIOUS** | URL is in Google's threat database |

---

## 🔧 Configuration

Edit `backend/.env` to customize:

```bash
# Optional: Enable Google Safe Browsing (Tier 3 threat intel)
GOOGLE_SAFE_BROWSING_API_KEY=your_api_key_here

# Optional: Enable urlscan.io enhanced scanning
URLSCAN_API_KEY=your_urlscan_key_here

# File upload limit
MAX_FILE_SIZE_MB=10

# Database (auto-detects, falls back to SQLite)
DATABASE_URL=postgresql+asyncpg://quishguard:quishguard_dev@localhost:5432/quishguard_db
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError: No module named 'asyncpg'" | `pip install asyncpg` — or SQLite will auto-fallback |
| "Unable to find zbar shared library" | `sudo apt install libzbar0` (Linux) or `brew install zbar` (Mac) |
| "Connection refused on port 8000" | Make sure backend is running: `uvicorn app.main:app --port 8000` |
| Frontend shows "Network error" | Ensure backend is running AND `NEXT_PUBLIC_API_URL` is set correctly |
| Large Docker build fails | Use CPU-only PyTorch: the Dockerfile handles this automatically |

---

**You're ready! Start scanning images and QR codes for threats.** 🛡️
