#include "RTreeNode.h"
#include <limits> // For numeric_limits
using namespace std;
// Calculate the MBR of the entire node by unioning the MBRs of all its entries
Rectangle RTreeNode::get_mbr() const {
    if (entries.empty()) {
        // Return an invalid rectangle if the node is empty
        return {{numeric_limits<double>::max(), numeric_limits<double>::max()},
                {numeric_limits<double>::lowest(), numeric_limits<double>::lowest()}};
    }

    Rectangle mbr = entries[0].mbr;
    for (size_t i = 1; i < entries.size(); ++i) {
        const auto& entry_mbr = entries[i].mbr;
        mbr.min_point.x = min(mbr.min_point.x, entry_mbr.min_point.x);
        mbr.min_point.y = min(mbr.min_point.y, entry_mbr.min_point.y);
        mbr.max_point.x = max(mbr.max_point.x, entry_mbr.max_point.x);
        mbr.max_point.y = max(mbr.max_point.y, entry_mbr.max_point.y);
    }
    return mbr;
}
