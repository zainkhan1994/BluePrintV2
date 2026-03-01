# 🧠 Blueprint V2 — Where You Are & What's Next
> Updated: March 1, 2026 | Branch: `main`

---

## ✅ FRONTEND — COMPLETE
The UI is done. Here's what's built and working:
- Notion-style white 3-column dashboard (sidebar + list + detail panel)
- Capture modal — add items manually
- Review queue — Approve / Modify / Reject (422 bug fixed)
- Mind Map view — markmap tree, logos on nodes, 4 control buttons
- Stats bar, filter tabs, audit trail

**You don't need to touch the frontend anymore.**

---

## 🔴 THE REAL GAP: Your Data Is Empty

Right now the database (`backend/blueprint_memory.db`) has **1 demo item**.
The Blueprint folders (`Accounts_Banking/`, `Health_Fitness/`, etc.) contain **only logo images** — no real content.

**The app is a working shell with no data inside it.**
This is the only thing left to build.

---

## ▶ HOW TO RESTART (run every session)

**Terminal 1 — Backend:**
```bash
cd /Users/xainkhan/BluePrintV2/backend
source ../.venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

**Terminal 2 — Frontend:**
```bash
cd /Users/xainkhan/BluePrintV2
python3 -m http.server 8085
```

**Open:** http://localhost:8085/classification-review-ui/

---

## 🗺️ THE 3 REMAINING PHASES

---

### PHASE 1 — Feed Your Real Data In (Do This First)

**Goal:** Get your actual accounts, bills, and documents into the system.

Right now your category folders only have logos. Add `.md` files with real info:

```
Accounts_Banking/Chase/
  ├── logo.png          ← already there
  └── account.md        ← ADD THIS
```

Example content for `Accounts_Banking/Chase/account.md`:
```markdown
# Chase Checking
- Account ending: 4821
- Login: chase.com
- Auto-pays: Rent, Netflix
- Monthly fee: none
```

Do this for the folders you care about most:
- `Accounts_Banking/` — bank + credit card details
- `Bills_Payments/` — recurring bills, due dates, amounts
- `Health_Fitness/` — doctors, insurance, prescriptions
- `Daily_Life_Digital_Presence/` — social accounts, subscriptions
- `Finance_Payments/` — Venmo, PayPal, CashApp info

**Then bulk-ingest everything:**
```bash
cd /Users/xainkhan/BluePrintV2
source .venv/bin/activate
python scripts/ingest_local.py --path . --source blueprint_personal
```

Then open the UI → Review Queue → Approve your items.

---

### PHASE 2 — Wire Up Real AI

**Goal:** Make Insights, Search, and Digest actually intelligent.

Right now the backend uses **keyword matching only** (no LLM). These API routes exist but don't use AI:
- `POST /insights/generate` — item summaries
- `POST /assistant/digest` — daily briefing
- `POST /search/semantic` — find related items

**To fix this, you need one API key.** Recommended options:

| Provider | Cost | Notes |
|----------|------|-------|
| OpenAI | ~$0.01/request | Easiest, best quality |
| Google Gemini | Free tier | You already have experience with it |
| Anthropic Claude | ~$0.01/request | Great for summaries |

**Setup (5 min):**
```bash
# Add to backend/.env
OPENAI_API_KEY=sk-your-key-here
embedding_provider=api
embedding_api_url=https://api.openai.com/v1/embeddings
embedding_api_key=sk-your-key-here
embedding_api_model=text-embedding-3-small
```

Then ask Copilot: *"Update backend/app/services/insights.py to call the OpenAI Chat API to generate real item summaries using the item content stored in the database."*

---

### PHASE 3 — Connect the Mind Map to Real Data

**Goal:** Mind map shows your actual Blueprint structure, not the sample demo.

Right now `data/sample-mindmap.json` has placeholder nodes. It should mirror your real folder structure with every account/app as a leaf node.

**Auto-generate it from your folders:**

Ask Copilot: *"Write a Python script at scripts/generate_mindmap.py that walks the BluePrintV2 folder structure (skipping .git, .venv, backend, scripts, classification-review-ui), finds folders with logo.png files, and generates data/sample-mindmap.json in the existing nodes+edges format. Use the folder name as the label and the relative logo.png path as metadata.logo."*

Run it after you've added content in Phase 1:
```bash
python scripts/generate_mindmap.py
```

---

## 📋 QUICKSTART CHECKLIST (do in order)

```
[ ] 1. Add account.md files to 3-5 of your most important folders
[ ] 2. Start both servers (commands above)
[ ] 3. Run: python scripts/ingest_local.py --path . --source blueprint_personal
[ ] 4. Open UI → Review Queue → Approve the new items
[ ] 5. Watch the stats bar show real numbers
[ ] 6. Get an OpenAI or Gemini API key
[ ] 7. Add key to backend/.env → restart backend
[ ] 8. Ask Copilot to update insights.py to use real AI
[ ] 9. Ask Copilot to create scripts/generate_mindmap.py
[ ] 10. Run generate_mindmap.py → reload UI → see your real mind map
```

---

## ⚡ CURRENT STATE AT A GLANCE

| Layer | Status | Notes |
|-------|--------|-------|
| Frontend UI | ✅ Done | No changes needed |
| Backend API | ✅ Running | All routes exist |
| Database schema | ✅ Done | SQLite at backend/blueprint_memory.db |
| Real personal data | ❌ Empty | Only 1 demo item — Phase 1 fixes this |
| AI / LLM | ❌ Keyword-only | Needs API key + code update — Phase 2 |
| Mind map data | ❌ Placeholder | Needs generate_mindmap.py — Phase 3 |
| Semantic search | ❌ Local hash only | Fixed automatically when you add API key |

---

## 🔑 KEY FILES

| File | What it does |
|------|-------------|
| `classification-review-ui/app.js` | Frontend logic — complete, don't change |
| `backend/app/services/model_assist.py` | AI scoring — needs real LLM wired in |
| `backend/app/services/insights.py` | Insight generation — needs real LLM |
| `backend/app/config.py` | Settings — reads from backend/.env |
| `backend/blueprint_memory.db` | SQLite DB — your data lives here |
| `data/sample-mindmap.json` | Mind map source — rebuild with generate_mindmap.py |
| `scripts/ingest_local.py` | Bulk import — point at any folder |
