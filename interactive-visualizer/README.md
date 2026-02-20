# Interactive Mind Map Visualizer

This is a React + D3-based interactive mind map visualizer that provides an advanced visualization of Blueprint data.

## Features

- **Interactive D3 Hierarchy Layout**: Tree-based layout with horizontal orientation
- **Search Functionality**: Search nodes by name or description
- **Toggle Branches**: Click folder nodes to collapse/expand branches
- **Save/Restore View**: Save your current view state and restore it later
- **Zoom & Pan**: SVG-based zoom and pan capabilities
- **Node Selection**: Click nodes to highlight and navigate

## Building

```bash
cd interactive-visualizer
npm install
npm run build
```

The build output will be in `../dist-interactive/` directory.

## Data Source

The visualizer automatically loads data from Blueprint's localStorage (`blueprintData` key), making it seamlessly integrated with the main Blueprint application.

## Usage

Navigate to `dist-interactive/index.html` in your browser, or use the brain icon button in the main Blueprint toolbar to access the interactive visualizer.
