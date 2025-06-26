cmake_minimum_required(VERSION 3.16)
project(RTreeSearchEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Find Python and pybind11 ---
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Get pybind11 include directory
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pybind11; print(pybind11.get_include())"
    OUTPUT_VARIABLE PYBIND11_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "pybind11 include directory: ${PYBIND11_INCLUDE_DIR}")

# --- Core Engine Library ---
add_library(rtree_lib
    src/geometry.cpp
    src/RTreeNode.cpp
    src/RTree.cpp
    src/engine.cpp
)
target_include_directories(rtree_lib PUBLIC src src/vendor)

# --- Main Application Executable ---
add_executable(rtree_server src/main.cpp)
target_link_libraries(rtree_server PRIVATE rtree_lib)

# --- Python Module ---
add_library(rtree_engine MODULE python_bindings.cpp)
target_link_libraries(rtree_engine PRIVATE rtree_lib)

# Add pybind11 and Python include directories manually
target_include_directories(rtree_engine PRIVATE 
    ${PYBIND11_INCLUDE_DIR}
    ${Python_INCLUDE_DIRS}  # <-- This line is correct, just ensure this variable is populated
    src/
    src/vendor/
)

# Also link against Python libraries if needed (important!)
target_link_libraries(rtree_engine PRIVATE ${Python_LIBRARIES})

# Set module properties
set_target_properties(rtree_engine PROPERTIES
    PREFIX ""
    SUFFIX ".pyd"  # Windows
    # SUFFIX ".so"  # Linux/Mac - uncomment if on Linux/Mac
)

# --- Testing Setup ---
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(run_tests tests/test_geometry.cpp)
target_link_libraries(run_tests PRIVATE rtree_lib GTest::gtest_main)
