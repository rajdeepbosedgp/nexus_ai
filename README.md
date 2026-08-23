# NEXUS — Society Maintenance Tracker & Emergent Intelligence

> **One-line pitch:** NEXUS is a society maintenance platform with one signature intelligence layer: it discovers emergent patterns that fall outside predefined complaint taxonomies, while making every discovery mathematically traceable to real complaint records.

---

## Technical Stack & Architecture

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy Async ORM, Pydantic v2, PyJWT, Passlib.
- **Target Database**: PostgreSQL (`postgresql+asyncpg://...`), with SQLite (`sqlite+aiosqlite:///./nexus.db`) provided for zero-configuration local development.
- **Intelligence Pipeline**:
  - `sentence-transformers` (`all-MiniLM-L6-v2`) for vector embeddings.
  - `hdbscan` / `scikit-learn` for mandatory density-based clustering.
  - Pure deterministic equal-weighted **Pattern Strength** scoring engine.
  - LLM cluster labeler (OpenAI/Claude API) with deterministic fallback generator and `label_source` tracking.
- **Frontend**: Vite + React + Tailwind CSS + Glassmorphic Design System.

---

## Quick Start Guide (One-Command Execution)

### 1. Backend Setup & Seeding

```bash
cd backend
python -m pip install -r requirements.txt
cd ..
python scripts/seed_demo_data.py
```

Start the FastAPI server:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Demo Persona Accounts

- **Admin Account**: `admin@nexus.society` / `admin123`
- **Resident Account**: `resident@nexus.society` / `resident123`

> [!NOTE]
> **Photo Storage**: Uploaded complaint images are stored in the backend `uploads/` directory for local/demo execution.
> **Security Note**: Demo-only credentials listed above are for evaluation purposes only — change or remove before production deployment.

---

## Environment Variables (`.env.example`)

```env
PROJECT_NAME="NEXUS — Society Maintenance Tracker"
# SQLite local development database: backend/nexus.db
DATABASE_URL="sqlite+aiosqlite:///./backend/nexus.db"
# Production PostgreSQL target example:
# DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/nexus"

JWT_SECRET="nexus_super_secret_jwt_key_2026"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Optional API Keys (System falls back gracefully if unconfigured):
RESEND_API_KEY=""
OPENAI_API_KEY=""
```

---

## System Design Write-Up

### 1. Complaint History Model (Immutable Log Design)
Every status update (`Open -> In Progress -> Resolved`) appends an immutable entry to the `complaint_history` table containing `{ id, complaint_id, actor_id, from_status, to_status, note, timestamp }`. History records are read-only and provide a clear audit trail for resolution SLAs.

### 2. Overdue Risk Score Formula
Instead of a naive flat counter, NEXUS computes a weighted overdue risk score:
$$\text{risk\_score} = \frac{\text{days\_open}}{\text{category\_avg\_resolution\_time}}$$
- **Electrical**: 2 days threshold
- **Plumbing**: 3 days threshold
- **Cosmetic**: 7 days threshold
- **Cleaning**: 1 day threshold
- **General**: 4 days threshold

Complaints are surfaced on the Admin Dashboard sorted descending by risk score.

### 3. Emergent Pattern Discovery Pipeline
NEXUS scans complaint descriptions across categories to discover emergent operational issues:
1. **Sentence Embeddings**: Text descriptions are converted into dense vector embeddings using `all-MiniLM-L6-v2`.
2. **HDBSCAN Clustering**: HDBSCAN is mandatory; it may be provided by `hdbscan` or `sklearn.cluster.HDBSCAN`. It identifies natural complaint clusters without predefining cluster counts.
3. **Cluster Size & Cross-Category Filter**: Candidates are filtered to keep only clusters containing $\ge 3$ complaints and spanning $\ge 2$ distinct predefined categories.
4. **Deterministic Pattern Strength Formula**:
   $$\text{Pattern Strength} = \frac{S_{\text{cohesion}} + S_{\text{size}} + S_{\text{category}} + S_{\text{temporal}}}{4}$$
   - $S_{\text{cohesion}} = \frac{\text{avg cosine similarity} + 1}{2} \times 100$
   - $S_{\text{size}} = \min\left(100, \frac{\text{count} - 2}{10} \times 100\right)$
   - $S_{\text{category}} = \min\left(100, \frac{\text{distinct\_categories} - 1}{4} \times 100\right)$
   - $S_{\text{temporal}} = \max\left(0, 1 - \frac{T_{\text{span}}}{7\text{ days}}\right) \times 100$
5. **LLM Cluster Labeling**: Downstream of discovery, an LLM (or fallback generator) assigns a human-readable name and description, setting `label_source` to `"llm"` or `"fallback"`.
6. **Traceability Evidence Panel**: Every pattern retains the exact source complaint IDs, allowing the evidence panel to trace each discovery back to its originating complaint records (`INC-xxx`).
