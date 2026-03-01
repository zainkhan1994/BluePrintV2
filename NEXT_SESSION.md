# 🧠 Blueprint V2 — Next Session Checklist
> Last saved: March 1, 2026 | Branch: `main` | Commit: `f681e2f`

---

## ▶ HOW TO RESTART EVERYTHING

Open two terminals in `/Users/xainkhan/BluePrintV2` and run:

**Terminal 1 — Backend (FastAPI on port 8100):**
```bash
cd /Users/xainkhan/BluePrintV2
source .venv/bin/activate
cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

**Terminal 2 — Frontend (static server on port 8085):**
```bash
cd /Users/xainkhan/BluePrintV2
python3 -m http.server 8085
```

**Then open:** http://localhost:8085/classification-review-ui/

---

## ✅ WHAT'S DONE (working right now)

- [x] Notion-style white UI — 3-column layout (sidebar + list + detail panel)
- [x] Capture modal — add new items via "+ Quick Capture" button
- [x] Review queue — Approve / Modify / Reject items, 422 error fixed
- [x] Mind Map view — markmap tree layout (click "Mind Map" in left sidebar under "Second Brain")
  - [x] 4 toolbar buttons: ⊕ Expand All, ⊖ Collapse All, ⊡ Fit to Screen, ↺ Reset View
  - [x] Click any node to expand/collapse its children
  - [x] Logos displayed on nodes (from `/logos/` folder)
  - [x] Node colors from metadata

---

## 🔜 NEXT STEPS (priority order)

### 1. 🗺️ Mind Map — Polish & Populate (HIGH)
The mind map loads from `data/sample-mindmap.json` which only has ~10 demo nodes.
The real data lives across all the category folders (Chase/, Wells_Fargo/, etc.).

**Tasks:**
- [ ] Add all real app/account nodes to `data/sample-mindmap.json`
  - Each folder under `Accounts_Banking/`, `Finance_Payments/`, `Health_Fitness/`, etc. = one node
  - Each has a logo at e.g. `logos/chase.png` → set `metadata.logo: "logos/chase.png"`
- [ ] Tune the mind map appearance:
  - Increase `maxWidth` (currently 260) if labels get cut off
  - Adjust `initialExpandLevel` (currently 2 = show top 2 levels on load)
  - Try `colorFreezeLevel: 3` for more color variety

### 2. 📥 Real Ingestion Pipeline (HIGH)
Right now there's only 1 demo item in the database.

**Tasks:**
- [ ] Run the ingest script to load real data:
  ```bash
  cd /Users/xainkhan/BluePrintV2
  source .venv/bin/activate
  python scripts/ingest_local.py
  ```
- [ ] If that doesn't work, use the capture modal in the UI to add items manually
- [ ] Add test items across different categories (Finance, Health, Personal, etc.)
  to see the review queue fill up

### 3. 🎨 Mind Map Node Styling (MEDIUM)
Nodes currently show a colored dot + label. Logos are loading but small.

**Tasks:**
- [ ] In `classification-review-ui/app.js` → `toMarkmapNode()`, try increasing logo size:
  ```javascript
  width:28px; height:28px;  // currently 20x20
  ```
- [ ] Add a tooltip or click-to-open behavior — when you click a leaf node (an app),
  open the detail panel or a link to that app's login page

### 4. 📊 Dashboard Stats (MEDIUM)
The top stats bar (`Total Items`, `Approved`, `Needs Review`, `Rejected`) is wired up
but the counts depend on real data.

**Tasks:**
- [ ] Verify stats update correctly after approving/rejecting items
- [ ] Add a "Today's activity" indicator

### 5. 🔗 Deep Link from Mind Map → Review Panel (MEDIUM)
When a node in the mind map is clicked (a leaf app node), it should:
- Switch to the Review view
- Filter/select that item in the list

**Tasks:**
- [ ] In `toMarkmapNode()`, add `onClick` behavior for app-type nodes
- [ ] Pass the node's category to `fetchItems(status, category)` on click

### 6. 🔍 Search (LOW)
No search exists yet. Items can only be browsed by filter tabs.

**Tasks:**
- [ ] Add a search input above the list
- [ ] On input, call `/items?search=<query>` (check if backend supports it)
  or filter client-side on `item.title` + `item.content`

### 7. 📱 Mobile / Responsive (LOW)
The 3-column layout breaks on small screens.

---

## 🐛 KNOWN ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| Mind map empty on first load (spinner stays) | Needs testing | If it stalls, check browser console for CORS or 404 on `data/sample-mindmap.json` |
| Review queue shows 0 items | Expected | Only 1 demo item exists, and it's already "accepted". Add more items via capture modal |
| Backend must be started manually | By design | No auto-start set up yet |

---

## 📁 KEY FILES

| File | What it does |
|------|-------------|
| `classification-review-ui/index.html` | Main UI shell, toolbar, mind map container |
| `classification-review-ui/app.js` | All frontend logic — fetch, render, review actions, mind map init |
| `classification-review-ui/styles.css` | All styles — Notion white theme, mind map container |
| `data/sample-mindmap.json` | Mind map data — nodes + edges (needs real data populated) |
| `logos/` | App logos served at `http://localhost:8085/logos/` |
| `backend/app/main.py` | FastAPI routes |
| `backend/app/schemas.py` | Pydantic request/response models |
| `backend/app/services/classification.py` | Classification + review logic |

---

## 💡 QUICK WINS (can do in < 15 min each)

1. **Add 5 real items** via the capture modal, then approve/reject them — makes the app feel alive
2. **Expand `sample-mindmap.json`** — copy the node pattern and add Chase, Wells Fargo, etc.
3. **Change the app title** — search for `"Blueprint"` in `index.html` and make it your own

