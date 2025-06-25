#include <iostream>
#include "engine.h"

// Using namespace std for this file
using namespace std;

int main() {
    SpatialSearchEngine engine;

    cout << "R-Tree Search Engine starting..." << endl;

    // Load data from our new JSON file
    if (!engine.load_data("../data/properties.json")) {
        cerr << "Failed to load data. Exiting." << endl;
        return 1;
    }

    // Define a search area around San Francisco
    Rectangle search_area = { {-122.5, 37.7}, {-122.3, 37.8} };

    cout << "\nSearching for properties in San Francisco area..." << endl;

    // Perform the search
    vector<Property> results = engine.search_properties(search_area);

    // Print the results
    cout << "Found " << results.size() << " properties:" << endl;
    for (const auto& prop : results) {
        cout << " - ID: " << prop.id << ", Address: " << prop.address << endl;
    }
    // Expected to find property with ID 1

    return 0;
}
