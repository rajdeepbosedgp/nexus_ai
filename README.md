# NEXUS — Society Maintenance Tracker & Emergent Intelligence

> NEXUS is a society maintenance platform with a signature intelligence layer that discovers emergent operational patterns across complaint categories using sentence embeddings and density-based clustering, with every pattern mathematically scored and fully traceable to underlying complaint records.

---

## 🔗 Live Links & Repository

* **GitHub Repository:** [https://github.com/rajdeepbosedgp/nexus_ai](https://github.com/rajdeepbosedgp/nexus_ai)
* **Live Production Frontend (Vercel):** [https://nexus-ai-rb-b912.vercel.app](https://nexus-ai-rb-b912.vercel.app)
* **Live Production Backend (Render):** [https://nexus-backend-hq86.onrender.com](https://nexus-backend-hq86.onrender.com)
* **Live Interactive API Docs (Swagger):** [https://nexus-backend-hq86.onrender.com/docs](https://nexus-backend-hq86.onrender.com/docs)

---

## Core Purpose & Key Features

NEXUS bridges the gap between traditional siloed complaint ticketing and proactive society infrastructure management. Instead of treating complaints in isolation, NEXUS discovers hidden structural issues (e.g., rainwater seepage causing electrical shorts and wall dampness across multiple floors) that span across separate maintenance categories.

### Key Capabilities
- **Resident Portal**: Submit complaints with category selection, description, weather metadata, and **real image photo file upload** (with 5 MB file size and MIME type validation). Track complaint resolution and view society notices.
- **Admin Dashboard**: Priority-driven dashboard featuring an **Overdue Risk Score engine** to prioritize urgent issues, transition complaint statuses (`Open` → `In Progress` → `Resolved`), and maintain an immutable audit trail.
- **Emergent Pattern Discovery**: One-click pattern detection scanning complaint descriptions to reveal cross-category systemic issues.
- **Evidence Panel & Traceability**: Modal displaying mathematical confidence scores and clickable references to exact source complaint IDs.
- **Notice Board**: Broadcast society announcements with priority pinning support.
- **Email Notifications**: Instant status update notifications dispatched to residents (via Resend or graceful console fallback).

---

## Emergent Pattern Discovery Architecture

The signature pattern discovery pipeline operates downstream of HDBSCAN clustering:

```text
Complaint Descriptions
          ↓
Sentence-Transformers (all-MiniLM-L6-v2 Embeddings)
          ↓
HDBSCAN Density Clustering (euclidean metric on L2-normalized vectors)
          ↓
Cross-Category Filter (>=3 complaints spanning >=2 distinct categories)
          ↓
Deterministic Pattern Strength Engine (4-part equal-weight score)
          ↓
LLM / Fallback Labeling Engine (Assigns name & description, tracks label_source)
          ↓
Evidence Traceability Panel (Source complaint IDs mapped to UI)
```

### Pattern Strength Methodology
Pattern Strength is computed using an equal-weighted 4-part deterministic formula normalized from 0 to 100%:

$$\text{Pattern Strength} = \frac{S_{\text{cohesion}} + S_{\text{size}} + S_{\text{category}} + S_{\text{temporal}}}{4}$$

1. **Cohesion Score ($S_{\text{cohesion}}$)**:
   $$S_{\text{cohesion}} = \frac{\text{avg\_cosine\_similarity} + 1}{2} \times 100$$
   Normalizes vector cosine similarity from $[-1, 1]$ into a $[0, 100]$ scale.
2. **Cluster Size Score ($S_{\text{size}}$)**:
   $$S_{\text{size}} = \min\left(100, \frac{\text{count} - 2}{10} \times 100\right)$$
   Scales linearly from minimum cluster size threshold up to 12+ complaints.
3. **Category Diversity Score ($S_{\text{category}}$)**:
   $$S_{\text{category}} = \min\left(100, \frac{\text{distinct\_categories} - 1}{4} \times 100\right)$$
   Rewards patterns that span across multiple isolated maintenance categories.
4. **Temporal Recency Score ($S_{\text{temporal}}$)**:
   $$S_{\text{temporal}} = \max\left(0, 1 - \frac{T_{\text{span}}}{7\text{ days}}\right) \times 100$$
   High scores indicate rapid clustering within recent days.

---

## Overdue Risk Score Engine

Complaints on the Admin Dashboard are sorted by an automated Overdue Risk Score formula:

$$\text{Risk Score} = \left(\frac{\text{Days Open}}{\text{Category SLA}}\right) \times \text{Priority Weight} \times \text{Floor Weight} \times \text{Weather Modifier}$$

- **Category SLA Baselines**: Cleaning (1 day), Electrical (2 days), Plumbing (3 days), General (4 days), Cosmetic (7 days).
- **Priority Weights**: High (1.5x), Medium (1.0x), Low (0.8x).
- **Weather Modifier**: 1.25x multiplier applied if rain/storm weather metadata is recorded.

---

## Technology Stack

- **Backend**: FastAPI (Python 3.11), Async SQLAlchemy, Pydantic v2, PyJWT, Passlib (`bcrypt==4.0.1`), `asyncpg` (PostgreSQL), `aiosqlite` (SQLite local).
- **Machine Learning & NLP**: `sentence-transformers` (`all-MiniLM-L6-v2`), `scikit-learn` / `hdbscan`.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Vanilla CSS Glassmorphism.
- **Testing & E2E**: Pytest, Pytest-Asyncio, Playwright (Chromium E2E DOM automation).

---

## Demo Persona Accounts

- **Admin Account**: `admin@nexus.society` / `admin123`
- **Resident Account**: `resident@nexus.society` / `resident123`

---

## Local Setup & Quick Start

### 1. Backend Setup & Data Seeding
```bash
# Navigate to backend and install requirements
cd backend
pip install -r requirements.txt
cd ..

# Seed test complaints and demo personas
python scripts/seed_demo_data.py

# Start local FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
# In a separate terminal
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Environment Variables (`.env.example`)

```env
PROJECT_NAME="NEXUS — Society Maintenance Tracker"
DATABASE_URL="sqlite+aiosqlite:///./backend/nexus.db"
# Production PostgreSQL URL automatically transformed to asyncpg:
# DATABASE_URL="postgresql+asyncpg://nexus_user:password@ep-xyz.render.com/nexus_db"

JWT_SECRET="nexus_super_secret_jwt_key_2026"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Optional Integration Keys (Graceful fallbacks if unconfigured)
RESEND_API_KEY=""
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
```

---

## Automated Testing & Verification

Run the backend unit and integration test suite:
```bash
python -m pytest backend/tests
```

Run visible Playwright Chromium E2E DOM automation:
```bash
python scripts/test_browser_playwright_e2e.py
```

---

## Scope Boundaries & Known Limitations

To maintain clear focus on core society intelligence:
- **NEXUS is not a building accounting/billing tool**: Maintenance dues and payment gateway integrations are deliberately out of scope.
- **LLM is strictly downstream**: Pattern discovery and scoring are 100% deterministic; the LLM is only invoked to generate human-readable labels for discovered clusters.
- **Photo Storage**: In cloud production, complaint image attachments are persisted directly in PostgreSQL as Base64 data URLs for ephemeral container resilience.

