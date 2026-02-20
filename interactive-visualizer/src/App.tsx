import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { RawNode, MindMapNode, D3HierarchyNode } from './types';
import Node from './components/Node';
import Edge from './components/Edge';
import { initialData as defaultData } from './constants';

// Load data from Blueprint localStorage
const loadBlueprintData = (): RawNode[] => {
  try {
    const storedData = localStorage.getItem('blueprintData');
    if (storedData) {
      const data = JSON.parse(storedData);
      // Convert Blueprint format to RawNode format
      return data.map((item: any) => ({
        id: item.id,
        name: item.name,
        description: item.description || '',
        type: item.type === 'folder' ? 'folder' : 'file',
        parentId: item.parentId || null
      }));
    }
  } catch (error) {
    console.error('Error loading Blueprint data:', error);
  }
  // Return default data if no data in localStorage
  return defaultData;
};

const initialData = loadBlueprintData();

const App: React.FC = () => {
  const [toggledNodes, setToggledNodes] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<RawNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hasSavedState, setHasSavedState] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);
  const gRef = useRef<SVGGElement>(null);

  useEffect(() => {
    const savedState = localStorage.getItem('mindMapState');
    setHasSavedState(!!savedState);
  }, []);

  const nodesById = useMemo(() => {
    const map = new Map<string, RawNode>();
    initialData.forEach(node => map.set(String(node.id), node));
    return map;
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length > 1) {
      const results = initialData.filter(node =>
        node.name.toLowerCase().includes(query.toLowerCase()) ||
        node.description?.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  };

  const handleSearchResultClick = (nodeId: number) => {
    const getAncestors = (id: number): number[] => {
      const ancestors: number[] = [];
      let current = nodesById.get(String(id));
      while (current && current.parentId !== null && current.parentId !== 0) {
        ancestors.push(current.parentId);
        current = nodesById.get(String(current.parentId));
      }
      return ancestors;
    };

    const ancestorIds = getAncestors(nodeId);

    setToggledNodes(prev => {
      const newToggled = new Set(prev);
      ancestorIds.forEach(id => newToggled.delete(String(id)));
      return newToggled;
    });

    setSelectedNodeId(String(nodeId));
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleNodeToggle = useCallback((nodeId: string) => {
    setToggledNodes(prev => {
      const newToggled = new Set(prev);
      if (newToggled.has(nodeId)) {
        newToggled.delete(nodeId);
      } else {
        newToggled.add(nodeId);
      }
      return newToggled;
    });
  }, []);

  const handleSaveState = () => {
    if (!svgRef.current) return;
    const transform = d3.zoomTransform(svgRef.current);
    const stateToSave = {
      toggledNodes: Array.from(toggledNodes),
      transform: {
        k: transform.k,
        x: transform.x,
        y: transform.y,
      },
    };
    localStorage.setItem('mindMapState', JSON.stringify(stateToSave));
    setHasSavedState(true);
    alert('View saved successfully!');
  };

  const handleRestoreState = () => {
    const savedStateJSON = localStorage.getItem('mindMapState');
    if (!savedStateJSON || !svgRef.current) return;

    const savedState = JSON.parse(savedStateJSON);

    setToggledNodes(new Set(savedState.toggledNodes));

    const { k, x, y } = savedState.transform;
    const transform = d3.zoomIdentity.translate(x, y).scale(k);

    const svg = d3.select(svgRef.current);
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>().on('zoom', (event) => {
      d3.select(gRef.current).attr('transform', event.transform.toString());
    });

    svg.call(zoomBehavior).transition().duration(750).call(zoomBehavior.transform, transform);
  };

  const { nodes, links } = useMemo(() => {
    // 1. Data Cleaning: Ensure unique IDs
    const uniqueData: RawNode[] = [];
    const seenIds = new Set<number>();
    for (const item of initialData) {
      if (!seenIds.has(item.id)) {
        uniqueData.push(item);
        seenIds.add(item.id);
      }
    }

    // 2. Add a virtual root node to handle multiple roots
    const dataWithRoot: (RawNode | {id: number; name: string; description: string; type: 'folder'; parentId: null})[] = [
      { id: 0, name: "Mind Map", description: "Root", type: 'folder', parentId: null },
      ...uniqueData.map(d => (d.parentId === null ? { ...d, parentId: 0 } : d))
    ];

    // 3. Create hierarchy using d3.stratify
    const root = d3.stratify<any>()
      .id(d => d.id)
      .parentId(d => d.parentId)
      (dataWithRoot) as d3.HierarchyNode<MindMapNode>;

    // 4. Augment nodes with data and handle toggling
    root.each((node: any) => {
      node.data.id = node.id;
      node.data.name = node.data.name || node.id;
      node.data.type = node.data.type;
      node.data.description = node.data.description;

      if (toggledNodes.has(node.id!) && node.children) {
        node._children = node.children;
        node.children = undefined;
      }
    });

    // 5. Create tree layout
    const treeLayout = d3.tree<MindMapNode>().nodeSize([40, 300]);
    const hierarchy = treeLayout(root as d3.HierarchyNode<MindMapNode>);

    const nodes = hierarchy.descendants() as D3HierarchyNode[];
    const links = hierarchy.links();

    return { nodes, links };
  }, [toggledNodes]);

  // Effect for setting up zoom and pan
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    const g = d3.select(gRef.current);

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Center the view on initial load only if no state is restored
    const isInitialLoad = !localStorage.getItem('mindMapState');
    if (isInitialLoad) {
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        nodes.forEach(node => {
            const [x, y] = [node.y, node.x]; // horizontal layout
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            minY = Math.min(minY, y);
            maxY = Math.max(maxY, y);
        });
        
        const svgElement = svg.node();
        if (!svgElement) return;

        const { width, height } = svgElement.getBoundingClientRect();
        const midX = (maxX + minX) / 2;
        const midY = (maxY + minY) / 2;

        const initialTransform = d3.zoomIdentity
            .translate(width / 2 - midX, height / 2 - midY)
            .scale(0.8);

        svg.call(zoom.transform, initialTransform);
    }
    
    return () => {
      svg.on('.zoom', null); // Clean up zoom listener
    };
  }, [nodes.length]); // Rerun if nodes length changes drastically on first render


  // Effect for centering on selected node
  useEffect(() => {
    if (selectedNodeId && svgRef.current) {
      const targetNode = nodes.find(n => n.id === selectedNodeId);
      const svg = d3.select(svgRef.current);
      
      const svgNode = svg.node();
      if (!targetNode || !svgNode) return;

      const { width, height } = svgNode.getBoundingClientRect();
      const scale = 1.2;

      const transform = d3.zoomIdentity
        .translate(width / 2 - targetNode.y * scale, height / 2 - targetNode.x * scale)
        .scale(scale);

      const zoom = d3.zoom<SVGSVGElement, unknown>().on('zoom', (event) => {
        d3.select(gRef.current).attr('transform', event.transform.toString());
      });

      svg.transition()
        .duration(750)
        .call(zoom.transform, transform);
    }
  }, [selectedNodeId, nodes]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="flex-shrink-0 bg-gray-800 p-4 text-center shadow-lg z-20">
        <div className="flex justify-between items-center mb-3">
          <a href="../index.html" className="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 transition-colors text-sm">
            ← Back to Blueprint
          </a>
          <h1 className="text-2xl font-bold tracking-wider text-sky-400">Interactive Mind Map Visualizer</h1>
          <div style={{width: '120px'}}></div>
        </div>
        <p className="text-sm text-gray-400 mt-1">Click folder nodes to toggle branches, or search below.</p>
        
        <div className="flex justify-center items-center gap-2 mt-4">
          <button
            onClick={handleSaveState}
            className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-400 transition-colors"
          >
            Save View
          </button>
          <button
            onClick={handleRestoreState}
            disabled={!hasSavedState}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
          >
            Restore View
          </button>
        </div>
        
        <div className="relative mt-3 max-w-md mx-auto">
          <input
            type="text"
            placeholder="Search by name or description..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 text-gray-200 placeholder-gray-500"
          />
          {searchResults.length > 0 && (
            <ul className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-60 overflow-y-auto">
              {searchResults.map(node => (
                <li
                  key={node.id}
                  onClick={() => handleSearchResultClick(node.id)}
                  className="px-4 py-2 text-left cursor-pointer hover:bg-gray-600 transition-colors duration-150"
                >
                  <div className="font-semibold">{node.name}</div>
                  <div className="text-xs text-gray-400 truncate">{node.description}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </header>
      <main className="flex-grow w-full h-full overflow-hidden">
        <svg ref={svgRef} width="100%" height="100%" className="cursor-grab active:cursor-grabbing">
          <g ref={gRef}>
            {links.map((link, i) => (
              <Edge key={i} link={link} />
            ))}
            {nodes.map((node) => (
              <Node 
                key={node.id} 
                node={node} 
                onToggle={handleNodeToggle} 
                isSelected={node.id === selectedNodeId}
              />
            ))}
          </g>
        </svg>
      </main>
    </div>
  );
};

export default App;
