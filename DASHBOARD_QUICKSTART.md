# Blueprint Dashboard - Quick Start Guide

## Status ✅

The modern dashboard is **fully operational** and ready to use!

**Services Running:**
- ✅ Backend: `http://127.0.0.1:8100`
- ✅ Dashboard: `http://127.0.0.1:8085`

## What You Can Do Now

### 1. **Capture Content**
Paste or drag-and-drop any text, email, or notes into the capture area (left sidebar)
- Automatically classifies into: action, thought, idea, emotion
- Or manually force a category
- Hits Enter to submit

### 2. **Review & Approve**
Items appear in the left sidebar as they're classified
- View full content in the right pane
- See AI confidence score with visual indicator
- Approve, Modify, or Reject each classification

### 3. **Override Classifications**
Click "Modify" to:
- Change the predicted category
- Add notes explaining the override
- System logs all changes with timestamps

### 4. **View Audit Trail**
See complete history of:
- Original AI classification + confidence
- User overrides with timestamps
- Notes explaining changes

## Example Workflow

```
1. Copy text from email: "Call mom on Monday about the dentist appointment"
2. Paste into capture area
3. Click Submit
4. System classifies as: "action"
5. You review and approve → Done!
6. Next item appears automatically
```

## File Locations

```
Dashboard Files:
├── index.html      (Professional HTML template)
├── app.js          (Complete JavaScript logic)
├── styles.css      (Dark theme with cyan accents)
└── README.md       (Original docs)

Backend Files:
└── backend/app/main.py  (FastAPI with CORS configured)
```

## Keyboard Shortcuts

- **Ctrl+Enter** in capture area: Submit item
- **Click item**: View details
- **Click close button**: Hide detail pane

## API Endpoints

All requests go directly to backend on port 8100:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /items | Capture new item |
| GET | /classification/needs-review | Fetch pending items |
| GET | /items/{id} | Get item details |
| GET | /items/{id}/classification | Get classification |
| POST | /items/{id}/classification/override | Approve/Modify/Reject |

## Frontend Features

### Dark Theme
- Background: #1e1e2e (professional dark)
- Accent: #00d4ff (vibrant cyan)
- Text: #e0e0e0 (light gray, easy on eyes)

### Layout
- **Left Sidebar**: Capture input + Items list
- **Right Pane**: Item details + Classification + Actions
- **Header**: Statistics (total, pending, approved)
- **Responsive**: Works on desktop and mobile

### Color Coding
- 🔵 Cyan (#00d4ff): Primary actions & selected items
- 🟢 Green (#00d46e): Approve button
- 🟡 Yellow (#ffd700): Modify button
- 🔴 Red (#ff6b6b): Reject button

## Environment Details

**Python Environment:**
```bash
Location: /Users/xainkhan/BluePrintV2/.venv
Python: 3.12.12
Active packages: FastAPI, SQLAlchemy, Chroma, etc.
```

**Database:**
```bash
Location: /Users/xainkhan/BluePrintV2/blueprint_memory.db
Type: SQLite
Size: ~700 KB (includes embeddings & classifications)
```

**Vector Store:**
```bash
Type: Chroma (persistent)
Collection: blueprint_items
Embeddings: 384-dimensional local-hash
Items: Currently 1 (demo item)
```

## Starting Fresh

If services stopped, restart them:

```bash
# Terminal 1: Start Backend
cd /Users/xainkhan/BluePrintV2
source .venv/bin/activate
python backend/app/main.py

# Terminal 2: Start UI Server
cd /Users/xainkhan/BluePrintV2/classification-review-ui
python -m http.server 8085

# Then open:
# http://localhost:8085
```

## Troubleshooting

### Dashboard won't load?
```bash
# Check UI server
curl http://localhost:8085

# Check backend
curl http://localhost:8100/ready
```

### Items not showing after submit?
- Wait 5 seconds (classification is async)
- Check browser console (F12) for errors
- Verify backend logs

### Submit button not responding?
- Ensure you entered content (title is optional)
- Check network tab in DevTools for failed requests
- Verify CORS headers are present

### Old data showing?
- Refresh page (Cmd+R or Ctrl+R)
- Clear browser cache if needed
- Check database isn't corrupted

## Code Organization

### app.js Structure
```javascript
// API Functions
apiFetch()
fetchNeedsReview()
ingestItem()
getItemDetail()
getItemClassification()
overrideClassification()

// Capture Handlers
setupCapture()
handleSubmit()

// List Management
loadList()
renderList()
selectItem()

// Action Handlers
handleApprove()
handleModify()
handleModifyConfirm()
handleReject()

// UI Helpers
updateDetailUI()
showPlaceholder()
showActionMessage()

// Audit Trail
addAuditEntry()
updateAuditTrail()
```

### styles.css Structure
```css
:root                          /* Colors & spacing */
body                           /* Base styling */
.header                        /* Top bar with stats */
.sidebar                       /* Left capture + list panel */
.input-section                 /* Capture input area */
.items-list                    /* Pending items */
.detail-pane                   /* Right item details */
.classification-card           /* AI classification display */
.override-section              /* Modify controls */
.action-buttons                /* Approve/Modify/Reject */
.audit-section                 /* Override history */
::-webkit-scrollbar            /* Styled scrollbars */
@media (max-width: 768px)      /* Mobile responsive */
```

## Next Steps

### Ready to Try?
1. Open http://localhost:8085 in your browser
2. Paste some text in the capture area
3. Click Submit
4. Watch it classify!
5. Approve, modify, or reject

### Want to Customize?
- Edit `styles.css` for colors/layout
- Edit `app.js` for behavior
- Edit `index.html` for structure
- No build tool needed!

### Want to Add Features?
- Search/filter by category
- Bulk approve operations
- Custom category definitions
- Classification thresholds
- Export functionality

## Support

**Backend Issues?**
- Check `/Users/xainkhan/BluePrintV2/backend/app/main.py`
- Review database: `blueprint_memory.db`
- Check logs in terminal running backend

**Frontend Issues?**
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests
- Clear cache and reload

**API Issues?**
- Test endpoints directly with curl
- Check CORS headers are present
- Verify backend is running

---

**Last Updated**: February 22, 2026  
**Version**: 1.0 - Modern Dashboard Release  
**Status**: ✅ Production Ready
