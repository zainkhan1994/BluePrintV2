// ─────────────────────────────────────────────
//  Blueprint — Second Brain  app.js
// ─────────────────────────────────────────────
const API_BASE = 'http://127.0.0.1:8100'

// ── tiny helpers ──────────────────────────────
const $ = s => document.querySelector(s)
const $$ = s => Array.from(document.querySelectorAll(s))

// ── state ─────────────────────────────────────
let currentItem  = null
let currentView  = 'inbox'    // nav section
let currentFilter = 'needs_review'  // tab filter

// ── element refs (new HTML) ───────────────────
const navItems       = $$('.nav-item')
const centerTitle    = $('#center-title')
const centerSub      = $('#center-sub')
const filterTabs     = $$('.tab')
const filterTabsBar  = $('#filter-tabs')
const itemsList      = $('#items-list')
const mindmapView    = $('#mindmap-view')
const refreshBtn     = $('#refresh-btn')
const newCaptureBtn  = $('#new-capture-btn')

// capture modal
const captureOverlay  = $('#capture-overlay')
const captureClose    = $('#capture-close')
const captureTitle    = $('#capture-title')
const captureContent  = $('#capture-content')
const captureCat      = $('#capture-category')
const captureSubmit   = $('#capture-submit')
const captureMsg      = $('#capture-msg')

// detail panel
const detailPlaceholder = $('#detail-placeholder')
const detailBody        = $('#detail-body')
const closeDetailBtn    = $('#close-detail')

const detailCatTag  = $('#detail-category-tag')
const detailTitle   = $('#detail-title')
const detailMeta    = $('#detail-meta')
const detailContent = $('#detail-content')

const detailClassLabel = $('#detail-class-label')
const detailConfBar    = $('#detail-conf-bar')
const detailConfPct    = $('#detail-conf-pct')
const detailStatus     = $('#detail-status')

const overrideCategory = $('#override-category')
const overrideNotes    = $('#override-notes')

const approveBtn  = $('#approve-btn')
const modifyBtn   = $('#modify-btn')
const rejectBtn   = $('#reject-btn')
const actionMsg   = $('#action-msg')

const auditSection = $('#audit-section')
const auditTrail   = $('#audit-trail')

// stats
const statTotal    = $('#stat-total')
const statPending  = $('#stat-pending')
const statApproved = $('#stat-approved')
const navBadge     = $('#nav-badge')

// ── API helpers ───────────────────────────────
async function apiFetch(path, opts = {}) {
  const res = await fetch(API_BASE + path, opts)
  if (!res.ok) throw new Error(`${res.status} – ${res.statusText}`)
  return res.json()
}

async function fetchItems(status = 'needs_review', category = null) {
  // needs-review uses special endpoint; others use /items with query params
  if (status === 'needs_review') {
    const data = await apiFetch('/classification/needs-review?limit=50')
    return Array.isArray(data) ? data : data.items || []
  }
  const p = new URLSearchParams()
  if (status !== 'all') p.set('status', status)
  if (category)         p.set('category', category)
  p.set('limit', '100')
  const data = await apiFetch('/items?' + p.toString())
  return Array.isArray(data) ? data : data.items || []
}

// ── VIEW CONFIG ───────────────────────────────
const views = {
  inbox:    { title: 'Inbox',       sub: 'Items waiting for your review',   defaultFilter: 'needs_review', category: null },
  review:   { title: 'Review Queue',sub: 'Manually triage each capture',    defaultFilter: 'needs_review', category: null },
  actions:  { title: 'Actions',     sub: 'Captured action items',           defaultFilter: 'all',          category: 'action'  },
  thoughts: { title: 'Thoughts',    sub: 'Your captured thoughts',          defaultFilter: 'all',          category: 'thought' },
  ideas:    { title: 'Ideas',       sub: 'Ideas worth keeping',             defaultFilter: 'all',          category: 'idea'    },
  emotions: { title: 'Emotions',    sub: 'Emotional notes & reflections',   defaultFilter: 'all',          category: 'emotion' },
  all:      { title: 'All Items',   sub: 'Everything in your brain',        defaultFilter: 'all',          category: null      },
  mindmap:  { title: 'Mind Map',    sub: 'Blueprint knowledge graph',       defaultFilter: null,           category: null      },
}

