# Blueprint Visualizer

A comprehensive, interactive blueprint management system with a beautiful black aesthetic and glass morphism effects.

## 🌟 Features

- **Interactive Tree Structure** - Collapse/expand folders with smooth animations
- **Three Main Branches**:
  - **Personal** - Life, home, ID, contacts, events, and financial management
  - **Applications** - 100+ mobile and desktop apps organized by category
  - **Health** - Medical records, medications, insurance, and mental health tracking
- **Visual Appeal** - Company logos integrated throughout the interface
- **JSON Export** - Export your entire blueprint structure as JSON
- **Mind Map View** - Visualize your blueprint as an interactive mind map
- **Interactive Mind Map Demo** - Advanced D3.js-powered mind map with zoom, pan, and touch support
- **Add/Edit/Delete** - Full CRUD functionality for all items
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Keyboard Navigation** - Full keyboard accessibility for power users

## 🚀 Getting Started

### Prerequisites
- Python 3.x (for local server)
- Modern web browser

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/zainkhan1994/Blueprint.git
   cd Blueprint
   ```

2. **Start a local server**:
   ```bash
   python3 -m http.server 8000
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

4. **Try the interactive mind map demo**:
   ```
   http://localhost:8000/mindmap-demo.html
   ```

## 📁 Project Structure

```
Blueprint/
├── index.html              # Main HTML structure
├── mindmap-demo.html       # Interactive mind map demo page
├── styles.css              # Black aesthetic with glass effects
├── styles/
│   └── mindmap.css         # Mind map viewer styles
├── script.js               # Complete application logic
├── MindMapViewer.js        # Interactive mind map component
├── data/
│   └── sample-mindmap.json # Sample mind map data
├── README.md               # This file
└── [Logo Directories]      # Organized company logos
```

## 🎨 Design Features

- **Black Aesthetic** - Sleek dark theme with gradient backgrounds
- **Glass Morphism** - Translucent elements with backdrop blur effects
- **Company Logos** - Visual integration of 100+ company logos
- **Smooth Animations** - Collapse/expand with rotating chevrons
- **Color-Coded Icons** - Different colors for different file types

## 📊 Data Structure

### Personal Branch
- Important Documents (Identity, Medical, Legal, Tax, Insurance)
- Contacts Network (Family, Friends, Professional Network)
- Financial Management (Banking, Bills, Tools, Reports)
- Daily Life & Digital Presence
- Assets & Inventory
- Timeline & Travel

### Applications Branch
- Social & Community (Messaging, Communities, Social Media)
- Productivity & Organization (Notes, Project Management, Automation)
- Finance & Payments
- Shopping & Rewards
- Navigation & Travel
- Health & Fitness
- Learning & Self-Improvement
- Entertainment & Media
- AI & Knowledge Tools

### Health Branch
- Medical Records (Doctors, Conditions, Lab Results, Timeline)
- Medications & Supplements
- Insurance & Coverage
- Mental Health (Therapy, Mood Tracking, Reflections)
- Health Apps Integration

## 🛠️ Technical Details

- **Pure JavaScript** - No external dependencies (main app and mind map viewer)
- **Custom Force-Directed Layout** - Interactive graph visualization with pure JavaScript
- **Local Storage** - Data persists in browser
- **SVG Mind Map** - Custom visualization engine with smooth animations
- **Responsive CSS** - Mobile-first design approach
- **Modular Architecture** - Clean, maintainable code structure
- **Zero Build Required** - Works directly in any modern browser

## 📱 Usage

### Main Application
1. **Navigate** - Click folders to expand/collapse
2. **Add Items** - Use the toolbar buttons to add folders or files
3. **Edit Items** - Click the edit button on any item
4. **Delete Items** - Click the delete button (with confirmation)
5. **Export Data** - Use the download button to export as JSON
6. **Mind Map** - Toggle to view your blueprint as a visual mind map

