#pragma once

#include <string>
#include "geometry.h" // Include our geometry for the point

struct Property {
    int id;
    std::string address;
    double price;
    int bedrooms;
    double bathrooms; // Using double for half-baths
    double square_footage;
    Point location; // The spatial data for the R-Tree
    std::string property_type; // e.g., "House", "Apartment", "Condo"

    // Optional: Constructor for easy initialization
    Property(int _id, const std::string& _address, double _price, int _bedrooms, double _bathrooms, double _sqft, Point _loc, const std::string& _type)
        : id(_id), address(_address), price(_price), bedrooms(_bedrooms), bathrooms(_bathrooms), square_footage(_sqft), location(_loc), property_type(_type) {
    }
};