// ── NAVIGATE ──────────────────────────────────
function setView(view) {
  if (view === 'capture') { openCaptureModal(); return }

  currentView = view
  const cfg = views[view] || views.inbox
  centerTitle.textContent = cfg.title
  centerSub.textContent   = cfg.sub

  // Highlight nav
  navItems.forEach(n => n.classList.toggle('active', n.dataset.view === view))

  const isMindMap = view === 'mindmap'

  // Toggle mind map vs list views
  mindmapView.classList.toggle('hidden', !isMindMap)
  itemsList.classList.toggle('hidden', isMindMap)
  filterTabsBar.classList.toggle('hidden', isMindMap)
  refreshBtn.style.display = isMindMap ? 'none' : ''
  newCaptureBtn.style.display = isMindMap ? 'none' : ''

  // Toggle full-width layout
  document.querySelector('.app').classList.toggle('mindmap-active', isMindMap)

  if (isMindMap) {
    initMindMap()
    return
  }

  currentFilter = cfg.defaultFilter
  filterTabs.forEach(t => {
    t.classList.toggle('active', t.dataset.filter === currentFilter)
  })
  loadList()
}

// ── MIND MAP ──────────────────────────────────
let mmInstance   = null   // markmap instance
let mmRootData   = null   // original root for reset
let mmLoaded     = false

