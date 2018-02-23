cmake_minimum_required(VERSION 3.8)

if( NOT APP_NAME OR APP_NAME STREQUAL "" )
	message(FATAL_ERROR "APP_NAME not set! Please set APP_NAME to appropriate value when running this CMake script.")
endif()

project(${APP_NAME})

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/scripts/cmake")

include(FindSources)
include(gtest)

find_source_files(lib_sources "${PROJECT_SOURCE_DIR}/src/lib")
# message(STATUS "lib_sources = : " ${lib_sources})
add_library(${LIB_NAME} ${lib_sources})
target_include_directories(${LIB_NAME}
	PUBLIC "${PROJECT_SOURCE_DIR}/src/lib")

find_source_files(app_sources "${PROJECT_SOURCE_DIR}/src/app")
# message(STATUS "app_sources = : " ${app_sources})
add_executable(${APP_NAME} ${app_sources})
target_link_libraries(${APP_NAME} ${LIB_NAME})

find_source_files(test_sources "${PROJECT_SOURCE_DIR}/src/tests")
# message(STATUS "test_sources = : " ${test_sources})
add_executable(${TESTS_NAME} ${test_sources})
target_link_libraries(${TESTS_NAME} ${LIB_NAME} gtest)
