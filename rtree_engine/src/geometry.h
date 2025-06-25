#pragma once // Prevents the file from being included multiple times

struct Point {
    double x, y;
};

struct Rectangle {
    Point min_point;
    Point max_point;

    // Calculate the area of the rectangle
    double area() const;

    // Check if this rectangle intersects with another one
    bool intersects(const Rectangle& other) const;

    // Calculate how much this rectangle would have to grow to include another one
    double enlargement(const Rectangle& other) const;
};
