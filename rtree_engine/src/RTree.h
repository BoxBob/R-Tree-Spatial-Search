#pragma once

#include "RTreeNode.h"
#include <vector>
#include <memory>

class RTree {
public:
    RTree();

    void insert(const Point& point, int id);
    std::vector<int> search(const Rectangle& query_box) const;
    void clear(); // New method to reset the tree

private:
    void search(const Rectangle& query_box, RTreeNode* node, std::vector<int>& result) const;
    RTreeNode* choose_leaf(const Rectangle& new_entry_mbr);
    void split_node(RTreeNode* node);
    void adjust_tree(RTreeNode* node);

    std::unique_ptr<RTreeNode> m_root;

    // --- The Fix ---
    // Removed 'const' so the class can be assignable if needed.
    int m_max_entries = 4;
    int m_min_entries = 2;
};
