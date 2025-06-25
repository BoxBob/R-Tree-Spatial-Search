#include "geometry.h"
#include <algorithm> // For std::min and std::max
using namespace std;
double Rectangle::area() const {
    return (max_point.x - min_point.x) * (max_point.y - min_point.y);
}

bool Rectangle::intersects(const Rectangle& other) const {
    // Two rectangles do not intersect if one is entirely to the left/right/top/bottom of the other.
    // If none of these "no overlap" conditions are true, they must overlap.
    if (this->max_point.x < other.min_point.x || this->min_point.x > other.max_point.x) {
        return false; // No overlap on the x-axis
    }
    if (this->max_point.y < other.min_point.y || this->min_point.y > other.max_point.y) {
        return false; // No overlap on the y-axis
    }
    return true;
}

double Rectangle::enlargement(const Rectangle& other) const {
    // Calculate the MBR of this rectangle and the other one combined
    double combined_min_x = min(min_point.x, other.min_point.x);
    double combined_min_y = min(min_point.y, other.min_point.y);
    double combined_max_x = max(max_point.x, other.max_point.x);
    double combined_max_y = max(max_point.y, other.max_point.y);

    double combined_area = (combined_max_x - combined_min_x) * (combined_max_y - combined_min_y);
    
    // The enlargement is the new area minus the original area
    return combined_area - this->area();
}
