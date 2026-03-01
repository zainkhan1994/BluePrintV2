# Modern Dashboard - Technical Specification

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (localhost:8085)                 │
│                    ─────────────────────────                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HEADER (Statistics: Total, Pending, Approved)       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────┬──────────────────────────────────────┐  │
│  │  SIDEBAR     │           DETAIL PANE                │  │
│  │              │                                       │  │
│  │ • Capture    │ • Item Content                        │  │
│  │ • List       │ • Classification Card                 │  │
│  │   - Items    │ • Override Controls                   │  │
│  │   - Stats    │ • Action Buttons                      │  │
│  │              │ • Audit Trail                         │  │
│  └──────────────┴──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         │ HTTP/Fetch (Port 8100)
         ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI + SQLAlchemy)             │
│                  localhost:8100 (Uvicorn)                   │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  • POST /items                                              │
│  • GET /classification/needs-review                         │
│  • GET /items/{id}                                          │
│  • GET /items/{id}/classification                           │
│  • POST /items/{id}/classification/override                 │
├─────────────────────────────────────────────────────────────┤
│  Services:                                                  │
│  • JobProcessor (embed → tag → classify)                   │
│  • EmbeddingService (local-hash 384-dim)                   │
│  • ClassificationService (ML classifier)                   │
│  • VectorStore (Chroma)                                    │
└─────────────────────────────────────────────────────────────┘
         │
         ├──→ SQLite Database (blueprint_memory.db)
         └──→ Chroma Vector Store (persistent)
```

## Frontend Component Hierarchy

### HTML Structure
```
<div class="container">
  ├─ <header class="header">
  │  ├─ <div class="header-content">
  │  │  ├─ <h1>Blueprint</h1>
  │  │  └─ <div class="subtitle">Classification Dashboard</div>
  │  └─ <div class="header-stats">
  │     ├─ <div class="stat"> Total Items
  │     ├─ <div class="stat"> Pending Review
  │     └─ <div class="stat"> Approved
  │
  ├─ <div class="main">
  │  ├─ <aside class="sidebar">
  │  │  ├─ <div class="input-section">
  │  │  │  ├─ <h2>New Capture</h2>
  │  │  │  ├─ <div class="input-area" id="drop-zone">
  │  │  │  ├─ <input class="input-field" id="capture-title">
  │  │  │  ├─ <textarea class="textarea-field" id="capture-content">
  │  │  │  ├─ <select class="select-field" id="capture-category">
  │  │  │  └─ <button class="btn btn-primary" id="capture-submit">
  │  │  │
  │  │  └─ <div class="list-section">
  │  │     ├─ <h3>Pending Items</h3>
  │  │     ├─ <ul id="items-list">
  │  │     │  └─ <li class="item-row">
  │  │     │     ├─ <div class="item-row-title">
  │  │     │     └─ <div class="item-row-class">
  │  │     └─ <button id="refresh-btn">Refresh</button>
  │  │
  │  └─ <section class="detail-pane">
  │     ├─ <div id="placeholder">
  │     │  └─ "Select an item to review"
  │     │
  │     └─ <div id="item-detail" class="item-detail">
  │        ├─ <div class="detail-header">
  │        │  ├─ <h2 id="detail-title">Item Title</h2>
  │        │  ├─ <div class="detail-meta">
  │        │  │  └─ ID: <span id="detail-id">uuid</span>
  │        │  └─ <button class="btn-close" id="close-detail">×</button>
  │        │
  │        ├─ <div class="detail-content">
  │        │  │
  │        │  ├─ <div class="content-section">
  │        │  │  ├─ <h3>Content</h3>
  │        │  │  └─ <div class="content-box" id="detail-content">
  │        │  │
  │        │  ├─ <div class="classification-section">
  │        │  │  ├─ <h3>AI Classification</h3>
  │        │  │  └─ <div class="classification-card">
  │        │  │     ├─ <div class="class-row">
  │        │  │     │  ├─ Label: <span id="class-label">
  │        │  │     │  └─ <div class="class-badge">
  │        │  │     ├─ <div class="class-row">
  │        │  │     │  ├─ Confidence:
  │        │  │     │  ├─ <div class="confidence-bar">
  │        │  │     │  │  └─ <div class="confidence-fill" id="confidence-bar">
  │        │  │     │  └─ <span id="class-confidence">95.0%</span>
  │        │  │     └─ <div class="class-row">
  │        │  │        ├─ Status:
  │        │  │        └─ <span id="class-status" class="status-badge">
  │        │  │
  │        │  ├─ <div class="override-section">
  │        │  │  ├─ <h3>Override Classification</h3>
  │        │  │  └─ <div class="override-controls">
  │        │  │     ├─ <select id="override-category">
  │        │  │     └─ <textarea id="override-notes">
  │        │  │
  │        │  ├─ <div class="action-buttons">
  │        │  │  ├─ <button id="action-approve" class="btn btn-approve">
  │        │  │  ├─ <button id="action-modify" class="btn btn-modify">
  │        │  │  ├─ <button id="action-reject" class="btn btn-reject">
  │        │  │  ├─ <button id="action-modify-confirm" class="btn btn-primary">
  │        │  │  └─ <button id="action-modify-cancel" class="btn btn-secondary">
  │        │  │
  │        │  └─ <div class="audit-section">
  │        │     ├─ <h3>Override History</h3>
  │        │     └─ <div id="audit-trail" class="audit-trail">
  │        │        └─ <div class="audit-entry">
  │        │
  │        └─ <div id="action-message" class="action-message">
