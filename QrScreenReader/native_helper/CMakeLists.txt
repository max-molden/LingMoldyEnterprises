cmake_minimum_required(VERSION 3.16)
project(QRHotkeyHelper LANGUAGES CXX)

add_executable(QRHotkeyHelper QRHotkeyHelper.cpp)
target_compile_features(QRHotkeyHelper PRIVATE cxx_std_17)
target_link_libraries(QRHotkeyHelper PRIVATE user32 shell32)

if (MSVC)
  target_compile_options(QRHotkeyHelper PRIVATE /O2 /W4 /permissive-)
else()
  target_compile_options(QRHotkeyHelper PRIVATE -O2 -Wall -Wextra)
endif()