async function initMindMap() {
  if (mmLoaded) return

  const container = $('#mindmap-container')
  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;
                height:100%;color:#999;font-size:13px;gap:8px;">
      <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"
           style="width:16px;height:16px;animation:spin 1s linear infinite">
        <path d="M4 10a6 6 0 1011.3-2.8M4 10V5M4 10H9"/>
      </svg>
      Building knowledge graph…
    </div>`

  try {
    const res = await fetch('../data/sample-mindmap.json')
    if (!res.ok) throw new Error(`Could not load mind map data (${res.status})`)
    const data = await res.json()

    // ── Convert nodes+edges JSON → markmap root tree ──
    const nodeById = {}
    data.nodes.forEach(n => { nodeById[n.id] = { ...n, children: [] } })
    data.edges.forEach(e => {
      if (nodeById[e.source] && nodeById[e.target])
        nodeById[e.source].children.push(nodeById[e.target])
    })
    const roots = data.nodes.filter(n => !data.edges.some(e => e.target === n.id))
    const treeRoot = roots.length === 1 ? nodeById[roots[0].id]
      : { id: '__root__', label: 'Blueprint', type: 'root',
          metadata: { color: '#4a9eff' }, children: roots.map(r => nodeById[r.id]) }

    // ── Build markmap INode tree ──
    const SERVER_BASE = 'http://localhost:8085/'

    function toMarkmapNode(node, depth = 0) {
      const color  = node.metadata?.color || '#4a9eff'
      const logo   = node.metadata?.logo
      const logoUrl = logo ? SERVER_BASE + logo : null

      // Node content: logo image or colored circle + label
      let content
      if (logoUrl) {
        content = `<img src="${logoUrl}"
          style="width:20px;height:20px;border-radius:50%;
                 object-fit:cover;vertical-align:middle;margin-right:5px;
                 border:2px solid ${color}20;"
          onerror="this.style.display='none'"
        /><span style="color:${color};font-weight:${depth <= 1 ? '700' : depth === 2 ? '600' : '500'}">${node.label}</span>`
      } else {
        content = `<span style="display:inline-block;width:10px;height:10px;
          border-radius:50%;background:${color};margin-right:6px;
          vertical-align:middle;flex-shrink:0"></span>
          <span style="color:${color};font-weight:${depth <= 1 ? '700' : depth === 2 ? '600' : '500'}">${node.label}</span>`
      }

      return {
        content,
        children: node.children.map(c => toMarkmapNode(c, depth + 1)),
        payload: {
          fold: depth >= 2 ? 1 : 0   // collapse at depth 2+, keep top 2 levels open
        }
      }
    }

    mmRootData = toMarkmapNode(treeRoot, 0)

    // ── Render ──
    container.innerHTML = ''
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    svg.style.cssText = 'width:100%;height:100%;'
    container.appendChild(svg)

    const { Markmap, loadCSS, loadJS } = window.markmap
    mmInstance = Markmap.create(svg, {
      colorFreezeLevel: 2,
      duration:         400,
      maxWidth:         260,
      zoom:             true,
      pan:              true,
      initialExpandLevel: 2,
      fitRatio:         0.92,
    }, mmRootData)

    mmLoaded = true

    // ── Wire the 4 toolbar buttons ──
    $('#mm-expand').onclick = () => {
      const expand = (node) => {
        node.payload = node.payload || {}
        node.payload.fold = 0
        node.children?.forEach(expand)
      }
      expand(mmRootData)
      mmInstance.setData(mmRootData)
      setTimeout(() => mmInstance.fit(), 350)
    }

    $('#mm-collapse').onclick = () => {
      const collapse = (node, depth) => {
        node.payload = node.payload || {}
        node.payload.fold = depth >= 1 ? 1 : 0
        node.children?.forEach(c => collapse(c, depth + 1))
      }
      collapse(mmRootData, 0)
      mmInstance.setData(mmRootData)
      setTimeout(() => mmInstance.fit(), 350)
    }

    $('#mm-fit').onclick = () => mmInstance.fit()

    $('#mm-reset').onclick = () => {
      // Rebuild from original with depth-2 fold
      const reset = (node, depth) => {
        node.payload = node.payload || {}
        node.payload.fold = depth >= 2 ? 1 : 0
        node.children?.forEach(c => reset(c, depth + 1))
      }
      reset(mmRootData, 0)
      mmInstance.setData(mmRootData)
      setTimeout(() => mmInstance.fit(), 350)
    }

  } catch (err) {
    container.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:center;
                  height:100%;color:#c03030;font-size:13px;">
        ⚠ ${err.message}
      </div>`
  }
}

// ── LOAD + RENDER LIST ────────────────────────
async function loadList() {
  itemsList.innerHTML = '<li class="empty-row">Loading…</li>'

  const cfg = views[currentView] || views.inbox
  // For category views, ignore the tab filter and fetch by category
  const status   = cfg.category ? 'all' : currentFilter
  const category = cfg.category || null

  try {
    let items = await fetchItems(status, category)

    // If we have a category view, filter client-side by classification_label
    if (category) {
      items = items.filter(it => {
        const label = (it.classification_label || it.item?.classification_label || '').toLowerCase()
        return label === category
      })
    }

    updateStats()
    renderList(items)
  } catch (err) {
    itemsList.innerHTML = `<li class="empty-row" style="color:#c03030">⚠ ${err.message}</li>`
  }
}

function renderList(items) {
  if (!items || items.length === 0) {
    itemsList.innerHTML = '<li class="empty-row">Nothing here yet.</li>'
    return
  }

  itemsList.innerHTML = ''
  items.forEach(item => {
    const id    = item.item_id || item.id
    const title = item.item?.title || item.title || '(Untitled)'
    const label = (item.classification_label || item.item?.classification_label || '').toLowerCase() || 'review'
    const ts    = item.item?.created_at || item.created_at || ''
    const dateStr = ts ? new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''

    const li = document.createElement('li')
    li.className = 'item-row'
    li.dataset.itemId = id
    if (currentItem?.id === id) li.classList.add('active')

    li.innerHTML = `
      <div class="item-row-info">
        <div class="item-row-title">${escHtml(title)}</div>
        ${dateStr ? `<div class="item-row-sub">${dateStr}</div>` : ''}
      </div>
      <span class="row-pill ${label}">${label === 'review' ? 'Review' : capitalize(label)}</span>
      <svg class="row-chevron" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M7 5l5 5-5 5"/>
      </svg>`

    li.addEventListener('click', () => selectItem(id))
    itemsList.appendChild(li)
  })
}

