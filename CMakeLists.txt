cmake_minimum_required(VERSION 3.12)
project(adcensus_py)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find OpenCV
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Use pybind11 from Python package (installed via pip)
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYBIND11_FOUND
)

if(NOT PYBIND11_FOUND EQUAL 0)
    message(FATAL_ERROR "pybind11 not found. Please install it: pip install pybind11")
endif()

# Add pybind11 using the directory from Python
list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

# Source files
set(ADCENSUS_SOURCES
    AD-Census/ADCensusStereo.cpp
    AD-Census/cost_computor.cpp
    AD-Census/cross_aggregator.cpp
    AD-Census/scanline_optimizer.cpp
    AD-Census/multistep_refiner.cpp
    AD-Census/adcensus_util.cpp
)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/AD-Census
    ${Python_INCLUDE_DIRS}
)

# Create Python module
pybind11_add_module(adcensus_py 
    python/adcensus_wrapper.cpp
    ${ADCENSUS_SOURCES}
)

# Link libraries
target_link_libraries(adcensus_py PRIVATE ${OpenCV_LIBS})

# Set output directory - the setup.py will handle copying to the right place
set_target_properties(adcensus_py PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}
)

