cmake_minimum_required(VERSION 3.16)
project(secure_calc VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(FLTK REQUIRED)

add_executable(secure_calc
    src/main.cpp
)

if(TARGET fltk::fltk)
    target_link_libraries(secure_calc PRIVATE fltk::fltk)
elseif(TARGET fltk)
    target_link_libraries(secure_calc PRIVATE fltk)
elseif(FLTK_LIBRARIES)
    target_link_libraries(secure_calc PRIVATE ${FLTK_LIBRARIES})
else()
    target_link_libraries(secure_calc PRIVATE fltk)
endif()

# Some FLTK discovery paths provide include directories via variables instead of target usage requirements.
if(DEFINED FLTK_INCLUDE_DIR AND FLTK_INCLUDE_DIR)
    target_include_directories(secure_calc PRIVATE "${FLTK_INCLUDE_DIR}")
endif()
if(DEFINED FLTK_INCLUDE_DIRS AND FLTK_INCLUDE_DIRS)
    target_include_directories(secure_calc PRIVATE ${FLTK_INCLUDE_DIRS})
endif()

if(MSVC)
    target_compile_options(secure_calc PRIVATE /W4 /permissive- /EHsc)
else()
    target_compile_options(secure_calc PRIVATE -Wall -Wextra -Wpedantic -Wconversion)
endif()