// ── SELECT ITEM ───────────────────────────────
async function selectItem(id) {
  // Highlight row
  $$('.item-row').forEach(r => r.classList.toggle('active', r.dataset.itemId === id))

  showDetail(null)  // show loading state
  actionMsg.textContent = ''

  try {
    // Fetch item + classification in parallel
    const [item, cls] = await Promise.all([
      apiFetch(`/items/${id}`),
      apiFetch(`/items/${id}/classification`).catch(() => null)
    ])

    currentItem = item
    // Cache the class_slug so doAction always has a valid slug ready
    currentItem._class_slug = cls?.classification?.class_slug || null

    // Populate detail
    const label = (cls?.classification_label || item.classification_label || '').toLowerCase()
    detailCatTag.textContent = label ? capitalize(label) : '—'
    detailTitle.textContent  = item.title || '(Untitled)'
    detailMeta.textContent   = item.created_at
      ? new Date(item.created_at).toLocaleString('en-US', { dateStyle:'medium', timeStyle:'short' })
      : ''
    detailContent.textContent = item.content || ''

    // Classification
    const conf = cls?.confidence ?? item.classification_confidence ?? 0
    detailClassLabel.textContent = label ? capitalize(label) : '—'
    detailClassLabel.className   = `class-pill ${label}`
    detailConfBar.style.width    = `${Math.round(conf * 100)}%`
    detailConfPct.textContent    = `${Math.round(conf * 100)}%`

    const status = cls?.status || item.classification_status || 'needs_review'
    detailStatus.textContent  = status.replace('_', ' ')
    detailStatus.className    = `status-chip ${status}`

    // Reset review fields
    overrideCategory.value = ''
    overrideNotes.value    = ''

    // Audit trail
    const history = cls?.history || item.history || []
    renderAudit(history)

    showDetail(item)
  } catch (err) {
    actionMsg.textContent = '⚠ ' + err.message
    actionMsg.className   = 'action-msg error'
  }
}

function showDetail(item) {
  if (!item) {
    detailPlaceholder.classList.add('hidden')
    detailBody.classList.add('hidden')
    return
  }
  detailPlaceholder.classList.add('hidden')
  detailBody.classList.remove('hidden')
}

function renderAudit(history) {
  if (!history || history.length === 0) {
    auditSection.style.display = 'none'
    return
  }
  auditSection.style.display = 'block'
  auditTrail.innerHTML = history.map(e => `
    <div class="audit-entry">
      <div class="audit-action">${escHtml(e.action || e.status || '—')}</div>
      <div class="audit-time">${e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}</div>
      ${e.notes ? `<div class="audit-note">${escHtml(e.notes)}</div>` : ''}
    </div>`).join('')
}

// ── STATS ─────────────────────────────────────
async function updateStats() {
  try {
    const all     = await apiFetch('/items?limit=500').catch(() => ({ items: [] }))
    const items   = Array.isArray(all) ? all : all.items || []
    const total   = items.length
    const pending = items.filter(i => (i.classification_status || '') === 'needs_review').length
    const approved = items.filter(i => (i.classification_status || '') === 'accepted').length

    statTotal.textContent    = total
    statPending.textContent  = pending
    statApproved.textContent = approved
    navBadge.textContent     = pending
  } catch (_) { /* silently ignore */ }
}

// ── CAPTURE MODAL ─────────────────────────────
function openCaptureModal() {
  captureOverlay.classList.remove('hidden')
  captureTitle.focus()
}

