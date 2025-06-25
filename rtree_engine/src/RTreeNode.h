#pragma once

#include "geometry.h"
#include <vector>
#include <memory> // For std::unique_ptr

// Forward declaration to break circular dependency with RTree
class RTree;

struct RTreeNode {
    // An entry in a node can be a pointer to a child node or data ID
    struct Entry {
        Rectangle mbr; // Minimum Bounding Rectangle of the entry
        std::unique_ptr<RTreeNode> child_ptr = nullptr; // Null if it's a leaf entry
        int data_id = -1; // -1 if it's not a leaf entry
    };

    // --- Member Variables ---
    RTreeNode* parent = nullptr;
    bool is_leaf = false;
    std::vector<Entry> entries;

    // --- Constructor ---
    RTreeNode(RTreeNode* p, bool leaf) : parent(p), is_leaf(leaf) {}

    Rectangle get_mbr() const;
};
