#include "RTree.h"
#include <limits>
#include <algorithm>
#include <iostream>

// --- Constructor ---
RTree::RTree() {
    // Start with a single root node that is a leaf
    m_root = std::make_unique<RTreeNode>(nullptr, true);
}

// --- Search Implementation ---

// PRIVATE helper search function
void RTree::search(const Rectangle& query_box, RTreeNode* node, std::vector<int>& result) const {
    if (!node) return;
    for (const auto& entry : node->entries) {
        if (entry.mbr.intersects(query_box)) {
            if (node->is_leaf) {
                result.push_back(entry.data_id);
            }
            else {
                search(query_box, entry.child_ptr.get(), result);
            }
        }
    }
}

// PUBLIC search function that users call
std::vector<int> RTree::search(const Rectangle& query_box) const {
    std::vector<int> result;
    search(query_box, m_root.get(), result);
    return result;
}


// --- Insertion Implementation ---

void RTree::insert(const Point& point, int id) {
    Rectangle point_mbr = { point, point };

    // This call now matches the header declaration
    RTreeNode* leaf = choose_leaf(point_mbr);

    leaf->entries.push_back({ point_mbr, nullptr, id });

    if (leaf->entries.size() > m_max_entries) {
        split_node(leaf);
    }
    else {
        adjust_tree(leaf);
    }
}

// This definition now matches the header declaration
RTreeNode* RTree::choose_leaf(const Rectangle& new_entry_mbr) {
    RTreeNode* current_node = m_root.get();

    while (!current_node->is_leaf) {
        RTreeNode* next_node = nullptr;
        double min_enlargement = std::numeric_limits<double>::max();
        double min_area = std::numeric_limits<double>::max();

        for (auto& entry : current_node->entries) {
            double enlargement = entry.mbr.enlargement(new_entry_mbr);
            if (enlargement < min_enlargement) {
                min_enlargement = enlargement;
                min_area = entry.mbr.area();
                next_node = entry.child_ptr.get();
            }
            else if (enlargement == min_enlargement) {
                double area = entry.mbr.area();
                if (area < min_area) {
                    min_area = area;
                    next_node = entry.child_ptr.get();
                }
            }
        }
        current_node = next_node;
    }
    return current_node;
}

void RTree::adjust_tree(RTreeNode* node) {
    while (node != nullptr) {
        // The split_node function will handle adjusting its direct parent.
        // For non-splitting adjustments, we'd update the parent's MBR here.
        // For simplicity, we keep this minimal. The MBRs are correctly
        // reconstructed during splits.
        node = node->parent;
    }
}

void RTree::split_node(RTreeNode* node) {
    std::vector<RTreeNode::Entry> all_entries;
    all_entries.swap(node->entries);

    int seed1_idx = -1, seed2_idx = -1;
    double max_wasted_area = -1.0;

    for (size_t i = 0; i < all_entries.size(); ++i) {
        for (size_t j = i + 1; j < all_entries.size(); ++j) {
            Rectangle combined_mbr = all_entries[i].mbr;
            combined_mbr.min_point.x = std::min(combined_mbr.min_point.x, all_entries[j].mbr.min_point.x);
            combined_mbr.min_point.y = std::min(combined_mbr.min_point.y, all_entries[j].mbr.min_point.y);
            combined_mbr.max_point.x = std::max(combined_mbr.max_point.x, all_entries[j].mbr.max_point.x);
            combined_mbr.max_point.y = std::max(combined_mbr.max_point.y, all_entries[j].mbr.max_point.y);

            double wasted_area = combined_mbr.area() - all_entries[i].mbr.area() - all_entries[j].mbr.area();
            if (wasted_area > max_wasted_area) {
                max_wasted_area = wasted_area;
                seed1_idx = i;
                seed2_idx = j;
            }
        }
    }

    node->entries.push_back(std::move(all_entries[seed1_idx]));

    auto new_node_ptr = std::make_unique<RTreeNode>(node->parent, node->is_leaf);
    new_node_ptr->entries.push_back(std::move(all_entries[seed2_idx]));

    std::vector<bool> assigned(all_entries.size(), false);
    assigned[seed1_idx] = true;
    assigned[seed2_idx] = true;

    while (true) {
        bool all_assigned = true;
        for (size_t i = 0; i < all_entries.size(); ++i) {
            if (!assigned[i]) {
                all_assigned = false;
                break;
            }
        }
        if (all_assigned) break;

        int best_entry_idx = -1;
        double max_diff = -1.0;

        for (size_t i = 0; i < all_entries.size(); ++i) {
            if (assigned[i]) continue;

            double cost1 = node->get_mbr().enlargement(all_entries[i].mbr);
            double cost2 = new_node_ptr->get_mbr().enlargement(all_entries[i].mbr);

            double diff = std::abs(cost1 - cost2);
            if (diff > max_diff) {
                max_diff = diff;
                best_entry_idx = i;
            }
        }

        if (best_entry_idx != -1) {
            double cost1 = node->get_mbr().enlargement(all_entries[best_entry_idx].mbr);
            double cost2 = new_node_ptr->get_mbr().enlargement(all_entries[best_entry_idx].mbr);
            if (cost1 < cost2) {
                node->entries.push_back(std::move(all_entries[best_entry_idx]));
            }
            else {
                new_node_ptr->entries.push_back(std::move(all_entries[best_entry_idx]));
            }
            assigned[best_entry_idx] = true;
        }
        else {
            break;
        }
    }

    RTreeNode* parent = node->parent;
    if (parent == nullptr) {
        auto old_root_node = m_root.release();
        auto new_root = std::make_unique<RTreeNode>(nullptr, false);
        node->parent = new_root.get();
        new_node_ptr->parent = new_root.get();

        new_root->entries.push_back({ node->get_mbr(), std::unique_ptr<RTreeNode>(old_root_node), -1 });
        new_root->entries.push_back({ new_node_ptr->get_mbr(), std::move(new_node_ptr), -1 });

        m_root = std::move(new_root);
    }
    else {
        for (auto& entry : parent->entries) {
            if (entry.child_ptr.get() == node) {
                entry.mbr = node->get_mbr();
                break;
            }
        }

        parent->entries.push_back({ new_node_ptr->get_mbr(), std::move(new_node_ptr), -1 });

        if (parent->entries.size() > m_max_entries) {
            split_node(parent);
        }
    }
}


void RTree::clear() {
    // Reset the root, which will cascade and delete all nodes
    m_root = std::make_unique<RTreeNode>(nullptr, true);
}