function closeCaptureModal() {
  captureOverlay.classList.add('hidden')
  captureMsg.textContent = ''
  captureMsg.className   = 'capture-msg'
  captureTitle.value   = ''
  captureContent.value = ''
  captureCat.value     = ''
}

async function handleCapture() {
  const title   = captureTitle.value.trim()
  const content = captureContent.value.trim()
  if (!content) { setCaptureMsg('Add some content first.', 'error'); return }

  captureSubmit.disabled = true
  setCaptureMsg('Capturing…', '')

  try {
    await apiFetch('/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || 'Untitled', content })
    })
    setCaptureMsg('✓ Captured!', 'success')
    setTimeout(() => {
      closeCaptureModal()
      loadList()
    }, 700)
  } catch (err) {
    setCaptureMsg('⚠ ' + err.message, 'error')
  } finally {
    captureSubmit.disabled = false
  }
}

function setCaptureMsg(text, cls) {
  captureMsg.textContent = text
  captureMsg.className   = 'capture-msg ' + cls
}

// ── REVIEW ACTIONS ────────────────────────────
async function doAction(action) {
  if (!currentItem) return

  const cat   = overrideCategory.value.trim() || null
  const notes = overrideNotes.value.trim()

  // For modify, a category override must be selected
  if (action === 'modify' && !cat) {
    setActionMsg('Select a category to reassign.', 'error')
    return
  }

  // class_slug is required by the API — fall back to the item's existing slug/label
  const existingSlug = currentItem._class_slug || currentItem.classification_label || currentItem.label || ''
  const classSlug    = cat || existingSlug

  if (!classSlug) {
    setActionMsg('No category found — select one first.', 'error')
    return
  }

  setActionMsg('Saving…', '')

  try {
    await apiFetch(`/items/${currentItem.id}/classification/override`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action:     action === 'modify' ? 'approve' : action,
        class_slug: classSlug,
        notes:      notes || null,
      })
    })
    setActionMsg(action === 'approve' ? '✓ Approved' : action === 'reject' ? '✓ Rejected' : '✓ Modified', 'success')
    setTimeout(() => loadList(), 800)
  } catch (err) {
    setActionMsg('⚠ ' + err.message, 'error')
  }
}

function setActionMsg(text, cls) {
  actionMsg.textContent = text
  actionMsg.className   = 'action-msg ' + cls
}

// ── MISC UTILS ────────────────────────────────
const escHtml = s => s?.toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') ?? ''
const capitalize = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : s

// ── EVENT WIRING ──────────────────────────────
// Nav
navItems.forEach(n => {
  n.addEventListener('click', () => setView(n.dataset.view))
})

// Tabs
filterTabs.forEach(t => {
  t.addEventListener('click', () => {
    filterTabs.forEach(x => x.classList.remove('active'))
    t.classList.add('active')
    currentFilter = t.dataset.filter
    loadList()
  })
})

// Toolbar
refreshBtn.addEventListener('click', loadList)
newCaptureBtn.addEventListener('click', openCaptureModal)

// Capture modal
captureClose.addEventListener('click', closeCaptureModal)
captureOverlay.addEventListener('click', e => { if (e.target === captureOverlay) closeCaptureModal() })
captureSubmit.addEventListener('click', handleCapture)
captureContent.addEventListener('keydown', e => { if (e.ctrlKey && e.key === 'Enter') handleCapture() })

// Detail panel
closeDetailBtn.addEventListener('click', () => {
  detailPlaceholder.classList.remove('hidden')
  detailBody.classList.add('hidden')
  $$('.item-row').forEach(r => r.classList.remove('active'))
  currentItem = null
})

approveBtn.addEventListener('click', () => doAction('approve'))
modifyBtn.addEventListener('click',  () => doAction('modify'))
rejectBtn.addEventListener('click',  () => doAction('reject'))

// Keyboard shortcut: Escape closes capture modal
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeCaptureModal()
})

// ── BOOT ──────────────────────────────────────
setView('inbox')
