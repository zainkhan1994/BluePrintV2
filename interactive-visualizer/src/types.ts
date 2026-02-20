import type { HierarchyPointNode, HierarchyNode } from 'd3-hierarchy';

export interface RawNode {
  id: number;
  name: string;
  description: string;
  type: 'folder' | 'file';
  parentId: number | null;
}

export interface MindMapNode {
  id: string;
  name: string;
  description: string;
  type: 'folder' | 'file';
  children?: MindMapNode[];
  _children?: MindMapNode[];
}

// FIX: Add _children to D3HierarchyNode type definition to support node collapsing.
// This property is added dynamically to store children of collapsed nodes.
export type D3HierarchyNode = HierarchyPointNode<MindMapNode> & {
  _children?: HierarchyNode<MindMapNode>[];
};
