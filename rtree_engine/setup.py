from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11

__version__ = "0.0.1"

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "rtree_engine",
        [
            # Python bindings file
            "python_bindings.cpp",
            # Your friend's C++ source files
            "src/geometry.cpp",
            "src/RTreeNode.cpp", 
            "src/RTree.cpp",
            "src/engine.cpp",
        ],
        include_dirs=[
            # pybind11 headers
            pybind11.get_include(),
            # Your project headers
            "src/",
            "src/vendor/",
        ],
        # C++ standard
        cxx_std=17,
        # Preprocessor definitions
        define_macros=[("VERSION_INFO", __version__)],
        # Additional compiler flags (optional)
        extra_compile_args=[],
    ),
]

setup(
    name="rtree_engine",
    version=__version__,
    author="Your Name",
    author_email="your.email@example.com",
    description="R-tree spatial indexing engine with Python bindings",
    long_description="A high-performance R-tree implementation for spatial indexing and searching",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
    ],
)
