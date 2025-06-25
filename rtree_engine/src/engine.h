#pragma once

#include "RTree.h"
#include "property.h"
#include <unordered_map>
#include <string>
#include <vector>

class SpatialSearchEngine {
public:
    SpatialSearchEngine();

    // Load property data from a JSON file
    bool load_data(const std::string& filepath);

    // Search for properties within a given geographical bounding box
    std::vector<Property> search_properties(const Rectangle& query_box) const;

    // Retrieve a property by its ID
    Property get_property_by_id(int id) const;

private:
    RTree m_rtree;
    std::unordered_map<int, Property> m_properties; // Stores all property data by ID
};
