
import React from 'react';
import * as d3 from 'd3';
import type { MindMapNode } from '../types';

interface EdgeProps {
  link: d3.HierarchyPointLink<MindMapNode>;
}

const Edge: React.FC<EdgeProps> = ({ link }) => {
  const linkGenerator = d3.linkHorizontal<any, d3.HierarchyPointNode<MindMapNode>>()
    .x(d => d.y)
    .y(d => d.x);

  const pathData = linkGenerator(link);

  return (
    <path
      d={pathData || ''}
      className="fill-none stroke-gray-600 stroke-1 transition-all duration-300 ease-in-out"
    />
  );
};

export default Edge;
