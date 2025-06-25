cmake_minimum_required(VERSION 3.16)
project(RTreeSearchEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

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


# ====================================================================
# --- Testing Setup (MANUAL MODE) ---
# ====================================================================

# We still need to download GoogleTest
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)


# --- Create our test executable AS A NORMAL PROGRAM ---
# NO enable_testing(). NO add_test(). NO ctest.
# This is now just a regular executable that happens to contain tests.
add_executable(run_tests tests/test_geometry.cpp)
target_link_libraries(run_tests PRIVATE rtree_lib GTest::gtest_main)
