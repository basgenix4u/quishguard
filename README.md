# 🛡️ QuishGuard

**Multimodal Deep Learning Framework for Detecting AI-Generated Images and QR Phishing (Quishing)**

---

## 🔬 Overview

QuishGuard is a unified cybersecurity analysis platform that detects two of the most emerging digital threats:

1. **AI-Generated / Synthetic Image Detection** — Identifies deepfakes, GAN outputs, and diffusion-model imagery using an ensemble of EfficientNet-B4 deep classification, FFT frequency-domain analysis, and noise inconsistency mapping.

2. **QR Phishing (Quishing) Detection** — Decodes QR codes and analyzes embedded URLs through a three-tier threat intelligence pipeline (local ML → urlscan.io → Google Safe Browsing) combined with visual tampering detection.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖼️ **AI-Image Detection** | EfficientNet-B4 classifier + FFT frequency analysis + noise inconsistency mapping with artifact heatmaps |
| 🛡️ **Quishing Detection** | QR code extraction, URL lexical analysis, visual tampering detection, 3-tier threat intel |
| 🔗 **Unified Scan Pipeline** | Single upload → auto-routes through both pipelines → combined threat report |
| 📊 **Dashboard & Statistics** | Scan history, verdict distributions, risk breakdowns with interactive charts |
| 🔑 **API Key Auth** | RESTful API with key-based auth and rate limiting for integration into security pipelines |
| 🗄️ **Dual Database** | Auto-detect PostgreSQL (production) / SQLite (local dev) |
| 🧪 **16 Unit Tests** | Full test coverage for ML services and API endpoints |

---

## 🏗️ System Architecture

```
┌──────────────────────┐
│   Next.js Frontend    │  React 18 + Tailwind + Recharts
│   (Port 3000)         │  Drag-drop upload, scan results, dashboard
└───────────┬──────────┘
            │ HTTP API
┌───────────▼──────────┐
│   FastAPI Backend     │  Pydantic v2, async SQLAlchemy
│   (Port 8000)         │  7 REST endpoints + Swagger docs
└───────────┬──────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼───┐     ┌────▼────┐
│  ML   │     │Database │     PostgreSQL 15 (prod)
│Engine │     │Layer    │     SQLite (dev fallback)
│       │     │         │
│•EffB4 │     │scans    │
│•FFT   │     │api_keys │
│•Noise │     └─────────┘
│•URL   │
│•QR    │
│•Threat│
│Intel  │
└───────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | FastAPI, Pydantic v2, Uvicorn, async SQLAlchemy 2.0 |
| **ML/DL** | PyTorch 2.x, EfficientNet-B4, XGBoost, scikit-learn, OpenCV, pyzbar |
| **Database** | PostgreSQL 15 (production) / SQLite (local dev) |
| **Threat Intel** | Google Safe Browsing, urlscan.io, local heuristic ML |
| **Auth** | API-key based, rate limiting (slowapi) |
| **Deployment** | Docker, docker-compose |

---

## 📂 Project Structure

```
quishguard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── dependencies.py      # Auth, rate limiting, validation
│   │   ├── api/endpoints/       # Scan, history, auth routes
│   │   ├── models/              # ORM models (Scan, ApiKey)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic services
│   │   └── ml/                  # ML/DL engine modules
│   │       ├── threat_intel/    # 3-tier aggregator
│   ├── tests/                   # pytest test suite (16 tests)
│   ├── alembic/                 # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   ├── lib/                 # API client, utilities
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml
├── backend.Dockerfile
├── frontend.Dockerfile
├── .env.example
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15 (optional — SQLite fallback works for local dev)

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Install libzbar (for QR decoding)
sudo apt-get install libzbar0  # Linux
# brew install zbar            # macOS

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🔗 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/scans` | Submit image for unified scan | Optional |
| `GET` | `/api/v1/scans/{id}` | Retrieve scan result | No |
| `GET` | `/api/v1/scans/{id}/heatmap` | Get artifact heatmap PNG | No |
| `GET` | `/api/v1/scans/history` | Paginated scan history | No |
| `GET` | `/api/v1/scans/stats` | Dashboard statistics | No |
| `POST` | `/api/v1/api-keys` | Create API key | Required |
| `GET` | `/api/v1/api-keys` | List API keys (masked) | Required |
| `GET` | `/health` | Health check | No |

### Example: Submit a Scan

```bash
curl -X POST http://localhost:8000/api/v1/scans \
  -F "file=@test_image.png" \
  -F 'scan_options={"ai_check": true, "qr_check": true}'
```

### Example: Get Scan Stats

```bash
curl http://localhost:8000/api/v1/scans/stats
```

---

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Access:
# Frontend → http://localhost:3000
# Backend  → http://localhost:8000/docs
```

---

## 🧪 Testing

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v             # Run 16 unit tests
pytest tests/ --cov=app      # Run with coverage
```

---

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:
- `DATABASE_URL` — PostgreSQL connection (auto-falls back to SQLite)
- `GOOGLE_SAFE_BROWSING_API_KEY` — Optional, enables Tier 3 threat intel
- `URLSCAN_API_KEY` — Optional, enhances Tier 2 urlscan.io
- `MAX_FILE_SIZE_MB` — Upload limit (default 10MB)

---

## 📊 ML Pipeline Details

### AI-Image Detection Ensemble

| Component | Weight | Description |
|-----------|--------|-------------|
| EfficientNet-B4 Classifier | 55% | Deep CNN with 2-class (real/fake) head |
| FFT Frequency Analysis | 25% | Spectral decay, periodic spikes, HF energy |
| Noise Inconsistency | 20% | Local variance/kurtosis patch analysis |

### Quishing Detection (Three-Tier Threat Intel)

| Tier | Source | Weight | Activation |
|------|--------|--------|------------|
| 1 | Local Heuristic ML (XGBoost) | 30% | Always (<5ms) |
| 2 | urlscan.io | 30% | If Tier 1 score > 0.3 |
| 3 | Google Safe Browsing | 40% | If any score > 0.5 |

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

**Built by AI Software Factory** • [GitHub Repository](https://github.com/basgenix4u/quishguard)
