/**
 * MindMapViewer - Interactive Mind Map Viewer with Pure JavaScript
 * 
 * Features:
 * - Zoom in/out (mouse wheel, pinch gestures, keyboard +/-)
 * - Pan (drag, two-finger touch)
 * - Clickable nodes with side panel details
 * - Expand/collapse subtrees
 * - Keyboard navigation (arrow keys, Enter, Escape)
 * - Smooth animated transitions
 * - Touch-friendly for mobile devices
 * 
 * Note: Pure JavaScript implementation with no external dependencies
 */
class MindMapViewer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }

        // Configuration
        this.config = {
            initialZoom: options.initialZoom || 1,
            minZoom: options.minZoom || 0.1,
            maxZoom: options.maxZoom || 4,
            showLabels: options.showLabels !== false,
            nodeRadius: options.nodeRadius || 20,
            linkDistance: options.linkDistance || 150,
            onNodeClick: options.onNodeClick || null,
            enableKeyboard: options.enableKeyboard !== false,
            enableTouch: options.enableTouch !== false
        };

        // State
        this.nodeMap = new Map();
        this.collapsedNodes = new Set();
        this.selectedNode = null;
        this.currentZoom = this.config.initialZoom;
        this.translateX = 0;
        this.translateY = 0;
        this.isPanning = false;
        this.panStart = { x: 0, y: 0 };
        this.isDraggingNode = false;
        this.draggedNode = null;
        this.dragStart = { x: 0, y: 0 };
        this.customNodePositions = new Map();

        this.init();
    }

    init() {
        this.createLayout();
        this.setupEventListeners();
    }

    createLayout() {
        this.container.innerHTML = '';
        this.container.className = 'mindmap-container';

        // Canvas wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'mindmap-canvas-wrapper';
        this.container.appendChild(wrapper);

        // SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('class', 'mindmap-canvas');
        this.svg.setAttribute('width', '100%');
        this.svg.setAttribute('height', '100%');
        this.svg.setAttribute('role', 'img');
        this.svg.setAttribute('aria-label', 'Interactive mind map visualization');
        wrapper.appendChild(this.svg);

        // SVG groups
        this.linkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.linkGroup.setAttribute('class', 'links');
        this.svg.appendChild(this.linkGroup);

        this.nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.nodeGroup.setAttribute('class', 'nodes');
        this.svg.appendChild(this.nodeGroup);

        // Controls
        this.createControls(wrapper);
        
        // Side panel
        this.createSidePanel();
        
        // Indicators
        this.createZoomIndicator(wrapper);
        if (this.config.enableKeyboard) {
            this.createKeyboardHelp(wrapper);
        }
    }

    createControls(wrapper) {
        const controls = document.createElement('div');
        controls.className = 'mindmap-controls';
        controls.innerHTML = `
            <button class="control-btn" id="zoom-in" aria-label="Zoom in" title="Zoom in (+)">
                <i class="fas fa-plus"></i>
            </button>
            <button class="control-btn" id="zoom-out" aria-label="Zoom out" title="Zoom out (-)">
                <i class="fas fa-minus"></i>
            </button>
            <button class="control-btn" id="reset-view" aria-label="Reset view" title="Reset view (R)">
                <i class="fas fa-compress"></i>
            </button>
            <button class="control-btn" id="expand-all" aria-label="Expand all" title="Expand all nodes">
                <i class="fas fa-expand-alt"></i>
            </button>
            <button class="control-btn" id="collapse-all" aria-label="Collapse all" title="Collapse all nodes">
                <i class="fas fa-compress-alt"></i>
            </button>
        `;
        wrapper.appendChild(controls);

        controls.querySelector('#zoom-in').addEventListener('click', () => this.zoomIn());
        controls.querySelector('#zoom-out').addEventListener('click', () => this.zoomOut());
        controls.querySelector('#reset-view').addEventListener('click', () => this.resetView());
        controls.querySelector('#expand-all').addEventListener('click', () => this.expandAll());
        controls.querySelector('#collapse-all').addEventListener('click', () => this.collapseAll());
    }

    createSidePanel() {
        const panel = document.createElement('div');
        panel.className = 'mindmap-side-panel hidden';
        panel.id = 'mind-map-side-panel';
        panel.innerHTML = `
            <div class="side-panel-header">
                <h2>Node Details</h2>
                <button class="close-panel-btn" aria-label="Close panel">&times;</button>
            </div>
            <div class="node-details" id="node-details-content"></div>
        `;
        this.container.appendChild(panel);

        panel.querySelector('.close-panel-btn').addEventListener('click', () => {
            this.hideSidePanel();
        });
    }

    createZoomIndicator(wrapper) {
        const indicator = document.createElement('div');
        indicator.className = 'zoom-indicator';
        indicator.id = 'zoom-indicator';
        indicator.textContent = `Zoom: ${Math.round(this.currentZoom * 100)}%`;
        wrapper.appendChild(indicator);
    }

    createKeyboardHelp(wrapper) {
        const help = document.createElement('div');
        help.className = 'keyboard-help';
        help.innerHTML = `
            <h4>Keyboard Shortcuts</h4>
            <ul>
                <li><kbd>+</kbd> / <kbd>-</kbd> Zoom in/out</li>
                <li><kbd>R</kbd> Reset view</li>
                <li><kbd>Space</kbd> Toggle expand</li>
                <li><kbd>Enter</kbd> Open details</li>
                <li><kbd>Esc</kbd> Close panel</li>
            </ul>
            <h4>Mouse Controls</h4>
            <ul>
                <li>Drag nodes to move</li>
                <li>Click <strong>+/−</strong> to expand/collapse</li>
                <li>Drag background to pan</li>
            </ul>
        `;
        wrapper.appendChild(help);
    }

    setupEventListeners() {
        // Mouse events
        this.svg.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.svg.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });

        // Touch events
        if (this.config.enableTouch) {
            this.svg.addEventListener('touchstart', (e) => this.handleTouchStart(e));
            this.svg.addEventListener('touchmove', (e) => this.handleTouchMove(e));
            this.svg.addEventListener('touchend', (e) => this.handleTouchEnd(e));
        }

        // Keyboard
        if (this.config.enableKeyboard) {
            document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        }
    }

    loadData(data) {
        if (!data || !data.nodes || !data.edges) {
            console.error('Invalid data format');
            return;
        }

        // Build node map and adjacency lists
        this.nodeMap.clear();
        data.nodes.forEach(node => {
            node.children = [];
            node.parents = [];
            this.nodeMap.set(node.id, node);
        });

        data.edges.forEach(edge => {
            const source = this.nodeMap.get(edge.source);
            const target = this.nodeMap.get(edge.target);
            if (source && target) {
                source.children.push(target);
                target.parents.push(source);
            }
        });

        // Collapse all non-root nodes by default for a cleaner initial view
        this.collapsedNodes.clear();
        this.nodeMap.forEach((node, id) => {
            if (node.children && node.children.length > 0 && node.type !== 'root') {
                this.collapsedNodes.add(id);
            }
        });

        this.render();
    }

    render() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        // Find root nodes
        const roots = [];
        this.nodeMap.forEach(node => {
            if (!node.parents || node.parents.length === 0) {
                roots.push(node);
            }
        });

        if (roots.length === 0) {
            this.showEmptyState();
            return;
        }

        // Layout nodes in tree structure
        const layoutData = this.layoutTree(roots, width, height);
        
        // Clear existing
        this.linkGroup.innerHTML = '';
        this.nodeGroup.innerHTML = '';

        // Render links
        layoutData.links.forEach(link => this.renderLink(link));

        // Render nodes
        layoutData.nodes.forEach(node => this.renderNode(node));

        // Apply initial transform
        this.applyTransform();
    }

    layoutTree(roots, width, height) {
        const nodes = [];
        const links = [];
        const visited = new Set();
        
        const centerX = width / 2;
        const centerY = height / 2;
        const levelGap = this.config.linkDistance;

        const traverse = (node, depth, parentX, parentY, angle, spread) => {
            if (visited.has(node.id)) return;
            visited.add(node.id);

            let x, y;
            // Check if node has custom position
            if (this.customNodePositions.has(node.id)) {
                const customPos = this.customNodePositions.get(node.id);
                x = customPos.x;
                y = customPos.y;
            } else if (depth === 0) {
                // Root node at center
                x = centerX;
                y = centerY;
            } else {
                // Position children in a circle around parent
                x = parentX + Math.cos(angle) * levelGap * depth;
                y = parentY + Math.sin(angle) * levelGap * depth;
            }

            node.x = x;
            node.y = y;
            node.depth = depth;
            nodes.push(node);

            // Add link from parent
            if (depth > 0 && parentX !== undefined) {
                links.push({
                    source: { x: parentX, y: parentY },
                    target: { x, y },
                    sourceNode: node.parents[0],
                    targetNode: node
                });
            }

            // Layout children
            if (!this.collapsedNodes.has(node.id) && node.children && node.children.length > 0) {
                const childCount = node.children.length;
                const angleStep = (spread * 2) / Math.max(childCount - 1, 1);
                
                node.children.forEach((child, i) => {
                    const childAngle = angle - spread + (angleStep * i);
                    const childSpread = spread * 0.6; // Narrow down for deeper levels
                    traverse(child, depth + 1, x, y, childAngle, childSpread);
                });
            }
        };

        // Start from roots
        if (roots.length === 1) {
            traverse(roots[0], 0, undefined, undefined, 0, Math.PI);
        } else {
            const angleStep = (2 * Math.PI) / roots.length;
            roots.forEach((root, i) => {
                const angle = i * angleStep;
                traverse(root, 0, centerX, centerY, angle, Math.PI / roots.length);
            });
        }

        return { nodes, links };
    }

    renderLink(link) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('class', 'link');
        line.setAttribute('x1', link.source.x);
        line.setAttribute('y1', link.source.y);
        line.setAttribute('x2', link.target.x);
        line.setAttribute('y2', link.target.y);
        line.setAttribute('stroke', 'rgba(255, 255, 255, 0.2)');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('data-source-id', link.sourceNode.id);
        line.setAttribute('data-target-id', link.targetNode.id);
        this.linkGroup.appendChild(line);
    }

    renderNode(node) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'node');
        g.setAttribute('data-node-id', node.id);
        g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', node.label);

        // Determine radius based on node type
        const radius = node.type === 'root' ? this.config.nodeRadius * 1.5 :
                      node.type === 'branch' ? this.config.nodeRadius * 1.2 :
                      this.config.nodeRadius;
        
        // Check if node has a logo path
        const logoPath = node.metadata?.logo || node.metadata?.logoPath;
        
        if (logoPath) {
            // Render logo image
            const imageSize = radius * 2;
            
            // Background circle for logo
            const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            bgCircle.setAttribute('r', radius);
            bgCircle.setAttribute('fill', '#ffffff');
            bgCircle.setAttribute('stroke', node.metadata?.color || '#4a9eff');
            bgCircle.setAttribute('stroke-width', '2');
            bgCircle.setAttribute('fill-opacity', '0.9');
            g.appendChild(bgCircle);
            
            // Create clipPath for circular logo
            const clipPathId = `clip-${node.id}`;
            const clipPath = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath');
            clipPath.setAttribute('id', clipPathId);
            const clipCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            clipCircle.setAttribute('r', radius - 2);
            clipCircle.setAttribute('cx', 0);
            clipCircle.setAttribute('cy', 0);
            clipPath.appendChild(clipCircle);
            
            // Add clipPath to defs
            let defs = this.svg.querySelector('defs');
            if (!defs) {
                defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
                this.svg.insertBefore(defs, this.svg.firstChild);
            }
            defs.appendChild(clipPath);
            
            // Logo image
            const image = document.createElementNS('http://www.w3.org/2000/svg', 'image');
            image.setAttribute('href', logoPath);
            image.setAttribute('x', -radius + 2);
            image.setAttribute('y', -radius + 2);
            image.setAttribute('width', imageSize - 4);
            image.setAttribute('height', imageSize - 4);
            image.setAttribute('clip-path', `url(#${clipPathId})`);
            image.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            g.appendChild(image);
        } else {
            // Fallback to colored circle for nodes without logos
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', radius);
            circle.setAttribute('fill', node.metadata?.color || '#4a9eff');
            circle.setAttribute('stroke', node.metadata?.color || '#4a9eff');
            circle.setAttribute('stroke-width', '2');
            circle.setAttribute('fill-opacity', '0.2');
            g.appendChild(circle);
        }

        // Label
        if (this.config.showLabels) {
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('dy', radius + 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#ffffff');
            text.setAttribute('font-size', '12px');
            text.textContent = node.label;
            g.appendChild(text);
        }

        // Collapse indicator
        if (node.children && node.children.length > 0) {
            const indicator = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            indicator.setAttribute('class', 'collapse-indicator');
            indicator.setAttribute('r', '8');
            indicator.setAttribute('cx', radius - 2);
            indicator.setAttribute('cy', -radius + 2);
            indicator.setAttribute('fill', this.collapsedNodes.has(node.id) ? 'rgba(74, 158, 255, 0.9)' : 'rgba(255, 255, 255, 0.9)');
            indicator.setAttribute('stroke', '#4a9eff');
            indicator.setAttribute('stroke-width', '2');
            indicator.style.cursor = 'pointer';
            g.appendChild(indicator);

            // Add plus/minus symbol
            const symbol = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            symbol.setAttribute('x', radius - 2);
            symbol.setAttribute('y', -radius + 2);
            symbol.setAttribute('text-anchor', 'middle');
            symbol.setAttribute('dominant-baseline', 'central');
            symbol.setAttribute('fill', '#000');
            symbol.setAttribute('font-size', '12px');
            symbol.setAttribute('font-weight', 'bold');
            symbol.setAttribute('pointer-events', 'none');
            symbol.textContent = this.collapsedNodes.has(node.id) ? '+' : '−';
            g.appendChild(symbol);

            // Add click handler for toggle button
            indicator.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleNodeCollapse(node);
            });
        }

        // Mark collapsed
        if (this.collapsedNodes.has(node.id)) {
            g.classList.add('collapsed');
        }

        // Events
        g.addEventListener('click', (e) => this.handleNodeClick(e, node));
        
        // Enable dragging on nodes
        g.addEventListener('mousedown', (e) => this.handleNodeMouseDown(e, node));
        g.style.cursor = 'move';

        this.nodeGroup.appendChild(g);
    }

    applyTransform() {
        const transform = `translate(${this.translateX}, ${this.translateY}) scale(${this.currentZoom})`;
        this.nodeGroup.setAttribute('transform', transform);
        this.linkGroup.setAttribute('transform', transform);
    }

    handleMouseDown(e) {
        if (e.button === 0 && !e.target.closest('.node')) {
            this.isPanning = true;
            this.panStart = { x: e.clientX - this.translateX, y: e.clientY - this.translateY };
            this.svg.style.cursor = 'grabbing';
        }
    }

    handleMouseMove(e) {
        if (this.isDraggingNode && this.draggedNode) {
            e.preventDefault();
            // Calculate new position in SVG coordinates
            const svgRect = this.svg.getBoundingClientRect();
            const x = (e.clientX - svgRect.left - this.translateX) / this.currentZoom;
            const y = (e.clientY - svgRect.top - this.translateY) / this.currentZoom;
            
            // Update the dragged node position
            this.customNodePositions.set(this.draggedNode.id, { x, y });
            this.draggedNode.x = x;
            this.draggedNode.y = y;
            
            // Update the node's transform
            const nodeEl = this.nodeGroup.querySelector(`[data-node-id="${this.draggedNode.id}"]`);
            if (nodeEl) {
                nodeEl.setAttribute('transform', `translate(${x}, ${y})`);
                nodeEl.style.opacity = '0.7';
            }
            
            // Update connected links
            this.updateNodeLinks(this.draggedNode);
        } else if (this.isPanning) {
            this.translateX = e.clientX - this.panStart.x;
            this.translateY = e.clientY - this.panStart.y;
            this.applyTransform();
        }
    }

    handleMouseUp(e) {
        if (this.isDraggingNode && this.draggedNode) {
            // Reset opacity
            const nodeEl = this.nodeGroup.querySelector(`[data-node-id="${this.draggedNode.id}"]`);
            if (nodeEl) {
                nodeEl.style.opacity = '1';
            }
            this.isDraggingNode = false;
            this.draggedNode = null;
        }
        this.isPanning = false;
        this.svg.style.cursor = 'grab';
    }

    handleNodeMouseDown(e, node) {
        // Don't start dragging if clicking the collapse indicator
        if (e.target.classList.contains('collapse-indicator')) {
            return;
        }
        
        e.stopPropagation();
        this.isDraggingNode = true;
        this.draggedNode = node;
        this.dragStart = { x: e.clientX, y: e.clientY };
    }

    updateNodeLinks(node) {
        // Update all links connected to this node
        const links = this.linkGroup.querySelectorAll('line');
        links.forEach(link => {
            const sourceId = link.getAttribute('data-source-id');
            const targetId = link.getAttribute('data-target-id');
            
            if (sourceId === node.id) {
                link.setAttribute('x1', node.x);
                link.setAttribute('y1', node.y);
            }
            if (targetId === node.id) {
                link.setAttribute('x2', node.x);
                link.setAttribute('y2', node.y);
            }
        });
    }

    handleWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoom(delta);
    }

    handleTouchStart(e) {
        if (e.touches.length === 2) {
            this.lastTouchDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
        } else if (e.touches.length === 1) {
            this.isPanning = true;
            this.panStart = {
                x: e.touches[0].clientX - this.translateX,
                y: e.touches[0].clientY - this.translateY
            };
        }
    }

    handleTouchMove(e) {
        e.preventDefault();
        
        if (e.touches.length === 2) {
            const distance = this.getTouchDistance(e.touches[0], e.touches[1]);
            if (this.lastTouchDistance > 0) {
                const scale = distance / this.lastTouchDistance;
                this.zoom(scale);
            }
            this.lastTouchDistance = distance;
        } else if (e.touches.length === 1 && this.isPanning) {
            this.translateX = e.touches[0].clientX - this.panStart.x;
            this.translateY = e.touches[0].clientY - this.panStart.y;
            this.applyTransform();
        }
    }

    handleTouchEnd(e) {
        this.isPanning = false;
        this.lastTouchDistance = 0;
    }

    getTouchDistance(touch1, touch2) {
        const dx = touch2.clientX - touch1.clientX;
        const dy = touch2.clientY - touch1.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    handleKeyDown(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch(e.key) {
            case '+':
            case '=':
                e.preventDefault();
                this.zoomIn();
                break;
            case '-':
            case '_':
                e.preventDefault();
                this.zoomOut();
                break;
            case 'r':
            case 'R':
                e.preventDefault();
                this.resetView();
                break;
            case ' ':
                e.preventDefault();
                if (this.selectedNode) this.toggleNodeCollapse(this.selectedNode);
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedNode) this.showNodeDetails(this.selectedNode);
                break;
            case 'Escape':
                e.preventDefault();
                this.hideSidePanel();
                break;
        }
    }

    handleNodeClick(e, node) {
        e.stopPropagation();
        this.selectNode(node);
        this.showNodeDetails(node);
        if (this.config.onNodeClick) {
            this.config.onNodeClick(node);
        }
    }

    selectNode(node) {
        this.selectedNode = node;
        this.nodeGroup.querySelectorAll('.node').forEach(n => {
            n.classList.remove('selected');
        });
        const nodeEl = this.nodeGroup.querySelector(`[data-node-id="${node.id}"]`);
        if (nodeEl) {
            nodeEl.classList.add('selected');
        }
    }

    showNodeDetails(node) {
        const panel = document.getElementById('mind-map-side-panel');
        const content = document.getElementById('node-details-content');

        const childCount = node.children ? node.children.length : 0;
        const parentCount = node.parents ? node.parents.length : 0;

        content.innerHTML = `
            <i class="node-icon ${node.metadata?.icon || 'fas fa-circle'}"></i>
            <div class="node-label">${node.label}</div>
            <span class="node-type">${node.type || 'node'}</span>
            <p class="node-description">${node.description || 'No description available.'}</p>
            
            ${childCount > 0 ? `
                <div class="node-connections">
                    <h3>Connected To (${childCount})</h3>
                    <ul class="connection-list">
                        ${node.children.map(child => `
                            <li class="connection-item" data-node-id="${child.id}">
                                ${child.label}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${parentCount > 0 ? `
                <div class="node-connections">
                    <h3>Connected From (${parentCount})</h3>
                    <ul class="connection-list">
                        ${node.parents.map(parent => `
                            <li class="connection-item" data-node-id="${parent.id}">
                                ${parent.label}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;

        content.querySelectorAll('.connection-item').forEach(item => {
            item.addEventListener('click', () => {
                const nodeId = item.getAttribute('data-node-id');
                const targetNode = this.nodeMap.get(nodeId);
                if (targetNode) {
                    this.selectNode(targetNode);
                    this.showNodeDetails(targetNode);
                    this.focusNode(targetNode);
                }
            });
        });

        panel.classList.remove('hidden');
    }

    hideSidePanel() {
        const panel = document.getElementById('mind-map-side-panel');
        panel.classList.add('hidden');
    }

    toggleNodeCollapse(node) {
        if (!node.children || node.children.length === 0) return;

        if (this.collapsedNodes.has(node.id)) {
            this.collapsedNodes.delete(node.id);
        } else {
            this.collapsedNodes.add(node.id);
        }

        this.render();
    }

    expandAll() {
        this.collapsedNodes.clear();
        this.render();
    }

    collapseAll() {
        this.nodeMap.forEach((node, id) => {
            if (node.children && node.children.length > 0 && node.type !== 'root') {
                this.collapsedNodes.add(id);
            }
        });
        this.render();
    }

    focusNode(node) {
        if (!node.x || !node.y) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.translateX = -node.x * this.currentZoom + width / 2;
        this.translateY = -node.y * this.currentZoom + height / 2;
        this.applyTransform();
    }

    zoom(scale) {
        const newZoom = this.currentZoom * scale;
        this.currentZoom = Math.max(this.config.minZoom, Math.min(this.config.maxZoom, newZoom));
        this.applyTransform();
        this.updateZoomIndicator();
    }

    zoomIn() {
        this.zoom(1.2);
    }

    zoomOut() {
        this.zoom(0.8);
    }

    resetView() {
        this.currentZoom = this.config.initialZoom;
        this.translateX = 0;
        this.translateY = 0;
        this.applyTransform();
        this.updateZoomIndicator();
    }

    updateZoomIndicator() {
        const indicator = document.getElementById('zoom-indicator');
        if (indicator) {
            indicator.textContent = `Zoom: ${Math.round(this.currentZoom * 100)}%`;
        }
    }

    showEmptyState() {
        const wrapper = this.container.querySelector('.mindmap-canvas-wrapper');
        wrapper.innerHTML = `
            <div class="mindmap-empty">
                <i class="fas fa-project-diagram"></i>
                <p>No data to display</p>
            </div>
        `;
    }

    destroy() {
        this.container.innerHTML = '';
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MindMapViewer;
}
