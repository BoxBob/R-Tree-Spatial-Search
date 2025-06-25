# CMake generated Testfile for 
# Source directory: C:/RTreeSearchEngine
# Build directory: C:/RTreeSearchEngine/out/build/x64-Debug
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(GeometryTests "C:/RTreeSearchEngine/out/build/x64-Debug/run_tests.exe")
set_tests_properties(GeometryTests PROPERTIES  _BACKTRACE_TRIPLES "C:/RTreeSearchEngine/CMakeLists.txt;42;add_test;C:/RTreeSearchEngine/CMakeLists.txt;0;")
subdirs("_deps/googletest-build")
