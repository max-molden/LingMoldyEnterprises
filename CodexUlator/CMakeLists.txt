cmake_minimum_required(VERSION 3.16)
project(secure_calc VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(FLTK REQUIRED)

add_executable(secure_calc
    src/main.cpp
)

target_link_libraries(secure_calc PRIVATE fltk)

if(MSVC)
    target_compile_options(secure_calc PRIVATE /W4 /permissive- /EHsc)
else()
    target_compile_options(secure_calc PRIVATE -Wall -Wextra -Wpedantic -Wconversion)
endif()