### Interactive Mind Map Demo
1. **Zoom** - Mouse wheel, pinch gestures, or +/- buttons
2. **Pan** - Click and drag, or two-finger swipe on touch devices
3. **Select Node** - Click any node to view details in the side panel
4. **Expand/Collapse** - Double-click nodes with children to collapse/expand subtrees
5. **Keyboard Navigation**:
   - `+` / `-` - Zoom in/out
   - `R` - Reset view
   - `Space` - Toggle collapse on selected node
   - `Enter` - Open details panel
   - `Esc` - Close details panel
   - `Arrow keys` - Navigate between connected nodes

## 🎯 MindMapViewer Component API

The `MindMapViewer` is a reusable, standalone component that can be integrated into any web project.

### Basic Usage

```javascript
// Initialize the viewer
const viewer = new MindMapViewer('container-id', {
    initialZoom: 0.8,
    minZoom: 0.1,
    maxZoom: 4,
    showLabels: true,
    nodeRadius: 20,
    linkDistance: 120,
    enableKeyboard: true,
    enableTouch: true,
    onNodeClick: (node) => {
        console.log('Node clicked:', node);
    }
});

// Load data
viewer.loadData({
    nodes: [
        { id: 'root', label: 'Root', type: 'root', description: '...' },
        { id: 'child1', label: 'Child 1', type: 'branch', description: '...' }
    ],
    edges: [
        { source: 'root', target: 'child1' }
    ]
});
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `initialZoom` | number | 1 | Starting zoom level |
| `minZoom` | number | 0.1 | Minimum zoom level |
| `maxZoom` | number | 4 | Maximum zoom level |
| `showLabels` | boolean | true | Show/hide node labels |
| `nodeRadius` | number | 20 | Base radius for nodes |
| `linkDistance` | number | 100 | Distance between connected nodes |
| `onNodeClick` | function | null | Callback when node is clicked |
| `enableKeyboard` | boolean | true | Enable keyboard navigation |
| `enableTouch` | boolean | true | Enable touch gestures |

### Data Format

Nodes should include:
- `id` (required) - Unique identifier
- `label` (required) - Display name
- `type` - Node type (root, branch, category, item)
- `description` - Detailed description
- `metadata` - Object with `icon` (Font Awesome class) and `color` (hex)

Edges should include:
- `source` (required) - Source node ID
- `target` (required) - Target node ID

### Methods

- `loadData(data)` - Load new graph data
- `zoomIn()` - Zoom in programmatically
- `zoomOut()` - Zoom out programmatically
- `resetView()` - Reset to initial view
- `expandAll()` - Expand all collapsed nodes
- `collapseAll()` - Collapse all expandable nodes
- `focusNode(node)` - Center view on specific node
- `destroy()` - Clean up and remove viewer

### Replacing Sample Data with Your Own

To use your own mind map data instead of the sample:

1. Create a JSON file with your data structure following the format in `data/sample-mindmap.json`
2. Update the `fetch()` call in `mindmap-demo.html` to point to your data file
3. Or dynamically load data using the `loadData()` method:

```javascript
const myData = {
    nodes: [
        { id: 'node1', label: 'My Node', type: 'root', description: '...', metadata: { icon: 'fas fa-star', color: '#ff6b6b' } },
        // ... more nodes
    ],
    edges: [
        { source: 'node1', target: 'node2' },
        // ... more edges
    ]
};

viewer.loadData(myData);
```

You can also convert your existing Blueprint data from `script.js` to this format programmatically.

## 🔧 Customization

The application is highly customizable:
- Modify `script.js` to change data structures
- Update `styles.css` for different visual themes
- Add new logo directories for additional companies
- Extend functionality by modifying the JavaScript classes
- Customize mind map appearance via `styles/mindmap.css`
- Replace sample data in `data/sample-mindmap.json` with your own structure

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**Created with ❤️ for comprehensive life and digital organization**
