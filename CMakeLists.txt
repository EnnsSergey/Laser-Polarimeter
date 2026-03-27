cmake_minimum_required(VERSION 3.25.1 FATAL_ERROR)

project(Polarimeter)

find_package(Geant4 REQUIRED ui_all vis_all)

include(${Geant4_USE_FILE})

include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB sources "source/*.cc")

add_executable(main main.cc ${sources})

target_link_libraries(main ${Geant4_LIBRARIES})

add_custom_target(Polarimeter DEPENDS main)

