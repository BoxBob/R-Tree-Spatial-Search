#include "engine.h"
#include <fstream>
#include <iostream>
#include "json.hpp" // The JSON library we just added

// For convenience in this file
using namespace std;
using json = nlohmann::json;

SpatialSearchEngine::SpatialSearchEngine() {
    // Constructor is fine
}

bool SpatialSearchEngine::load_data(const std::string& filepath) {
    // --- THIS IS NOW IMPLEMENTED ---
    ifstream file_stream(filepath);
    if (!file_stream.is_open()) {
        cerr << "Error: Could not open data file: " << filepath << endl;
        return false;
    }

    json data;
    try {
        file_stream >> data; // Parse the entire file into a JSON object
    }
    catch (json::parse_error& e) {
        cerr << "Error: Failed to parse JSON file. " << e.what() << endl;
        return false;
    }

    cout << "Loading " << data.size() << " properties..." << endl;

    // Clear any existing data
    m_properties.clear();
    m_rtree.clear(); // Re-initialize the R-Tree

    for (const auto& item : data) {
        Point loc = { item["location"]["x"], item["location"]["y"] };

        Property prop(
            item["id"],
            item["address"],
            item["price"],
            item["bedrooms"],
            item["bathrooms"],
            item["square_footage"],
            loc,
            item["property_type"]
        );

        // Store the full property object
        m_properties.emplace(prop.id, prop);
        // Insert the location and ID into our spatial index
        m_rtree.insert(loc, prop.id);
    }

    cout << "Data loading complete." << endl;
    return true;
}

// ... rest of the file is the same ...
vector<Property> SpatialSearchEngine::search_properties(const Rectangle& query_box) const {
    vector<int> property_ids = m_rtree.search(query_box);
    vector<Property> results;
    for (int id : property_ids) {
        auto it = m_properties.find(id);
        if (it != m_properties.end()) {
            results.push_back(it->second);
        }
    }
    return results;
}

Property SpatialSearchEngine::get_property_by_id(int id) const {
    auto it = m_properties.find(id);
    if (it != m_properties.end()) {
        return it->second;
    }
    return Property(-1, "Not Found", 0.0, 0, 0.0, 0.0, { 0.0, 0.0 }, "Unknown");
}