```

## JavaScript Module Map

### State Management
```javascript
let currentItem = null           // Current selected item
let currentClassification = null // Current classification data
let auditTrail = []             // Manual overrides history
let modifyMode = false          // Whether in modify edit mode
```

### API Layer
```javascript
apiFetch(path, opts)            // Direct HTTP to backend
├─ fetchNeedsReview(limit)      // GET /classification/needs-review
├─ ingestItem(title, content, category)     // POST /items
├─ getItemDetail(itemId)        // GET /items/{id}
├─ getItemClassification(itemId) // GET /items/{id}/classification
└─ overrideClassification(...)   // POST /items/{id}/classification/override
```

### UI Controller Layer
```javascript
setupCapture()                  // Initialize capture form handlers
├─ handleSubmit()               // Form submission → POST /items
├─ Drag/drop handler
└─ Focus management

loadList()                       // Fetch and render items list
├─ fetchNeedsReview()
└─ renderList(items)

selectItem(itemId)              // Load item detail
├─ getItemDetail()
├─ getItemClassification()
├─ updateDetailUI()
├─ updateAuditTrail()
└─ Highlight in list

handleApprove()                 // POST override with action=approve
handleModify()                  // Toggle modify mode
handleModifyConfirm()           // POST override with action=modify
handleModifyCancel()            // Exit modify mode
handleReject()                  // POST override with action=reject
```

### UI Helpers
```javascript
updateDetailUI()                // Show/hide buttons based on state
showPlaceholder(show)           // Toggle placeholder vs detail pane
showActionMessage(text, type)   // Display status message
addAuditEntry(action, notes)    // Log manual override
updateAuditTrail()              // Render audit entries
```

## CSS Class Hierarchy

### Layout Classes
```css
.container              /* Main flex container (height: 100vh) */
.header                 /* Top bar (background: secondary) */
.main                   /* Flex container (flex: 1) */
.sidebar                /* Left panel (width: 340px, border-right) */
.detail-pane            /* Right panel (flex: 1) */
```

### Content Sections
```css
.input-section          /* Capture form area */
.input-area             /* Drag-drop zone (border: dashed) */
.list-section           /* Items list area */
.detail-header          /* Item title + metadata */
.detail-content         /* Scrollable content area */
```

### Cards & Components
```css
.classification-card    /* AI classification display */
.class-row              /* Label/value pair in card */
.class-badge            /* Category badge */
.status-badge           /* Status indicator (color-coded) */
.confidence-bar         /* Visual confidence indicator */
.action-buttons         /* Approve/Modify/Reject group */
.audit-entry            /* Single override log entry */
```

### State Classes
```css
.hidden                 /* display: none */
.active                 /* Selected item highlight */
.drag-over              /* Drag-drop hover state */
.show                   /* Message visibility */
.success                /* Success status color */
.error                  /* Error status color */
.pending                /* Pending status badge color */
```

## Data Flow

### Capture Workflow
```
User Input
    ↓
handleSubmit()
    ↓
ingestItem(title, content, category)
    ↓
