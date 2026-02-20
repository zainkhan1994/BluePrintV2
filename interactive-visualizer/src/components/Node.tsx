
import React from 'react';
import type { D3HierarchyNode } from '../types';
import { FolderIcon, FileIcon } from './icons';

interface NodeProps {
  node: D3HierarchyNode;
  onToggle: (id: string) => void;
  isSelected: boolean;
}

const Node: React.FC<NodeProps> = ({ node, onToggle, isSelected }) => {
  const isFolder = node.data.type === 'folder';
  const hasChildren = !!node.children || !!node._children;
  const isToggled = !!node._children;

  const handleToggle = () => {
    if (isFolder && hasChildren) {
      onToggle(node.id!);
    }
  };

  const nodeColor = isFolder ? 'text-sky-400' : 'text-gray-500';
  const circleColor = isFolder ? 'fill-sky-500/20 stroke-sky-400' : 'fill-gray-600/20 stroke-gray-500';
  const hoverColor = isFolder ? 'hover:fill-sky-500/40 hover:stroke-sky-300' : 'hover:fill-gray-600/40 hover:stroke-gray-400';
  const cursor = isFolder && hasChildren ? 'cursor-pointer' : 'cursor-default';

  return (
    <g transform={`translate(${node.y},${node.x})`} className="transition-transform duration-300 ease-in-out group">
      <title>{node.data.description}</title>
      
      {isSelected && (
        <circle
            r={16}
            className="fill-none stroke-yellow-400 stroke-2 animate-pulse"
        />
      )}

      <circle
        r={12}
        className={`stroke-2 transition-all duration-200 ${circleColor} ${hoverColor} ${cursor}`}
        onClick={handleToggle}
      />
      <g transform="translate(-8, -8)" className={`pointer-events-none ${nodeColor}`}>
        {isFolder ? <FolderIcon isToggled={isToggled} /> : <FileIcon />}
      </g>
      <text
        dy="0.31em"
        x={20}
        textAnchor="start"
        className="fill-gray-200 text-sm font-medium select-none"
      >
        {node.data.name}
      </text>
    </g>
  );
};

export default Node;
