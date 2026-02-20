class SimpleBlueprint {
    constructor() {
        this.data = [];
        this.nextId = 1;
        this.selectedItem = null;
        this.currentParent = null;
        this.isMindMapView = false;
        this.collapsedFolders = new Set(); // Track which folders are collapsed
        
        // Logo mapping for quick lookups (performance optimization)
        this.logoMap = new Map([
            ['Bank_of_America', 'Accounts_Banking/Bank_of_America/logo.svg'],
            ['Wells_Fargo', 'Accounts_Banking/Wells_Fargo/logo.png'],
            ['Chase', 'Accounts_Banking/Chase/logo.png'],
            ['American_Express', 'Accounts_Banking/American_Express/logo.png'],
            ['Credit_One', 'Accounts_Banking/Other_Cards/Credit_One/logo.png'],
            ['Indigo', 'Accounts_Banking/Other_Cards/Indigo/logo.png'],
            ['Nordstrom', 'Accounts_Banking/Other_Cards/Nordstrom/logo.png'],
            ['Synchrony', 'Accounts_Banking/Other_Cards/Synchrony/logo.png'],
            ['Car_HondaFS', 'Bills_Payments/Car_HondaFS/logo.png'],
            ['Phone_ATT', 'Bills_Payments/Phone_ATT/logo.png'],
            ['Insurance_Allstate', 'Bills_Payments/Insurance_Allstate/logo.png'],
            ['Water_Minol', 'Bills_Payments/Utilities/Water_Minol/logo.png'],
            ['Electric_PSO', 'Bills_Payments/Utilities/Electric_PSO/logo.svg'],
            ['Gas_ONG', 'Bills_Payments/Utilities/Gas_ONG/logo.svg'],
            ['Instagram', 'Daily_Life_Digital_Presence/Social_Media/Instagram/logo.png'],
            ['TikTok', 'Daily_Life_Digital_Presence/Social_Media/TikTok/logo.png'],
            ['Facebook', 'Daily_Life_Digital_Presence/Social_Media/Facebook/logo.png'],
            ['LinkedIn', 'Daily_Life_Digital_Presence/Social_Media/LinkedIn/logo.png'],
            ['Snapchat', 'Daily_Life_Digital_Presence/Social_Media/Snapchat/logo.png'],
            ['Gmail', 'Daily_Life_Digital_Presence/Email_Accounts/Gmail/logo.svg'],
            ['Outlook', 'Daily_Life_Digital_Presence/Email_Accounts/Outlook/logo.png'],
            ['Yahoo', 'Daily_Life_Digital_Presence/Email_Accounts/Yahoo/logo.png'],
            ['Netflix', 'Daily_Life_Digital_Presence/Entertainment/Netflix/logo.png'],
            ['Hulu', 'Daily_Life_Digital_Presence/Entertainment/Hulu/logo.png'],
            ['Disney+', 'Daily_Life_Digital_Presence/Entertainment/DisneyPlus/logo.png'],
            ['HBO_Max', 'Daily_Life_Digital_Presence/Entertainment/HBO_Max/logo.png'],
            ['Crunchyroll', 'Daily_Life_Digital_Presence/Entertainment/Crunchyroll/logo.png'],
            ['AMC', 'Daily_Life_Digital_Presence/Entertainment/AMC/logo.png'],
            ['Amazon', 'Daily_Life_Digital_Presence/Shopping/Amazon/logo.png'],
            ['Target', 'Daily_Life_Digital_Presence/Shopping/Target/logo.png'],
            ['Walmart', 'Daily_Life_Digital_Presence/Shopping/Walmart/logo.png'],
            ['BestBuy', 'Daily_Life_Digital_Presence/Shopping/BestBuy/logo.png'],
            ['Costco', 'Daily_Life_Digital_Presence/Shopping/Costco/logo.png'],
            ['PayPal', 'Financial_Tools/PayPal/logo.png'],
            ['Venmo', 'Financial_Tools/Venmo/logo.png'],
            ['CashApp', 'Financial_Tools/CashApp/logo.png'],
            ['Zelle', 'Financial_Tools/Zelle/logo.png'],
            ['iPhone15', 'Assets_Inventory/Electronics/iPhone15/logo.png'],
            ['MacBook', 'Assets_Inventory/Electronics/MacBook/logo.png'],
            ['Apple_Watch', 'Assets_Inventory/Electronics/Apple_Watch/logo.png'],
            ['Apple', 'Refunds_Service_Logs/Apple/logo.png'],
            ['Nike', 'Refunds_Service_Logs/Nike_Ross_HandAndStone/Nike/logo.png'],
            ['Ross', 'Refunds_Service_Logs/Nike_Ross_HandAndStone/Ross/logo.png'],
            ['Airbnb', 'Timeline/Travel/Airbnb/logo.png'],
            ['Delta', 'Timeline/Travel/Delta/logo.png'],
            ['Emirates', 'Timeline/Travel/Emirates/logo.png'],
            ['United', 'Timeline/Travel/United/logo.png']
        ]);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTreeEventDelegation(); // Add event delegation for tree items
        this.loadFromStorage();
        this.render();
    }

    setupEventListeners() {
        // Toolbar buttons 
        document.getElementById('loadPersonal').addEventListener('click', () => this.loadPersonalStructure());
        document.getElementById('addFolder').addEventListener('click', () => this.showAddModal('folder'));
        document.getElementById('addFile').addEventListener('click', () => this.showAddModal('file'));
        document.getElementById('exportJson').addEventListener('click', () => this.exportJson());
        document.getElementById('exportCsv').addEventListener('click', () => this.exportCsv());
        document.getElementById('mindMapToggle').addEventListener('click', () => this.toggleMindMap());

        // Modal events
        const modal = document.getElementById('addModal');
        const closeBtn = document.querySelector('.close');
        const saveBtn = document.getElementById('saveItem');

        closeBtn.addEventListener('click', () => this.hideModal());
        saveBtn.addEventListener('click', () => this.saveItem());

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideModal();
            }
        });

        // Enter key to save
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && modal.style.display === 'block') {
                this.saveItem();
            }
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }

    setupTreeEventDelegation() {
        // Use event delegation on the tree view container for better performance
        const treeView = document.getElementById('treeView');
        
        treeView.addEventListener('click', (e) => {
            const treeItem = e.target.closest('.tree-item');
            const actionBtn = e.target.closest('.action-btn');
            const collapseBtn = e.target.closest('.collapse-btn');
            
            if (collapseBtn) {
                // Handled by onclick in HTML
                return;
            }
            
            if (actionBtn) {
                e.stopPropagation();
                const action = actionBtn.dataset.action;
                const id = parseInt(actionBtn.dataset.id);
                
                switch(action) {
                    case 'add':
                        this.addChild(id);
                        break;
                    case 'edit':
                        this.editItem(id);
                        break;
                    case 'delete':
                        this.deleteItem(id);
                        break;
                }
                return;
            }
            
            if (treeItem && !e.target.closest('.actions') && !e.target.closest('.collapse-btn')) {
                const id = parseInt(treeItem.dataset.id);
                this.selectItem(id);
            }
        });
    }

    showAddModal(type) {
        this.currentType = type;
        this.currentParent = this.selectedItem ? this.selectedItem.id : null;
        
        document.getElementById('modalTitle').textContent = `Add ${type === 'folder' ? 'Folder' : 'File'}`;
        document.getElementById('itemName').value = '';
        document.getElementById('itemDescription').value = '';
        document.getElementById('addModal').style.display = 'block';
        document.getElementById('itemName').focus();
    }

    hideModal() {
        document.getElementById('addModal').style.display = 'none';
        this.currentType = null;
        this.currentParent = null;
    }

    saveItem() {
        const name = document.getElementById('itemName').value.trim();
        const description = document.getElementById('itemDescription').value.trim();

        if (!name) {
            alert('Please enter a name');
            return;
        }

        const item = {
            id: this.nextId++,
            name: name,
            description: description,
            type: this.currentType,
            parentId: this.currentParent,
            children: []
        };

        this.data.push(item);
        this.saveToStorage();
        this.render();
        this.hideModal();
    }

    render() {
        const treeView = document.getElementById('treeView');
        
        if (this.data.length === 0) {
            treeView.innerHTML = `
                <div class="welcome">
                    <i class="fas fa-folder-open"></i>
                    <p>Click + to add folders or files</p>
                </div>
            `;
            return;
        }

        // Use requestAnimationFrame for smoother rendering
        requestAnimationFrame(() => {
            const rootItems = this.data.filter(item => !item.parentId);
            const html = rootItems.map(item => this.renderItem(item)).join('');
            
            treeView.innerHTML = `
                <div class="tree-container">
                    ${html}
                </div>
            `;
        });
        // Event delegation is now handled globally, no need to attach listeners per render
    }

    renderItem(item) {
        const isSelected = this.selectedItem && this.selectedItem.id === item.id;
        const isCollapsed = this.collapsedFolders.has(item.id);
        
        // Only process children if folder is not collapsed (performance optimization)
        let childrenHtml = '';
        if (item.type === 'folder' && !isCollapsed) {
            const children = this.data.filter(child => child.parentId === item.id);
            childrenHtml = children.map(child => this.renderItem(child)).join('');
        }
        
        // Determine icon and color based on file type
        let iconClass = 'fas fa-file';
        let iconColor = '#ff6b6b'; // Default red for files
        let logoPath = null;
        
        if (item.type === 'folder') {
            iconClass = 'fas fa-folder';
            iconColor = '#4a9eff'; // Blue for folders
            
            // Check for logos using the optimized Map lookup
            logoPath = this.logoMap.get(item.name);
        } else if (item.name.includes('_Notes') || item.name === 'Notes') {
            iconClass = 'fas fa-file-code';
            iconColor = '#f39c12'; // Yellow/orange for notes (JSON)
        } else if (item.name.includes('_Photos')) {
            iconClass = 'fas fa-images';
            iconColor = '#3498db'; // Blue for photos
        } else if (item.name === 'Credentials') {
            iconClass = 'fas fa-key';
            iconColor = '#9b59b6'; // Purple for credentials
        } else if (item.name === 'Account_Info') {
            iconClass = 'fas fa-info-circle';
            iconColor = '#3498db'; // Blue for account info
        }
        
        return `
            <div class="tree-item ${item.type} ${isSelected ? 'selected' : ''}" data-id="${item.id}">
                ${item.type === 'folder' ? `<button class="collapse-btn ${isCollapsed ? 'collapsed' : ''}" onclick="blueprint.toggleCollapse(${item.id})" title="${isCollapsed ? 'Expand' : 'Collapse'}"><i class="fas fa-chevron-right"></i></button>` : '<div class="collapse-spacer"></div>'}
                ${logoPath ? `<img src="${logoPath}" class="logo-icon" alt="${item.name} logo">` : `<i class="icon ${iconClass}" style="color: ${iconColor}"></i>`}
                <div class="content">
                    <div class="name">${item.name}</div>
                    ${item.description ? `<div class="description">${item.description}</div>` : ''}
                </div>
                <div class="actions">
                    ${item.type === 'folder' ? `<button class="action-btn" data-action="add" data-id="${item.id}" title="Add Child"><i class="fas fa-plus"></i></button>` : ''}
                    <button class="action-btn" data-action="edit" data-id="${item.id}" title="Edit"><i class="fas fa-edit"></i></button>
                    <button class="action-btn" data-action="delete" data-id="${item.id}" title="Delete"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            ${childrenHtml && !isCollapsed ? `<div class="tree-children">${childrenHtml}</div>` : ''}
        `;
    }


    toggleCollapse(folderId) {
        if (this.collapsedFolders.has(folderId)) {
            this.collapsedFolders.delete(folderId);
        } else {
            this.collapsedFolders.add(folderId);
        }
        this.render();
    }

    selectItem(id) {
        this.selectedItem = this.data.find(item => item.id === id);
        this.render();
    }

    addChild(parentId) {
        this.selectedItem = this.data.find(item => item.id === parentId);
        this.showAddModal('folder');
    }

    editItem(id) {
        const item = this.data.find(item => item.id === id);
        if (!item) return;

        this.currentEditId = id;
        document.getElementById('modalTitle').textContent = `Edit ${item.type}`;
        document.getElementById('itemName').value = item.name;
        document.getElementById('itemDescription').value = item.description || '';
        document.getElementById('addModal').style.display = 'block';
        document.getElementById('itemName').focus();
    }

    deleteItem(id) {
        const item = this.data.find(item => item.id === id);
        if (!item) return;

        const itemName = item.name;
        const hasChildren = this.data.some(child => child.parentId === id);
        
        let confirmMessage = `Are you sure you want to delete "${itemName}"?`;
        if (hasChildren) {
            confirmMessage += ` This will also delete all child items.`;
        }

        if (!confirm(confirmMessage)) {
            return;
        }

        // Remove item and all its children recursively
        const removeItemRecursive = (itemId) => {
            const children = this.data.filter(item => item.parentId === itemId);
            children.forEach(child => removeItemRecursive(child.id));
            this.data = this.data.filter(item => item.id !== itemId);
        };

        removeItemRecursive(id);
        this.saveToStorage();
        this.render();
        this.selectedItem = null;
        
        // Show success message
        this.showMessage(`"${itemName}" deleted successfully!`, 'success');
    }

    saveItem() {
        const name = document.getElementById('itemName').value.trim();
        const description = document.getElementById('itemDescription').value.trim();

        if (!name) {
            alert('Please enter a name');
            return;
        }

        if (this.currentEditId) {
            // Editing existing item
            const item = this.data.find(item => item.id === this.currentEditId);
            if (item) {
                item.name = name;
                item.description = description;
            }
            this.currentEditId = null;
        } else {
            // Adding new item
            const item = {
                id: this.nextId++,
                name: name,
                description: description,
                type: this.currentType,
                parentId: this.currentParent,
                children: []
            };
            this.data.push(item);
        }

        this.saveToStorage();
        this.render();
        this.hideModal();
    }

    toggleMindMap() {
        this.isMindMapView = !this.isMindMapView;
        const treeView = document.getElementById('treeView');
        const mindMapView = document.getElementById('mindMapView');
        
        if (this.isMindMapView) {
            treeView.style.display = 'none';
            mindMapView.style.display = 'block';
            this.renderMindMap();
        } else {
            treeView.style.display = 'block';
            mindMapView.style.display = 'none';
        }
    }

    renderMindMap() {
        const svg = document.getElementById('mindMapSvg');
        svg.innerHTML = '';

        if (this.data.length === 0) {
            return;
        }

        const width = svg.clientWidth;
        const height = svg.clientHeight;
        const centerX = width / 2;
        const centerY = height / 2;

        // Create root nodes (items without parents)
        const rootItems = this.data.filter(item => !item.parentId);
        
        if (rootItems.length === 0) return;

        // If only one root, center it
        if (rootItems.length === 1) {
            this.createMindMapNode(svg, rootItems[0], centerX, centerY, true);
            this.createChildNodes(svg, rootItems[0], centerX, centerY, 0);
        } else {
            // Multiple roots - arrange in circle
            const angleStep = (2 * Math.PI) / rootItems.length;
            rootItems.forEach((item, index) => {
                const angle = index * angleStep;
                const x = centerX + Math.cos(angle) * 150;
                const y = centerY + Math.sin(angle) * 150;
                this.createMindMapNode(svg, item, x, y, true);
                this.createChildNodes(svg, item, x, y, 0);
            });
        }
    }

    createMindMapNode(svg, item, x, y, isRoot = false) {
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        nodeGroup.classList.add('mind-node');
        nodeGroup.setAttribute('data-id', item.id);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', isRoot ? 25 : 20);
        circle.setAttribute('fill', item.type === 'folder' ? 'rgba(74, 158, 255, 0.2)' : 'rgba(255, 107, 107, 0.2)');
        circle.setAttribute('stroke', item.type === 'folder' ? '#4a9eff' : '#ff6b6b');
        circle.setAttribute('stroke-width', 2);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x);
        text.setAttribute('y', y);
        text.setAttribute('fill', '#ffffff');
        text.setAttribute('font-size', isRoot ? '14' : '12');
        text.setAttribute('font-weight', '500');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'central');
        
        // Truncate text if too long
        const maxLength = isRoot ? 12 : 8;
        const displayText = item.name.length > maxLength ? item.name.substring(0, maxLength) + '...' : item.name;
        text.textContent = displayText;

        nodeGroup.appendChild(circle);
        nodeGroup.appendChild(text);
        svg.appendChild(nodeGroup);

        // Add click event
        nodeGroup.addEventListener('click', () => {
            this.selectItem(item.id);
            this.toggleMindMap(); // Switch back to tree view
        });
    }

    createChildNodes(svg, parentItem, parentX, parentY, level) {
        const children = this.data.filter(item => item.parentId === parentItem.id);
        if (children.length === 0) return;

        const maxChildren = 6; // Limit children per level
        const angleStep = (2 * Math.PI) / Math.min(children.length, maxChildren);
        const radius = 80 + (level * 60);

        children.forEach((child, index) => {
            if (index >= maxChildren) return;

            const angle = index * angleStep;
            const x = parentX + Math.cos(angle) * radius;
            const y = parentY + Math.sin(angle) * radius;

            // Create connection line
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', parentX);
            line.setAttribute('y1', parentY);
            line.setAttribute('x2', x);
            line.setAttribute('y2', y);
            line.setAttribute('stroke', 'rgba(255, 255, 255, 0.2)');
            line.setAttribute('stroke-width', 1.5);
            line.classList.add('mind-link');
            svg.appendChild(line);

            // Create child node
            this.createMindMapNode(svg, child, x, y, false);
            this.createChildNodes(svg, child, x, y, level + 1);
        });
    }

    exportJson() {
        const dataStr = JSON.stringify(this.data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'blueprint.json';
        link.click();
        
        URL.revokeObjectURL(url);
    }

    exportCsv() {
        if (this.data.length === 0) {
            alert('No data to export. Please load data first.');
            return;
        }

        // Get all root categories (items without parents)
        const rootItems = this.data.filter(item => !item.parentId);
        
        // Export comprehensive CSV with all data
        this.exportComprehensiveCsv();
        
        // Export individual CSVs for each major category
        rootItems.forEach(rootItem => {
            this.exportCategoryCsv(rootItem);
        });
        
        this.showMessage('CSV files exported successfully!', 'success');
    }

    exportComprehensiveCsv() {
        // Build hierarchy path for each item
        const csvData = this.data.map(item => {
            const path = this.buildHierarchyPath(item);
            const parentName = item.parentId ? this.data.find(p => p.id === item.parentId)?.name || '' : '';
            const depth = this.getItemDepth(item);
            const childCount = this.data.filter(child => child.parentId === item.id).length;
            
            return {
                id: item.id,
                name: item.name,
                type: item.type,
                description: item.description || '',
                parentId: item.parentId || '',
                parentName: parentName,
                hierarchyPath: path,
                depth: depth,
                childCount: childCount
            };
        });

        // Sort by hierarchy path for logical ordering
        csvData.sort((a, b) => a.hierarchyPath.localeCompare(b.hierarchyPath));

        // Convert to CSV format
        const csvContent = this.convertToCSV(csvData);
        
        // Download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'blueprint_complete.csv';
        link.click();
        URL.revokeObjectURL(url);
    }

    exportCategoryCsv(rootItem) {
        // Get all descendants of this root item
        const descendants = this.getAllDescendants(rootItem.id);
        const categoryData = [rootItem, ...descendants];
        
        // Remove duplicates by ID (in case of data integrity issues)
        const seenIds = new Set();
        const uniqueCategoryData = categoryData.filter(item => {
            if (seenIds.has(item.id)) {
                return false;
            }
            seenIds.add(item.id);
            return true;
        });
        
        // Build CSV data
        const csvData = uniqueCategoryData.map(item => {
            const path = this.buildHierarchyPath(item);
            const parentName = item.parentId ? this.data.find(p => p.id === item.parentId)?.name || '' : '';
            const depth = this.getItemDepth(item);
            const childCount = this.data.filter(child => child.parentId === item.id).length;
            
            return {
                id: item.id,
                name: item.name,
                type: item.type,
                description: item.description || '',
                parentId: item.parentId || '',
                parentName: parentName,
                hierarchyPath: path,
                depth: depth,
                childCount: childCount
            };
        });

        // Sort by hierarchy path
        csvData.sort((a, b) => a.hierarchyPath.localeCompare(b.hierarchyPath));

        // Convert to CSV
        const csvContent = this.convertToCSV(csvData);
        
        // Download with category-specific filename
        const filename = `blueprint_${rootItem.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.csv`;
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }

    getAllDescendants(itemId) {
        const descendants = [];
        const children = this.data.filter(item => item.parentId === itemId);
        
        children.forEach(child => {
            descendants.push(child);
            descendants.push(...this.getAllDescendants(child.id));
        });
        
        return descendants;
    }

    buildHierarchyPath(item) {
        const path = [];
        let currentItem = item;
        
        while (currentItem) {
            path.unshift(currentItem.name);
            if (currentItem.parentId) {
                currentItem = this.data.find(p => p.id === currentItem.parentId);
            } else {
                currentItem = null;
            }
        }
        
        return path.join(' > ');
    }

    getItemDepth(item) {
        let depth = 0;
        let currentItem = item;
        
        while (currentItem && currentItem.parentId) {
            depth++;
            currentItem = this.data.find(p => p.id === currentItem.parentId);
        }
        
        return depth;
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        // Get headers from first object
        const headers = Object.keys(data[0]);
        
        // Escape CSV values
        const escapeCSV = (value) => {
            if (value === null || value === undefined) return '';
            const stringValue = String(value);
            if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
                return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
        };
        
        // Create CSV content
        const headerRow = headers.join(',');
        const dataRows = data.map(row => 
            headers.map(header => escapeCSV(row[header])).join(',')
        ).join('\n');
        
        return `${headerRow}\n${dataRows}`;
    }

    saveToStorage() {
        localStorage.setItem('blueprintData', JSON.stringify(this.data));
        localStorage.setItem('nextId', this.nextId.toString());
    }

    loadFromStorage() {
        const savedData = localStorage.getItem('blueprintData');
        const savedNextId = localStorage.getItem('nextId');
        
        // Check if we have saved data first
        if (savedData) {
            try {
                this.data = JSON.parse(savedData);
            } catch(e) {
                console.error('Error loading saved data:', e);
                this.data = [];
            }
        }
        
        if (savedNextId) {
            this.nextId = parseInt(savedNextId);
        }
    }

    loadPersonalStructure() {
        // Show loading indicator
        const loadingIndicator = document.getElementById('loadingIndicator');
        const treeView = document.getElementById('treeView');
        
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        if (treeView) {
            treeView.style.opacity = '0.3';
        }
        
        // Use setTimeout to make loading non-blocking
        setTimeout(() => {
            // Load data
            this.data = [
            // Root Personal folder
            { id: 1, name: "P - Personal", description: "Life, Home, ID, Contacts, Events", type: "folder", parentId: null },
            
            // Health
            { id: 500, name: "H - Health", description: "Medical, mental, and personal wellness information", type: "folder", parentId: null },
            
            // Work
            { id: 600, name: "W - Work", description: "Professional work history, employers, projects, and portfolio", type: "folder", parentId: null },
            
            // Projects
            { id: 700, name: "P - Projects", description: "Personal and professional development projects", type: "folder", parentId: null },
            
            // Medical_Records
            { id: 501, name: "Medical_Records", description: "Doctors, conditions, symptoms, and test history", type: "folder", parentId: 500 },
            { id: 502, name: "Doctors_and_Providers", description: "Contacts, specialties, visit notes", type: "folder", parentId: 501 },
            { id: 503, name: "Conditions_and_Symptoms", description: "Diagnoses, recurring issues, notes", type: "folder", parentId: 501 },
            { id: 504, name: "Lab_Results_and_Tests", description: "Reports and uploads from labs", type: "folder", parentId: 501 },
            { id: 505, name: "LabCorp", description: "LabCorp test results", type: "file", parentId: 504 },
            { id: 506, name: "Quest_Diagnostics", description: "Quest Diagnostics test results", type: "file", parentId: 504 },
            { id: 507, name: "Other_Labs", description: "Other laboratory test results", type: "file", parentId: 504 },
            { id: 508, name: "Timeline_and_Notes", description: "Chronological medical events and reflections", type: "folder", parentId: 501 },
            
            // Medications_and_Supplements
            { id: 509, name: "Medications_and_Supplements", description: "Current, past, and scheduled intake", type: "folder", parentId: 500 },
            { id: 510, name: "Active_Medications", description: "Currently prescribed medications", type: "file", parentId: 509 },
            { id: 511, name: "Past_Treatments", description: "Previous medications and treatments", type: "file", parentId: 509 },
            { id: 512, name: "Supplements", description: "Vitamins and dietary supplements", type: "file", parentId: 509 },
            { id: 513, name: "Dosage_and_Schedule", description: "Medication schedules and dosages", type: "file", parentId: 509 },
            
            // Insurance_and_Coverage
            { id: 514, name: "Insurance_and_Coverage", description: "Policies, claims, and provider networks", type: "folder", parentId: 500 },
            { id: 515, name: "Health_Insurance_Policies", description: "Health insurance policy information", type: "file", parentId: 514 },
            { id: 516, name: "Claims_and_EOBs", description: "Insurance claims and explanation of benefits", type: "file", parentId: 514 },
            { id: 517, name: "Provider_Network_Info", description: "In-network provider information", type: "file", parentId: 514 },
            
            // Mental_Health
            { id: 518, name: "Mental_Health", description: "Therapy, emotional tracking, and self-reflection", type: "folder", parentId: 500 },
            { id: 519, name: "Therapy_Notes", description: "Therapy session notes and insights", type: "file", parentId: 518 },
            { id: 520, name: "Mood_Tracking", description: "Emotional and mood tracking data", type: "file", parentId: 518 },
            { id: 521, name: "Reflections", description: "Personal reflections and journaling", type: "file", parentId: 518 },
            
            // Health_Apps
            { id: 522, name: "Health_Apps", description: "Linked apps and digital health platforms", type: "folder", parentId: 500 },
            { id: 523, name: "MyChart", description: "MyChart health portal", type: "file", parentId: 522 },
            { id: 524, name: "Healow", description: "Healow health app", type: "file", parentId: 522 },
            { id: 525, name: "PT_Solutions", description: "PT Solutions physical therapy", type: "file", parentId: 522 },
            { id: 526, name: "BetterSleep", description: "BetterSleep app", type: "file", parentId: 522 },
            { id: 527, name: "Life_Time", description: "Life Time fitness", type: "file", parentId: 522 },
            
            // Work Structure
            { id: 601, name: "Work_Timeline", description: "Chronological work history and career progression", type: "folder", parentId: 600 },
            { id: 602, name: "Employers", description: "All employers and organizations worked with", type: "folder", parentId: 600 },
            
            // R-Cubed
            { id: 603, name: "R-Cubed", description: "R-Cubed employment and projects", type: "folder", parentId: 602 },
            
            // R-Cubed Subfolders
            { id: 6031, name: "Pay_Stubs_Benefits", description: "Pay stubs, benefits, and employment documents", type: "folder", parentId: 603 },
            { id: 6032, name: "Business_Documents", description: "Company documents, branding, and official records", type: "folder", parentId: 603 },
            { id: 6033, name: "Cleverly_Dashboard_Data", description: "Cleverly dashboard exports and analytics", type: "folder", parentId: 603 },
            { id: 6034, name: "LinkedIn_Social_Media", description: "LinkedIn analytics and social media data", type: "folder", parentId: 603 },
            { id: 6035, name: "Meeting_Calendar_Data", description: "Meeting schedules, calendar exports, and Jim's calendar", type: "folder", parentId: 603 },
            { id: 6036, name: "Microsoft_Teams_OneDrive", description: "Teams chats and OneDrive media files", type: "folder", parentId: 603 },
            { id: 6037, name: "Sales_Pipeline_Data", description: "Sales pipeline, territory lists, and qualification guidelines", type: "folder", parentId: 603 },
            { id: 6038, name: "Business_Development", description: "Business development strategies and planning documents", type: "folder", parentId: 603 },
            { id: 6039, name: "Marketing_GTM", description: "Marketing materials, GTM assets, and Oracle overviews", type: "folder", parentId: 603 },
            { id: 6040, name: "Partner_Contact_Data", description: "Partner contacts, collaboration accounts, and client success", type: "folder", parentId: 603 },
            { id: 6041, name: "Lead_Generation_Data", description: "Lead generation, Apollo data, and suggested contacts", type: "folder", parentId: 603 },
            { id: 6042, name: "Website_Planning", description: "Website requirements, search history, and Zoom recordings", type: "folder", parentId: 603 },
            
            // Red River Development
            { id: 604, name: "Red_River_Development", description: "Red River Development employment", type: "folder", parentId: 602 },
            
            // Trulo Homes
            { id: 605, name: "Trulo_Homes", description: "Trulo Homes employment across multiple locations", type: "folder", parentId: 602 },
            { id: 606, name: "Trulo_Homes_Bentoville", description: "Trulo Homes - Bentoville location", type: "folder", parentId: 605 },
            { id: 607, name: "Trulo_Homes_Jenks", description: "Trulo Homes - Jenks location", type: "folder", parentId: 605 },
            { id: 608, name: "Trulo_Homes_Whitestone", description: "Trulo Homes - Whitestone location", type: "folder", parentId: 605 },
            { id: 609, name: "Trulo_Homes_Kansas_City", description: "Trulo Homes - Kansas City location", type: "folder", parentId: 605 },
            
            // Rose Rock Development
            { id: 610, name: "Rose_Rock_Development", description: "Rose Rock Development employment", type: "folder", parentId: 602 },
            { id: 611, name: "Reunion", description: "Reunion project", type: "folder", parentId: 610 },
            { id: 612, name: "Palace", description: "Palace project", type: "folder", parentId: 610 },
            { id: 613, name: "Adams", description: "Adams project", type: "folder", parentId: 610 },
            { id: 614, name: "Vandever", description: "Vandever project", type: "folder", parentId: 610 },
            
            // Other Employers
            { id: 615, name: "Minaret_Foundation", description: "Minaret Foundation employment", type: "folder", parentId: 602 },
            { id: 616, name: "Ashford_Communities", description: "Ashford Communities employment", type: "folder", parentId: 602 },
            { id: 617, name: "US_Census_Bureau", description: "US Census Bureau employment", type: "folder", parentId: 602 },
            { id: 618, name: "Gulf_Coast_Regional_Blood_Center", description: "Gulf Coast Regional Blood Center employment", type: "folder", parentId: 602 },
            { id: 619, name: "ISGH", description: "Islamic Society of Greater Houston employment", type: "folder", parentId: 602 },
            { id: 620, name: "Maryam_Islamic_Center", description: "Maryam Islamic Center employment", type: "folder", parentId: 619 },
            
            // Work Projects and Tools
            { id: 621, name: "Work_Projects", description: "Professional projects and deliverables", type: "folder", parentId: 600 },
            { id: 622, name: "Tools", description: "Work-related tools and software", type: "folder", parentId: 600 },
            { id: 623, name: "Work_Portfolio", description: "Professional portfolio and achievements", type: "folder", parentId: 600 },
            
            // Projects Structure
            { id: 701, name: "SFA", description: "SFA project documentation and resources", type: "folder", parentId: 700 },
            { id: 702, name: "SpaceApps", description: "NASA Space Apps Challenge projects", type: "folder", parentId: 700 },
            { id: 703, name: "NASA_JSC", description: "NASA Johnson Space Center projects", type: "folder", parentId: 700 },
            { id: 704, name: "Hackathons", description: "Hackathon projects and competitions", type: "folder", parentId: 700 },
            { id: 705, name: "Xain_Dev", description: "Xain development projects and personal coding", type: "folder", parentId: 700 },
            
            // Important_Documents
            { id: 2, name: "Important_Documents", description: "Core records and IDs", type: "folder", parentId: 1 },
            { id: 3, name: "Identity_Records", description: "Official identification documents", type: "folder", parentId: 2 },
            { id: 4, name: "Passport", description: "", type: "file", parentId: 3 },
            { id: 5, name: "Drivers_License", description: "", type: "file", parentId: 3 },
            { id: 6, name: "Social_Security_Card", description: "", type: "file", parentId: 3 },
            { id: 7, name: "Birth_Certificate", description: "", type: "file", parentId: 3 },
            { id: 8, name: "Voter_Registration", description: "", type: "file", parentId: 3 },
            
            { id: 9, name: "Medical_Records", description: "Health summaries and insurance info", type: "folder", parentId: 2 },
            { id: 10, name: "Immunization_Records", description: "", type: "file", parentId: 9 },
            { id: 11, name: "Health_Insurance_Cards", description: "", type: "file", parentId: 9 },
            { id: 12, name: "Primary_Care_Notes", description: "", type: "file", parentId: 9 },
            
            { id: 13, name: "Legal_Documents", description: "Contracts, agreements, authorizations", type: "folder", parentId: 2 },
            { id: 14, name: "Lease_Agreements", description: "", type: "file", parentId: 13 },
            { id: 15, name: "Power_of_Attorney", description: "", type: "file", parentId: 13 },
            { id: 16, name: "Wills_Trusts", description: "", type: "file", parentId: 13 },
            { id: 17, name: "NDAs_Employment_Contracts", description: "", type: "file", parentId: 13 },
            
            { id: 18, name: "Tax_Records", description: "Annual filings and statements", type: "folder", parentId: 2 },
            { id: 19, name: "W2_Forms", description: "", type: "file", parentId: 18 },
            { id: 20, name: "1099_Forms", description: "", type: "file", parentId: 18 },
            { id: 21, name: "IRS_Returns", description: "", type: "file", parentId: 18 },
            
            { id: 22, name: "Insurance", description: "Coverage documents", type: "folder", parentId: 2 },
            { id: 23, name: "Auto_Insurance", description: "", type: "file", parentId: 22 },
            { id: 24, name: "Health_Insurance", description: "", type: "file", parentId: 22 },
            { id: 25, name: "Life_Insurance", description: "", type: "file", parentId: 22 },
            { id: 26, name: "Renters_or_Homeowners", description: "", type: "file", parentId: 22 },
            
            // Contacts_Network
            { id: 27, name: "Contacts_Network", description: "Personal and professional connections", type: "folder", parentId: 1 },
            
            // Family subfolders
            { id: 28, name: "Family", description: "Family member profiles", type: "folder", parentId: 27 },
            { id: 29, name: "Immediate", description: "Immediate family members", type: "folder", parentId: 28 },
            { id: 30, name: "Extended", description: "Extended family members", type: "folder", parentId: 28 },
            
            // Immediate family profiles
            { id: 31, name: "Mom", description: "Mother's profile", type: "file", parentId: 29 },
            { id: 32, name: "Mom_Notes", description: "Notes about Mom", type: "file", parentId: 31 },
            { id: 33, name: "Mom_Photos", description: "Photos of Mom", type: "file", parentId: 31 },
            
            { id: 34, name: "Dad", description: "Father's profile", type: "file", parentId: 29 },
            { id: 35, name: "Dad_Notes", description: "Notes about Dad", type: "file", parentId: 34 },
            { id: 36, name: "Dad_Photos", description: "Photos of Dad", type: "file", parentId: 34 },
            
            { id: 37, name: "Stepmom", description: "Stepmother's profile", type: "file", parentId: 29 },
            { id: 38, name: "Stepmom_Notes", description: "Notes about Stepmom", type: "file", parentId: 37 },
            { id: 39, name: "Stepmom_Photos", description: "Photos of Stepmom", type: "file", parentId: 37 },
            
            { id: 40, name: "Sister", description: "Sister's profile", type: "file", parentId: 29 },
            { id: 41, name: "Sister_Notes", description: "Notes about Sister", type: "file", parentId: 40 },
            { id: 42, name: "Sister_Photos", description: "Photos of Sister", type: "file", parentId: 40 },
            
            { id: 43, name: "Brother", description: "Brother's profile", type: "file", parentId: 29 },
            { id: 44, name: "Brother_Notes", description: "Notes about Brother", type: "file", parentId: 43 },
            { id: 45, name: "Brother_Photos", description: "Photos of Brother", type: "file", parentId: 43 },
            
            { id: 46, name: "Sister_2", description: "Second sister's profile", type: "file", parentId: 29 },
            { id: 47, name: "Sister_2_Notes", description: "Notes about Sister 2", type: "file", parentId: 46 },
            { id: 48, name: "Sister_2_Photos", description: "Photos of Sister 2", type: "file", parentId: 46 },
            
            // Extended family profiles
            { id: 49, name: "Sister_in_Law", description: "Sister-in-law's profile", type: "file", parentId: 30 },
            { id: 50, name: "Sister_in_Law_Notes", description: "Notes about Sister-in-law", type: "file", parentId: 49 },
            { id: 51, name: "Sister_in_Law_Photos", description: "Photos of Sister-in-law", type: "file", parentId: 49 },
            
            { id: 52, name: "Brother_in_Law", description: "Brother-in-law's profile", type: "file", parentId: 30 },
            { id: 53, name: "Brother_in_Law_Notes", description: "Notes about Brother-in-law", type: "file", parentId: 52 },
            { id: 54, name: "Brother_in_Law_Photos", description: "Photos of Brother-in-law", type: "file", parentId: 52 },
            
            { id: 55, name: "Nephew", description: "Nephew's profile (Brother + Sister-in-law's child)", type: "file", parentId: 30 },
            { id: 56, name: "Nephew_Notes", description: "Notes about Nephew", type: "file", parentId: 55 },
            { id: 57, name: "Nephew_Photos", description: "Photos of Nephew", type: "file", parentId: 55 },
            
            { id: 58, name: "Niece_1", description: "First niece's profile", type: "file", parentId: 30 },
            { id: 59, name: "Niece_1_Notes", description: "Notes about Niece 1", type: "file", parentId: 58 },
            { id: 60, name: "Niece_1_Photos", description: "Photos of Niece 1", type: "file", parentId: 58 },
            
            { id: 61, name: "Niece_2", description: "Second niece's profile", type: "file", parentId: 30 },
            { id: 62, name: "Niece_2_Notes", description: "Notes about Niece 2", type: "file", parentId: 61 },
            { id: 63, name: "Niece_2_Photos", description: "Photos of Niece 2", type: "file", parentId: 61 },
            
            { id: 64, name: "Nephew_2", description: "Second nephew's profile (Sister + Brother-in-law's children)", type: "file", parentId: 30 },
            { id: 65, name: "Nephew_2_Notes", description: "Notes about Nephew 2", type: "file", parentId: 64 },
            { id: 66, name: "Nephew_2_Photos", description: "Photos of Nephew 2", type: "file", parentId: 64 },
            
            // Attributes moved under Family
            { id: 67, name: "Attributes", description: "Relationship metadata", type: "folder", parentId: 28 },
            { id: 68, name: "Connection_Type", description: "", type: "file", parentId: 67 },
            { id: 69, name: "Residence_Status", description: "", type: "file", parentId: 67 },
            { id: 70, name: "Contact_Frequency", description: "", type: "file", parentId: 67 },
            { id: 71, name: "Support_Role", description: "", type: "file", parentId: 67 },
            { id: 72, name: "Shared_Responsibilities", description: "", type: "file", parentId: 67 },
            
            // Groups moved under Family
            { id: 73, name: "Groups", description: "Relationship clusters auto-generated by assistant", type: "folder", parentId: 28 },
            { id: 74, name: "Parents (Mom, Dad, Stepmom)", description: "", type: "file", parentId: 73 },
            { id: 75, name: "Siblings (Sister, Brother, Sister_2)", description: "", type: "file", parentId: 73 },
            { id: 76, name: "In_Laws (Sister_in_Law, Brother_in_Law)", description: "", type: "file", parentId: 73 },
            { id: 77, name: "Kids (All nieces and nephews)", description: "", type: "file", parentId: 73 },
            { id: 78, name: "Extended (Uncles, aunts, cousins – optional future expansion)", description: "", type: "file", parentId: 73 },
            
            // Friends
            { id: 79, name: "Friends", description: "Personal friendships and social connections", type: "folder", parentId: 27 },
            { id: 80, name: "Childhood", description: "Friends from childhood", type: "folder", parentId: 79 },
            { id: 81, name: "High_School", description: "High school friends", type: "folder", parentId: 79 },
            { id: 82, name: "College", description: "College friends", type: "folder", parentId: 79 },
            { id: 83, name: "Events", description: "Friends from events (SpaceApps, NASA, etc.)", type: "folder", parentId: 79 },
            { id: 84, name: "Religious_Community", description: "Muslim Network and religious community", type: "folder", parentId: 79 },
            { id: 85, name: "Current_Acquaintances", description: "Current social acquaintances", type: "folder", parentId: 79 },
            
            // Professional Network
            { id: 86, name: "Professional_Network", description: "Professional connections and colleagues", type: "folder", parentId: 27 },
            { id: 87, name: "Mentors", description: "Professional mentors and advisors", type: "folder", parentId: 86 },
            { id: 88, name: "Collaborators", description: "Professional collaborators and partners", type: "folder", parentId: 86 },
            { id: 89, name: "Clients", description: "Professional clients and business contacts", type: "folder", parentId: 86 },
            
            // Applications
            { id: 90, name: "Applications", description: "Mobile and desktop applications", type: "folder", parentId: 1 },
            
            // Social & Community
            { id: 91, name: "Social_Community", description: "Social media and community apps", type: "folder", parentId: 90 },
            { id: 92, name: "Direct_Messaging", description: "Direct messaging applications", type: "folder", parentId: 91 },
            { id: 93, name: "iMessage", description: "Apple iMessage", type: "file", parentId: 92 },
            { id: 94, name: "FaceTime", description: "Apple FaceTime", type: "file", parentId: 92 },
            { id: 95, name: "TextMe", description: "TextMe messaging app", type: "file", parentId: 92 },
            { id: 96, name: "TextFree", description: "TextFree messaging app", type: "file", parentId: 92 },
            { id: 97, name: "WhatsApp", description: "WhatsApp messaging", type: "file", parentId: 92 },
            { id: 98, name: "Facebook_Messenger", description: "Facebook Messenger", type: "file", parentId: 92 },
            { id: 99, name: "Discord", description: "Discord chat platform", type: "file", parentId: 92 },
            { id: 100, name: "Slack", description: "Slack workspace communication", type: "file", parentId: 92 },
            
            { id: 101, name: "Communities_Groups", description: "Community and group platforms", type: "folder", parentId: 91 },
            { id: 102, name: "Skool", description: "Skool community platform", type: "file", parentId: 101 },
            { id: 103, name: "Mighty", description: "Mighty community platform", type: "file", parentId: 101 },
            { id: 104, name: "Reddit", description: "Reddit social platform", type: "file", parentId: 101 },
            { id: 105, name: "Meetup", description: "Meetup event platform", type: "file", parentId: 101 },
            { id: 106, name: "Eventbrite", description: "Eventbrite event platform", type: "file", parentId: 101 },
            { id: 107, name: "LinkedIn_Events", description: "LinkedIn Events", type: "file", parentId: 101 },
            { id: 108, name: "Meta_Events", description: "Meta Events", type: "file", parentId: 101 },
            { id: 109, name: "Faves", description: "Faves community app", type: "file", parentId: 101 },
            
            { id: 110, name: "Social_Media", description: "Social media platforms", type: "folder", parentId: 91 },
            { id: 111, name: "Instagram", description: "Instagram social platform", type: "file", parentId: 110 },
            { id: 112, name: "TikTok", description: "TikTok video platform", type: "file", parentId: 110 },
            { id: 113, name: "Snapchat", description: "Snapchat messaging", type: "file", parentId: 110 },
            { id: 114, name: "Facebook", description: "Facebook social platform", type: "file", parentId: 110 },
            { id: 115, name: "YouTube", description: "YouTube video platform", type: "file", parentId: 110 },
            { id: 116, name: "Threads", description: "Threads social platform", type: "file", parentId: 110 },
            
            // Productivity & Organization
            { id: 117, name: "Productivity_Organization", description: "Productivity and organization apps", type: "folder", parentId: 90 },
            { id: 118, name: "Planning_Notes", description: "Planning and note-taking apps", type: "folder", parentId: 117 },
            { id: 119, name: "Notion", description: "Notion workspace", type: "file", parentId: 118 },
            { id: 120, name: "Obsidian", description: "Obsidian note-taking", type: "file", parentId: 118 },
            { id: 121, name: "Apple_Notes", description: "Apple Notes app", type: "file", parentId: 118 },
            { id: 122, name: "Google_Tasks", description: "Google Tasks", type: "file", parentId: 118 },
            { id: 123, name: "Reminders", description: "Apple Reminders", type: "file", parentId: 118 },
            { id: 124, name: "Calendar", description: "Calendar applications", type: "file", parentId: 118 },
            
            { id: 125, name: "Project_Management", description: "Project management and collaboration", type: "folder", parentId: 117 },
            { id: 126, name: "Asana", description: "Asana project management", type: "file", parentId: 125 },
            { id: 127, name: "Miro", description: "Miro collaboration platform", type: "file", parentId: 125 },
            { id: 128, name: "GitHub", description: "GitHub development platform", type: "file", parentId: 125 },
            { id: 129, name: "Google_Cloud", description: "Google Cloud platform", type: "file", parentId: 125 },
            
            { id: 130, name: "Automation_Tools", description: "Automation and productivity tools", type: "folder", parentId: 117 },
            { id: 131, name: "IFTTT", description: "IFTTT automation", type: "file", parentId: 130 },
            { id: 132, name: "Shortcuts", description: "Apple Shortcuts", type: "file", parentId: 130 },
            { id: 133, name: "Scriptable", description: "Scriptable automation", type: "file", parentId: 130 },
            { id: 134, name: "Pythonista", description: "Pythonista Python IDE", type: "file", parentId: 130 },
            { id: 135, name: "Fireflies", description: "Fireflies AI meeting assistant", type: "file", parentId: 130 },
            
            // Finance & Payments
            { id: 136, name: "Finance_Payments", description: "Finance and payment apps", type: "folder", parentId: 90 },
            { id: 137, name: "Cash_App", description: "Cash App payments", type: "file", parentId: 136 },
            { id: 138, name: "Venmo", description: "Venmo payments", type: "file", parentId: 136 },
            { id: 139, name: "PayPal", description: "PayPal payments", type: "file", parentId: 136 },
            { id: 140, name: "Rocket_Money", description: "Rocket Money finance", type: "file", parentId: 136 },
            { id: 141, name: "Acorns", description: "Acorns investment", type: "file", parentId: 136 },
            { id: 142, name: "Wells_Fargo", description: "Wells Fargo banking", type: "file", parentId: 136 },
            { id: 143, name: "Bank_of_America", description: "Bank of America banking", type: "file", parentId: 136 },
            { id: 144, name: "Western_Union", description: "Western Union transfers", type: "file", parentId: 136 },
            { id: 145, name: "Zelle", description: "Zelle payments", type: "file", parentId: 136 },
            { id: 146, name: "Plaid", description: "Plaid financial data", type: "file", parentId: 136 },
            { id: 147, name: "SquareUp", description: "Square payment processing", type: "file", parentId: 136 },
            
            // Shopping & Rewards
            { id: 148, name: "Shopping_Rewards", description: "Shopping and rewards apps", type: "folder", parentId: 90 },
            { id: 149, name: "Retail", description: "Retail shopping apps", type: "folder", parentId: 148 },
            { id: 150, name: "Amazon", description: "Amazon shopping", type: "file", parentId: 149 },
            { id: 151, name: "Walmart", description: "Walmart shopping", type: "file", parentId: 149 },
            { id: 152, name: "Target", description: "Target shopping", type: "file", parentId: 149 },
            { id: 153, name: "Lowes", description: "Lowe's home improvement", type: "file", parentId: 149 },
            { id: 154, name: "Home_Depot", description: "Home Depot", type: "file", parentId: 149 },
            { id: 155, name: "Office_Depot", description: "Office Depot", type: "file", parentId: 149 },
            { id: 156, name: "eBay", description: "eBay marketplace", type: "file", parentId: 149 },
            { id: 157, name: "Temu", description: "Temu shopping", type: "file", parentId: 149 },
            { id: 158, name: "Etsy", description: "Etsy marketplace", type: "file", parentId: 149 },
            
            { id: 159, name: "Food_Coffee", description: "Food and coffee apps", type: "folder", parentId: 148 },
            { id: 160, name: "Chick_fil_A", description: "Chick-fil-A app", type: "file", parentId: 159 },
            { id: 161, name: "Dutch_Bros", description: "Dutch Bros coffee", type: "file", parentId: 159 },
            { id: 162, name: "Starbucks", description: "Starbucks coffee", type: "file", parentId: 159 },
            { id: 163, name: "DoorDash", description: "DoorDash food delivery", type: "file", parentId: 159 },
            { id: 164, name: "Uber_Eats", description: "Uber Eats delivery", type: "file", parentId: 159 },
            
            { id: 165, name: "Shipping_Tracking", description: "Shipping and tracking apps", type: "folder", parentId: 148 },
            { id: 166, name: "UPS", description: "UPS shipping", type: "file", parentId: 165 },
            { id: 167, name: "FedEx", description: "FedEx shipping", type: "file", parentId: 165 },
            { id: 168, name: "USPS_Mobile", description: "USPS Mobile", type: "file", parentId: 165 },
            
            // Navigation & Travel
            { id: 169, name: "Navigation_Travel", description: "Navigation and travel apps", type: "folder", parentId: 90 },
            { id: 170, name: "Maps_Transport", description: "Maps and transportation", type: "folder", parentId: 169 },
            { id: 171, name: "Google_Maps", description: "Google Maps", type: "file", parentId: 170 },
            { id: 172, name: "Apple_Maps", description: "Apple Maps", type: "file", parentId: 170 },
            { id: 173, name: "Yandex_Maps", description: "Yandex Maps", type: "file", parentId: 170 },
            { id: 174, name: "ParkMobile", description: "ParkMobile parking", type: "file", parentId: 170 },
            { id: 175, name: "Uber", description: "Uber rideshare", type: "file", parentId: 170 },
            { id: 176, name: "Lyft", description: "Lyft rideshare", type: "file", parentId: 170 },
            
            { id: 177, name: "Housing_Weather", description: "Housing and weather apps", type: "folder", parentId: 169 },
            { id: 178, name: "Apartments_App", description: "Apartments.com app", type: "file", parentId: 177 },
            { id: 179, name: "Weather", description: "Weather applications", type: "file", parentId: 177 },
            
            // Health & Fitness
            { id: 180, name: "Health_Fitness", description: "Health and fitness apps", type: "folder", parentId: 90 },
            { id: 181, name: "MyChart", description: "MyChart health portal", type: "file", parentId: 180 },
            { id: 182, name: "BetterSleep", description: "BetterSleep app", type: "file", parentId: 180 },
            { id: 183, name: "PT_Solutions", description: "PT Solutions", type: "file", parentId: 180 },
            { id: 184, name: "Noji", description: "Noji health app", type: "file", parentId: 180 },
            { id: 185, name: "Healow", description: "Healow health app", type: "file", parentId: 180 },
            { id: 186, name: "Life_Time", description: "Life Time fitness", type: "file", parentId: 180 },
            { id: 187, name: "Weight_Gurus", description: "Weight Gurus", type: "file", parentId: 180 },
            { id: 188, name: "Go_Kinetic", description: "Go Kinetic fitness", type: "file", parentId: 180 },
            { id: 189, name: "Elevate", description: "Elevate brain training", type: "file", parentId: 180 },
            { id: 190, name: "Think_Dirty", description: "Think Dirty product scanner", type: "file", parentId: 180 },
            
            // Learning & Self-Improvement
            { id: 191, name: "Learning_Self_Improvement", description: "Learning and self-improvement apps", type: "folder", parentId: 90 },
            { id: 192, name: "Duolingo", description: "Duolingo language learning", type: "file", parentId: 191 },
            { id: 193, name: "Mimo", description: "Mimo coding app", type: "file", parentId: 191 },
            { id: 194, name: "Brilliant", description: "Brilliant learning platform", type: "file", parentId: 191 },
            { id: 195, name: "Quizgecko", description: "Quizgecko quiz platform", type: "file", parentId: 191 },
            { id: 196, name: "Information_Reading", description: "Information and reading apps", type: "file", parentId: 191 },
            
            // Entertainment & Media
            { id: 197, name: "Entertainment_Media", description: "Entertainment and media apps", type: "folder", parentId: 90 },
            { id: 198, name: "Streaming", description: "Streaming services", type: "folder", parentId: 197 },
            { id: 199, name: "Netflix", description: "Netflix streaming", type: "file", parentId: 198 },
            { id: 200, name: "Hulu", description: "Hulu streaming", type: "file", parentId: 198 },
            { id: 201, name: "Max", description: "Max streaming", type: "file", parentId: 198 },
            { id: 202, name: "Prime_Video", description: "Prime Video streaming", type: "file", parentId: 198 },
            { id: 203, name: "Disney_Plus", description: "Disney Plus streaming", type: "file", parentId: 198 },
            { id: 204, name: "Crunchyroll", description: "Crunchyroll anime", type: "file", parentId: 198 },
            { id: 205, name: "YouTube", description: "YouTube streaming", type: "file", parentId: 198 },
            
            { id: 206, name: "Devices_Control", description: "Device control apps", type: "folder", parentId: 197 },
            { id: 207, name: "VIZIO", description: "VIZIO TV control", type: "file", parentId: 206 },
            { id: 208, name: "Apple_TV_Remote", description: "Apple TV Remote", type: "file", parentId: 206 },
            
            // AI & Knowledge Tools
            { id: 209, name: "AI_Knowledge_Tools", description: "AI and knowledge tools", type: "folder", parentId: 90 },
            { id: 210, name: "ChatGPT", description: "ChatGPT AI assistant", type: "file", parentId: 209 },
            { id: 211, name: "Claude", description: "Claude AI assistant", type: "file", parentId: 209 },
            { id: 212, name: "Perplexity", description: "Perplexity AI search", type: "file", parentId: 209 },
            { id: 213, name: "Rewind", description: "Rewind AI recorder", type: "file", parentId: 209 },
            
            // Financial
            { id: 214, name: "Financial", description: "Personal financial management", type: "folder", parentId: 1 },
            { id: 215, name: "Accounts_Banking", description: "Banking and credit card accounts", type: "folder", parentId: 214 },
            
            // Bank of America
            { id: 216, name: "Bank_of_America", description: "Bank of America accounts", type: "folder", parentId: 215 },
            { id: 217, name: "Checking", description: "Bank of America checking account", type: "folder", parentId: 216 },
            { id: 218, name: "Account_Number", description: "Account Number – •••6820", type: "file", parentId: 217 },
            { id: 219, name: "Routing_Numbers", description: "Routing numbers for different transaction types", type: "folder", parentId: 217 },
            { id: 220, name: "Electronic_Transfers", description: "Electronic Transfers – 111000025", type: "file", parentId: 219 },
            { id: 221, name: "Checks", description: "Checks – 113000023", type: "file", parentId: 219 },
            { id: 222, name: "Wire_Transfers", description: "Wire Transfers – 026009593", type: "file", parentId: 219 },
            { id: 223, name: "Status", description: "Status – Active", type: "file", parentId: 217 },
            { id: 224, name: "Credit_Cards", description: "Bank of America credit cards", type: "folder", parentId: 216 },
            { id: 225, name: "Visa_2328", description: "Visa •••2328", type: "file", parentId: 224 },
            { id: 226, name: "Limit", description: "Limit – [placeholder]", type: "file", parentId: 224 },
            { id: 227, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 224 },
            { id: 228, name: "Payment_Due_Date", description: "Payment Due Date – [placeholder]", type: "file", parentId: 224 },
            { id: 229, name: "Notes", description: "Bank of America notes and info", type: "folder", parentId: 216 },
            { id: 230, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 229 },
            { id: 231, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 229 },
            
            // Credit One Bank
            { id: 232, name: "Credit_One_Bank", description: "Credit One Bank accounts", type: "folder", parentId: 215 },
            { id: 233, name: "Credit_Cards", description: "Credit One credit cards", type: "folder", parentId: 232 },
            { id: 234, name: "Amex_2913", description: "Amex •••2913", type: "file", parentId: 233 },
            { id: 235, name: "Amex_9974", description: "Amex •••9974", type: "file", parentId: 233 },
            { id: 236, name: "Limit", description: "Limit – [placeholder]", type: "file", parentId: 233 },
            { id: 237, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 233 },
            { id: 238, name: "Payment_Due_Date", description: "Payment Due Date – [placeholder]", type: "file", parentId: 233 },
            { id: 239, name: "Notes", description: "Credit One Bank notes", type: "folder", parentId: 232 },
            { id: 240, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 239 },
            { id: 241, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 239 },
            
            // Wells Fargo
            { id: 242, name: "Wells_Fargo", description: "Wells Fargo accounts", type: "folder", parentId: 215 },
            { id: 243, name: "Credit_Cards", description: "Wells Fargo credit cards", type: "folder", parentId: 242 },
            { id: 244, name: "Home_Furnishings_8058", description: "Home Furnishings •••8058", type: "file", parentId: 243 },
            { id: 245, name: "Limit", description: "Limit – [placeholder]", type: "file", parentId: 243 },
            { id: 246, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 243 },
            { id: 247, name: "Payment_Due_Date", description: "Payment Due Date – [placeholder]", type: "file", parentId: 243 },
            { id: 248, name: "Notes", description: "Wells Fargo notes", type: "folder", parentId: 242 },
            { id: 249, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 248 },
            { id: 250, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 248 },
            
            // Indigo Platinum
            { id: 251, name: "Indigo_Platinum", description: "Indigo Platinum accounts", type: "folder", parentId: 215 },
            { id: 252, name: "Credit_Cards", description: "Indigo Platinum credit cards", type: "folder", parentId: 251 },
            { id: 253, name: "Indigo_Platinum_Card_6612", description: "Indigo Platinum Card •••6612", type: "file", parentId: 252 },
            { id: 254, name: "Limit", description: "Limit – [placeholder]", type: "file", parentId: 252 },
            { id: 255, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 252 },
            { id: 256, name: "Payment_Due_Date", description: "Payment Due Date – [placeholder]", type: "file", parentId: 252 },
            { id: 257, name: "Notes", description: "Indigo Platinum notes", type: "folder", parentId: 251 },
            { id: 258, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 257 },
            { id: 259, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 257 },
            
            // Robinhood
            { id: 260, name: "Robinhood", description: "Robinhood accounts", type: "folder", parentId: 215 },
            { id: 261, name: "Checking", description: "Robinhood checking account", type: "folder", parentId: 260 },
            { id: 262, name: "Account_1070", description: "Account •••1070", type: "file", parentId: 261 },
            { id: 263, name: "Routing_Number", description: "Routing Number – [placeholder]", type: "file", parentId: 261 },
            { id: 264, name: "Status", description: "Status – [placeholder]", type: "file", parentId: 261 },
            { id: 265, name: "Brokerage", description: "Robinhood brokerage account", type: "folder", parentId: 260 },
            { id: 266, name: "Investment_Account_1802", description: "Investment Account •••1802", type: "file", parentId: 265 },
            { id: 267, name: "Portfolio_Value", description: "Portfolio Value – [placeholder]", type: "file", parentId: 265 },
            { id: 268, name: "Holdings", description: "Holdings – [placeholder]", type: "file", parentId: 265 },
            { id: 269, name: "Connected_Bank", description: "Connected Bank – [placeholder]", type: "file", parentId: 265 },
            { id: 270, name: "Notes", description: "Robinhood notes", type: "folder", parentId: 260 },
            { id: 271, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 270 },
            { id: 272, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 270 },
            
            // Acorns
            { id: 273, name: "Acorns", description: "Acorns investment accounts", type: "folder", parentId: 215 },
            { id: 274, name: "Investment", description: "Acorns investment account", type: "folder", parentId: 273 },
            { id: 275, name: "Account_Type", description: "Account Type – [placeholder]", type: "file", parentId: 274 },
            { id: 276, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 274 },
            { id: 277, name: "Goal", description: "Goal – [placeholder]", type: "file", parentId: 274 },
            { id: 278, name: "Recurring_Amount", description: "Recurring Amount – [placeholder]", type: "file", parentId: 274 },
            { id: 279, name: "Notes", description: "Acorns notes", type: "folder", parentId: 273 },
            { id: 280, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 279 },
            { id: 281, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 279 },
            
            // Apple Credit
            { id: 282, name: "Apple_Credit", description: "Apple Credit accounts", type: "folder", parentId: 215 },
            { id: 283, name: "Credit_Cards", description: "Apple credit cards", type: "folder", parentId: 282 },
            { id: 284, name: "Apple_Card", description: "Apple Card – Linked to Apple Account", type: "file", parentId: 283 },
            { id: 285, name: "Limit", description: "Limit – [placeholder]", type: "file", parentId: 283 },
            { id: 286, name: "Balance", description: "Balance – [placeholder]", type: "file", parentId: 283 },
            { id: 287, name: "Payment_Due_Date", description: "Payment Due Date – [placeholder]", type: "file", parentId: 283 },
            { id: 288, name: "Notes", description: "Apple Credit notes", type: "folder", parentId: 282 },
            { id: 289, name: "Login_Info", description: "Login Info – [placeholder]", type: "file", parentId: 288 },
            { id: 290, name: "Last_Statement", description: "Last Statement – [placeholder]", type: "file", parentId: 288 },
            
            // Chase
            { id: 291, name: "Chase", description: "Chase account", type: "folder", parentId: 215 },
            { id: 292, name: "Credentials", description: "Chase credentials", type: "file", parentId: 291 },
            
            // American Express
            { id: 293, name: "American_Express", description: "American Express account", type: "folder", parentId: 215 },
            { id: 294, name: "Credentials", description: "American Express credentials", type: "file", parentId: 293 },
            
            // Other Cards
            { id: 295, name: "Other_Cards", description: "Additional credit cards", type: "folder", parentId: 215 },
            { id: 296, name: "Nordstrom", description: "Nordstrom card", type: "folder", parentId: 295 },
            { id: 297, name: "Account_Info", description: "Nordstrom account information", type: "file", parentId: 296 },
            { id: 298, name: "Synchrony", description: "Synchrony card", type: "folder", parentId: 295 },
            { id: 299, name: "Account_Info", description: "Synchrony account information", type: "file", parentId: 298 },
            
            // Bills Payments
            { id: 300, name: "Bills_Payments", description: "Monthly bills and payments", type: "folder", parentId: 214 },
            { id: 301, name: "Rent_HOA", description: "Rent and HOA payments", type: "folder", parentId: 300 },
            { id: 302, name: "Payment_Records", description: "Rent and HOA payment records", type: "file", parentId: 301 },
            { id: 303, name: "Car_HondaFS", description: "Honda Financial Services", type: "folder", parentId: 300 },
            { id: 304, name: "Credentials", description: "Honda FS credentials", type: "file", parentId: 303 },
            
            // Utilities
            { id: 305, name: "Utilities", description: "Utility accounts", type: "folder", parentId: 300 },
            { id: 306, name: "Water_Minol", description: "Minol water service", type: "folder", parentId: 305 },
            { id: 307, name: "Credentials", description: "Minol water credentials", type: "file", parentId: 306 },
            { id: 308, name: "Electric_PSO", description: "PSO electric service", type: "folder", parentId: 305 },
            { id: 309, name: "Account_Info", description: "PSO electric account information", type: "file", parentId: 308 },
            { id: 310, name: "Gas_ONG", description: "ONG gas service", type: "folder", parentId: 305 },
            { id: 311, name: "Account_Info", description: "ONG gas account information", type: "file", parentId: 310 },
            { id: 312, name: "Phone_ATT", description: "AT&T phone service", type: "folder", parentId: 300 },
            { id: 313, name: "Credentials", description: "AT&T credentials", type: "file", parentId: 312 },
            { id: 314, name: "Insurance_Allstate", description: "Allstate insurance", type: "folder", parentId: 300 },
            { id: 315, name: "Credentials", description: "Allstate credentials", type: "file", parentId: 314 },
            
            // Credit Debt
            { id: 316, name: "Credit_Debt", description: "Credit reports and debt management", type: "folder", parentId: 214 },
            { id: 317, name: "Reports", description: "Credit reports", type: "folder", parentId: 316 },
            { id: 318, name: "Experian", description: "Experian credit report", type: "file", parentId: 317 },
            { id: 319, name: "CreditKarma", description: "CreditKarma report", type: "file", parentId: 317 },
            { id: 320, name: "Loans", description: "Active loans", type: "folder", parentId: 316 },
            { id: 321, name: "HondaFS", description: "Honda Financial Services loan", type: "file", parentId: 320 },
            { id: 322, name: "Citizens_Apple", description: "Citizens Apple loan", type: "file", parentId: 320 },
            { id: 323, name: "Federal_Student_Aid", description: "Federal student aid", type: "file", parentId: 320 },
            { id: 324, name: "Credit_Repair", description: "Credit repair services", type: "folder", parentId: 316 },
            { id: 325, name: "Lexington_Law", description: "Lexington Law credit repair", type: "file", parentId: 324 },
            
            // Refunds Service Logs
            { id: 326, name: "Refunds_Service_Logs", description: "Refund and service request logs", type: "folder", parentId: 214 },
            { id: 327, name: "Walmart", description: "Walmart refunds and services", type: "file", parentId: 326 },
            { id: 328, name: "Target", description: "Target refunds and services", type: "file", parentId: 326 },
            { id: 329, name: "ATT", description: "AT&T refunds and services", type: "file", parentId: 326 },
            { id: 330, name: "Apple", description: "Apple refunds and services", type: "file", parentId: 326 },
            { id: 331, name: "Nike_Ross_HandAndStone", description: "Nike, Ross, Hand and Stone refunds", type: "file", parentId: 326 },
            
            // Financial Tools
            { id: 332, name: "Financial_Tools", description: "Financial management tools", type: "folder", parentId: 214 },
            { id: 333, name: "RocketMoney", description: "Rocket Money app", type: "file", parentId: 332 },
            { id: 334, name: "Plaid", description: "Plaid financial data", type: "file", parentId: 332 },
            { id: 335, name: "Zelle", description: "Zelle payment app", type: "file", parentId: 332 },
            { id: 336, name: "PayPal", description: "PayPal account", type: "file", parentId: 332 },
            { id: 337, name: "Venmo", description: "Venmo payment app", type: "file", parentId: 332 },
            { id: 338, name: "CashApp", description: "Cash App", type: "file", parentId: 332 },
            { id: 339, name: "SquareUp", description: "Square payment processing", type: "file", parentId: 332 },
            
            // Assets Inventory
            { id: 190, name: "Assets_Inventory", description: "Personal assets and inventory", type: "folder", parentId: 1 },
            { id: 191, name: "Electronics", description: "Electronic devices and accessories", type: "folder", parentId: 190 },
            { id: 192, name: "MacBook", description: "MacBook computer", type: "file", parentId: 191 },
            { id: 193, name: "iPhone15", description: "iPhone 15", type: "file", parentId: 191 },
            { id: 194, name: "Apple_Watch", description: "Apple Watch", type: "file", parentId: 191 },
            { id: 195, name: "LG_34_Monitor", description: "LG 34-inch monitor", type: "file", parentId: 191 },
            { id: 196, name: "ZMUIPNG_Hub", description: "ZMUIPNG hub", type: "file", parentId: 191 },
            { id: 197, name: "Tile", description: "Tile tracking device", type: "file", parentId: 191 },
            { id: 198, name: "iXpand", description: "iXpand device", type: "file", parentId: 191 },
            
            { id: 199, name: "Home_Storage", description: "Home storage and furniture", type: "folder", parentId: 190 },
            { id: 200, name: "Furniture", description: "Home furniture", type: "file", parentId: 199 },
            { id: 201, name: "Decor", description: "Home decorations", type: "file", parentId: 199 },
            { id: 202, name: "Event_Decor", description: "Event decorations", type: "file", parentId: 199 },
            { id: 203, name: "Tools", description: "Home tools", type: "file", parentId: 199 },
            { id: 204, name: "Christmas_Items", description: "Christmas decorations and items", type: "file", parentId: 199 },
            
            { id: 205, name: "Sell_List", description: "Items to sell", type: "folder", parentId: 190 },
            { id: 206, name: "AirPods", description: "AirPods for sale", type: "file", parentId: 205 },
            { id: 207, name: "Dyson_Vacuum", description: "Dyson vacuum for sale", type: "file", parentId: 205 },
            { id: 208, name: "Mirrors", description: "Mirrors for sale", type: "file", parentId: 205 },
            { id: 209, name: "Lights", description: "Lights for sale", type: "file", parentId: 205 },
            { id: 210, name: "Hats", description: "Hats for sale", type: "file", parentId: 205 },
            { id: 211, name: "Shoes", description: "Shoes for sale", type: "file", parentId: 205 },
            
            // Timeline
            { id: 212, name: "Timeline", description: "Life events and timeline", type: "folder", parentId: 1 },
            { id: 213, name: "Event_Summaries", description: "Major life event summaries", type: "folder", parentId: 212 },
            { id: 214, name: "Move_NYC_Baltimore_2018", description: "Move from NYC to Baltimore 2018", type: "file", parentId: 213 },
            { id: 215, name: "Job_BloodCenter_2019", description: "Blood Center job 2019", type: "file", parentId: 213 },
            { id: 216, name: "Eid_2021", description: "Eid celebration 2021", type: "file", parentId: 213 },
            { id: 217, name: "Car_Accident_2023", description: "Car accident 2023", type: "file", parentId: 213 },
            
            { id: 218, name: "Travel", description: "Travel records and accounts", type: "folder", parentId: 212 },
            { id: 219, name: "Emirates", description: "Emirates airline", type: "file", parentId: 218 },
            { id: 220, name: "Delta", description: "Delta airline", type: "file", parentId: 218 },
            { id: 221, name: "United", description: "United airline", type: "file", parentId: 218 },
            { id: 222, name: "Airbnb", description: "Airbnb bookings", type: "file", parentId: 218 },
            
            { id: 223, name: "Incidents", description: "Incident reports", type: "folder", parentId: 212 },
            { id: 224, name: "Car_Accident_Aqsa_2022", description: "Car accident with Aqsa 2022", type: "file", parentId: 223 },
            
            // Daily Life Digital Presence
            { id: 225, name: "Daily_Life_Digital_Presence", description: "Digital accounts and daily life", type: "folder", parentId: 1 },
            { id: 226, name: "Routines_Preferences", description: "Daily routines and preferences", type: "folder", parentId: 225 },
            { id: 227, name: "Notes", description: "Routine and preference notes", type: "file", parentId: 226 },
            
            { id: 228, name: "Email_Accounts", description: "Email account management", type: "folder", parentId: 225 },
            { id: 229, name: "Apple_IDs", description: "Apple ID accounts", type: "folder", parentId: 228 },
            { id: 230, name: "Zainkhan5@yahoo.com", description: "Primary Yahoo email", type: "file", parentId: 229 },
            { id: 231, name: "Other_IDs", description: "Other Apple IDs", type: "file", parentId: 229 },
            { id: 232, name: "Gmail", description: "Gmail account", type: "file", parentId: 228 },
            { id: 233, name: "Outlook", description: "Outlook account", type: "file", parentId: 228 },
            { id: 234, name: "Yahoo", description: "Yahoo email account", type: "file", parentId: 228 },
            
            { id: 235, name: "Social_Media", description: "Social media accounts", type: "folder", parentId: 225 },
            { id: 236, name: "Instagram", description: "Instagram account", type: "folder", parentId: 235 },
            { id: 237, name: "Credentials", description: "Instagram credentials", type: "file", parentId: 236 },
            { id: 239, name: "TikTok", description: "TikTok account", type: "folder", parentId: 235 },
            { id: 240, name: "Credentials", description: "TikTok credentials", type: "file", parentId: 239 },
            { id: 242, name: "Facebook", description: "Facebook account", type: "file", parentId: 235 },
            { id: 243, name: "LinkedIn", description: "LinkedIn account", type: "file", parentId: 235 },
            { id: 244, name: "Snapchat", description: "Snapchat account", type: "file", parentId: 235 },
            
            { id: 245, name: "Shopping", description: "Shopping accounts", type: "folder", parentId: 225 },
            { id: 246, name: "Amazon", description: "Amazon account", type: "file", parentId: 245 },
            { id: 247, name: "Walmart", description: "Walmart account", type: "file", parentId: 245 },
            { id: 248, name: "Target", description: "Target account", type: "file", parentId: 245 },
            { id: 249, name: "BestBuy", description: "Best Buy account", type: "file", parentId: 245 },
            { id: 250, name: "Costco", description: "Costco account", type: "file", parentId: 245 },
            
            { id: 251, name: "Entertainment", description: "Entertainment subscriptions", type: "folder", parentId: 225 },
            { id: 252, name: "AMC", description: "AMC Theaters", type: "file", parentId: 251 },
            { id: 253, name: "Netflix", description: "Netflix subscription", type: "file", parentId: 251 },
            { id: 254, name: "Hulu", description: "Hulu subscription", type: "file", parentId: 251 },
            { id: 255, name: "Crunchyroll", description: "Crunchyroll subscription", type: "file", parentId: 251 },
            { id: 256, name: "Disney+", description: "Disney Plus subscription", type: "file", parentId: 251 },
            { id: 257, name: "HBO_Max", description: "HBO Max subscription", type: "file", parentId: 251 }
        ];
        
        this.nextId = 6500; // Set next ID to continue from where we left off (updated for expanded financial structure)
        
        // Auto-collapse all folders for better initial performance
        this.autoCollapseAll();
        
        this.saveToStorage();
        
        // Use requestAnimationFrame for smoother rendering
        requestAnimationFrame(() => {
            this.render();
            
            // Hide loading indicator after render
            const loadingIndicator = document.getElementById('loadingIndicator');
            const treeView = document.getElementById('treeView');
            
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            if (treeView) {
                treeView.style.opacity = '1';
            }
        });
        }, 0); // Execute after current call stack
    }
    
    autoCollapseAll() {
        // Collapse all folders except root level for better performance
        this.data.forEach(item => {
            if (item.type === 'folder' && item.parentId !== null) {
                this.collapsedFolders.add(item.id);
            }
        });
    }

    showMessage(text, type) {
        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.textContent = text;
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            message.style.background = 'rgba(39, 174, 96, 0.9)';
            message.style.border = '1px solid rgba(39, 174, 96, 0.3)';
        } else if (type === 'error') {
            message.style.background = 'rgba(231, 76, 60, 0.9)';
            message.style.border = '1px solid rgba(231, 76, 60, 0.3)';
        }
        
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application
const blueprint = new SimpleBlueprint();