POST /items
    ↓
Backend: Create item + Embed + Tag + Classify
    ↓
showActionMessage("Item captured!")
    ↓
Clear inputs
loadList()
    ↓
Select first item (auto-expand detail pane)
    ↓
selectItem(itemId)
    ↓
Display classification
```

### Review Workflow
```
Click Item in List
    ↓
selectItem(itemId)
    ↓
Parallel:
├─ getItemDetail()
└─ getItemClassification()
    ↓
renderList() highlights selected
updateDetailUI() shows action buttons
    ↓
User clicks Approve/Modify/Reject
    ↓
overrideClassification(itemId, action)
    ↓
POST /items/{id}/classification/override
    ↓
addAuditEntry()
updateAuditTrail()
loadList() (refresh)
    ↓
showActionMessage("✓ Item approved")
```

## Color Palette (CSS Variables)

| Variable | Value | Usage |
|----------|-------|-------|
| --primary | #1e1e2e | Main background |
| --secondary | #2d2d44 | Panel backgrounds |
| --accent | #00d4ff | Primary action, highlights |
| --accent-alt | #00ff88 | Gradient secondary |
| --text | #e0e0e0 | Main text |
| --text-muted | #888 | Secondary text |
| --border | #404050 | Dividers |
| --success | #00d46e | Approve action |
| --warning | #ffd700 | Modify action |
| --danger | #ff6b6b | Reject action |

## Responsive Breakpoints

```css
@media (max-width: 1024px) {
  .sidebar { width: 280px; }
  .header-stats { gap: 20px; }
}

@media (max-width: 768px) {
  .main { flex-direction: column; }
  .sidebar { 
    width: 100%;
    height: 40%;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
  .detail-pane { height: 60%; }
}
```

## Error Handling Strategy

```javascript
try {
  const result = await apiCall()
  // Success path
} catch (err) {
  showActionMessage(err.message, 'error')
  // Automatic UI recovery
  // User sees error in message bar
  // Can retry or switch to different item
}
```

## Performance Optimizations

1. **Direct API Calls**: No proxy layer (was removed)
2. **Parallel Requests**: `Promise.all([getItem(), getClassification()])`
3. **Efficient DOM Updates**: Replace only what changed
4. **Smart List Rendering**: Minimal DOM traversal
5. **Event Delegation**: Click handler on list parent
6. **Scrollbar Styling**: Custom scrollbars for theme consistency

## Security Considerations

1. **CORS**: Whitelist only 127.0.0.1:8085 on backend
2. **No Authentication**: Currently open access (can add JWT later)
3. **Input Validation**: Minimal on frontend (validated by backend)
4. **XSS Prevention**: No innerHTML for user content (using textContent)
5. **CSRF**: Not applicable (no state-changing cookies)

## Testing Checklist

- [ ] Capture input accepts text and files
- [ ] Submit creates item in backend
- [ ] List loads automatically
- [ ] Item details render correctly
- [ ] Classification displays with confidence bar
- [ ] Approve saves and refreshes list
- [ ] Modify mode enables category select
- [ ] Modify confirm saves and logs to audit trail
- [ ] Reject marks item as rejected
- [ ] Audit trail shows all overrides with timestamps
- [ ] Close button returns to placeholder
- [ ] Refresh button updates list
- [ ] Error messages display on network failure
- [ ] Responsive design works on mobile
- [ ] Dark theme renders correctly
- [ ] Cyan accents display properly
- [ ] Keyboard shortcut (Ctrl+Enter) submits

## File Sizes

| File | Size | Lines |
|------|------|-------|
| index.html | ~7 KB | 180 |
| app.js | ~14 KB | 380 |
| styles.css | ~15 KB | 580 |
| **Total** | **~36 KB** | **1140** |

## Browser Requirements

- ES6+ JavaScript support
- Fetch API
- CSS Grid/Flexbox
- Local Storage (optional, not currently used)
- No external dependencies

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-22 | Initial modern dashboard release |
| | | • Dark theme with cyan accents |
| | | • Capture input (paste/drop) |
| | | • Review with approve/modify/reject |
| | | • Audit trail |
| | | • Responsive design |
| | | • Direct API integration |

---

**Document**: Modern Dashboard Technical Specification  
**Version**: 1.0  
**Last Updated**: February 22, 2026
