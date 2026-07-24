# QuishGuard — Master Task Board

## 🛑 STAGE 1: PRODUCT DEFINITION & SYSTEM ARCHITECTURE
- [x] Draft PRD with user stories and feature scope
- [x] Define system architecture and tech stack
- [x] Design database schema
- [x] Define API contracts
- [x] Create master task board
- [x] Get stakeholder approval ← **APPROVED**

## 🛑 STAGE 2: ENVIRONMENT SETUP & CORE CONFIGURATION
- [x] Initialize project directory structure
- [x] Write backend requirements.txt and config files
- [x] Write frontend package.json and config files
- [x] Create .env.example and .gitignore
- [x] Install all backend dependencies
- [x] Install all frontend dependencies
- [x] Create FastAPI smoke-test "Hello World" route
- [x] Verify backend with curl check
- [x] Create Next.js smoke-test page
- [x] Get stakeholder approval

## 🚀 STAGE 3: BACKEND ENGINE DEVELOPMENT
- [x] Set up PostgreSQL connection and async SQLAlchemy engine
- [~] Create Alembic migration for initial schema
- [ ] Implement ORM models (Scan, ApiKey)
- [ ] Implement Pydantic schemas
- [ ] Implement API key auth dependency
- [ ] Implement rate limiting dependency
- [ ] Build ML module: EfficientNet-B4 classifier wrapper
- [ ] Build ML module: FFT frequency analyzer
- [ ] Build ML module: Noise inconsistency analyzer
- [ ] Build ML module: URL lexical classifier (XGBoost)
- [ ] Build ML module: QR tampering detector (ResNet-18)
- [ ] Build threat intel: Local heuristics engine
- [ ] Build threat intel: urlscan.io client
- [ ] Build threat intel: Google Safe Browsing client
- [ ] Build threat intel: Three-tier aggregator
- [ ] Build service: QR extractor (OpenCV + pyzbar)
- [ ] Build service: AI image detector (ensemble)
- [ ] Build service: Quishing detector (multimodal)
- [ ] Build service: Unified scanner orchestrator
- [ ] Build API endpoint: POST /scans
- [ ] Build API endpoint: GET /scans/{id}
- [ ] Build API endpoint: GET /scans/{id}/heatmap
- [ ] Build API endpoint: GET /scans/history
- [ ] Build API endpoint: GET /scans/stats
- [ ] Build API endpoint: POST /api-keys
- [ ] Build API endpoint: GET /api-keys
- [ ] Build training script: download_datasets.py
- [ ] Build training script: train_ai_detector.py
- [ ] Build training script: train_url_classifier.py
- [ ] Write unit tests for AI detector service
- [ ] Write unit tests for QR extractor service
- [ ] Write unit tests for quishing detector service
- [ ] Write unit tests for scan API endpoints
- [ ] Run full test suite and fix any failures

## 🚀 STAGE 4: FRONTEND UI & INTEGRATION
- [ ] Set up shadcn/ui component library
- [ ] Build Navbar and layout components
- [ ] Build ImageUploader component (drag-drop + paste)
- [ ] Build ScanResultCard component
- [ ] Build AIImageReport component (verdict, confidence, heatmap)
- [ ] Build QuishingReport component (decoded URL, verdict, threat intel)
- [ ] Build ArtifactHeatmap component
- [ ] Build ScanHistoryTable with pagination & filters
- [ ] Build StatsOverview dashboard with Recharts
- [ ] Build API documentation page
- [ ] Wire API client (lib/api.ts) to backend
- [ ] Implement scan page with real-time upload flow
- [ ] Implement scan/[id] result detail page
- [ ] Implement history page with filters
- [ ] Run frontend build check (zero TS errors)
- [ ] End-to-end integration test

## 🚀 STAGE 5: DEVOPS, DEPLOYMENT & DELIVERY
- [ ] Write backend Dockerfile (multi-stage)
- [ ] Write frontend Dockerfile (multi-stage)
- [ ] Write docker-compose.yml (api, web, db)
- [ ] Write professional README.md
- [ ] Final codebase cleanup and lint check
- [ ] Deliver final codebase
