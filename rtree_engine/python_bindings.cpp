#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

// Include your friend's headers
#include "geometry.h"
#include "RTree.h"
#include "engine.h"
// #include "property.h"  // Uncomment if this exists

namespace py = pybind11;

PYBIND11_MODULE(rtree_engine, m) {
    m.doc() = "R-tree spatial indexing engine with Python bindings";
    
    // Version info
    m.attr("__version__") = "0.0.1";
    
    // ========================================
    // Basic test functions
    // ========================================
    m.def("hello", []() {
        return "Hello from C++ R-tree engine!";
    }, "Test function to verify module is working");
    
    m.def("version", []() {
        return "R-tree Engine v0.0.1";
    }, "Get version information");
    
    // ========================================
    // Point struct binding
    // ========================================
    py::class_<Point>(m, "Point", "2D point with x, y coordinates")
        .def(py::init<>(), "Default constructor")
        .def_readwrite("x", &Point::x, "X coordinate")
        .def_readwrite("y", &Point::y, "Y coordinate")
        .def("__repr__", [](const Point& p) {
            return "Point(x=" + std::to_string(p.x) + ", y=" + std::to_string(p.y) + ")";
        });
    
    // ========================================
    // Rectangle struct binding
    // ========================================
    py::class_<Rectangle>(m, "Rectangle", "Rectangle defined by min and max points")
        .def(py::init<>(), "Default constructor")
        .def_readwrite("min_point", &Rectangle::min_point, "Minimum point (bottom-left)")
        .def_readwrite("max_point", &Rectangle::max_point, "Maximum point (top-right)")
        .def("area", &Rectangle::area, "Calculate rectangle area")
        .def("intersects", &Rectangle::intersects, "Check if this rectangle intersects with another",
             py::arg("other"))
        .def("enlargement", &Rectangle::enlargement, "Calculate enlargement needed to include another rectangle",
             py::arg("other"))
        .def("__repr__", [](const Rectangle& r) {
            return "Rectangle(min=(" + std::to_string(r.min_point.x) + "," + std::to_string(r.min_point.y) + 
                   "), max=(" + std::to_string(r.max_point.x) + "," + std::to_string(r.max_point.y) + "))";
        });
    
    // ========================================
    // RTree class binding
    // ========================================
    py::class_<RTree>(m, "RTree", "R-tree spatial index data structure")
        .def(py::init<>(), "Create a new R-tree")
        .def("insert", [](RTree& self, const Point& point, int id) {
            self.insert(point, id);
        }, "Insert a point with associated ID into the tree",
           py::arg("point"), py::arg("id"))
        .def("search", [](const RTree& self, const Rectangle& query_box) {
            return self.search(query_box);
        }, "Search for all points within the given rectangle",
           py::arg("query_box"))
        .def("clear", [](RTree& self) {
            self.clear();
        }, "Clear all entries from the tree")
        .def("__repr__", [](const RTree& tree) {
            return "RTree()";
        });
    
    // ========================================
    // SpatialSearchEngine class binding
    // ========================================
    py::class_<SpatialSearchEngine>(m, "SpatialSearchEngine", "High-level spatial search engine")
        .def(py::init<>(), "Create a new spatial search engine")
        .def("load_data", [](SpatialSearchEngine& self, const std::string& filepath) {
            return self.load_data(filepath);
        }, "Load property data from JSON file",
           py::arg("filepath"))
        .def("search_properties", [](const SpatialSearchEngine& self, const Rectangle& query_box) {
            return self.search_properties(query_box);
        }, "Search for properties within the given bounding box",
           py::arg("query_box"))
        .def("get_property_by_id", [](const SpatialSearchEngine& self, int id) {
            return self.get_property_by_id(id);
        }, "Retrieve a property by its ID",
           py::arg("id"))
        .def("__repr__", [](const SpatialSearchEngine& engine) {
            return "SpatialSearchEngine()";
        });
    
    // ========================================
    // Convenience functions
    // ========================================
    m.def("create_point", [](double x, double y) {
        Point p;
        p.x = x;
        p.y = y;
        return p;
    }, "Create a Point from x, y coordinates",
       py::arg("x"), py::arg("y"));
    
    m.def("create_rectangle", [](double min_x, double min_y, double max_x, double max_y) {
        Rectangle rect;
        rect.min_point.x = min_x;
        rect.min_point.y = min_y;
        rect.max_point.x = max_x;
        rect.max_point.y = max_y;
        return rect;
    }, "Create a Rectangle from min/max coordinates",
       py::arg("min_x"), py::arg("min_y"), py::arg("max_x"), py::arg("max_y"));
    
    m.def("create_rectangle_from_points", [](const Point& min_point, const Point& max_point) {
        Rectangle rect;
        rect.min_point = min_point;
        rect.max_point = max_point;
        return rect;
    }, "Create a Rectangle from two Point objects",
       py::arg("min_point"), py::arg("max_point"));
    
    // ========================================
    // Utility functions
    // ========================================
    m.def("point_in_rectangle", [](const Point& point, const Rectangle& rect) {
        return (point.x >= rect.min_point.x && point.x <= rect.max_point.x &&
                point.y >= rect.min_point.y && point.y <= rect.max_point.y);
    }, "Check if a point is inside a rectangle",
       py::arg("point"), py::arg("rectangle"));
    
    m.def("distance", [](const Point& p1, const Point& p2) {
        double dx = p1.x - p2.x;
        double dy = p1.y - p2.y;
        return std::sqrt(dx * dx + dy * dy);
    }, "Calculate Euclidean distance between two points",
       py::arg("point1"), py::arg("point2"));
}
