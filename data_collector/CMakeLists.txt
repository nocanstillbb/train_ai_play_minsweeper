cmake_minimum_required(VERSION 3.14)

project(data_collector VERSION 0.1 LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core LinguistTools)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Gui Widgets Quick Qml QuickControls2 Concurrent)
#find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Gui Widgets Quick Qml QuickControls2 LinguistTools Sql SerialBus)

find_package(prism COMPONENTS container qt::modular qt::core qt::ui)
find_package(OpenCV CONFIG REQUIRED)

set(PROJECT_SOURCES
        src/main.cpp
        src/qml.qrc
        src/viewmodels/remote_viewmodel.cpp

        models/label.h
)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(data_collector
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )
# Define target properties for Android with Qt 6 as:
#    set_property(TARGET data_collector APPEND PROPERTY QT_ANDROID_PACKAGE_SOURCE_DIR
#                 ${CMAKE_CURRENT_SOURCE_DIR}/android)
# For more information, see https://doc.qt.io/qt-6/qt-add-executable.html#target-creation
else()
    if(ANDROID)
        add_library(data_collector SHARED
            ${PROJECT_SOURCES}
        )
# Define properties for Android with Qt 5 after find_package() calls as:
#    set(ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android")
    else()
        add_executable(data_collector
          ${PROJECT_SOURCES}
        )
    endif()
endif()

message(STATUS "Available OpenCV components: ${OpenCV_LIBS}")
target_compile_definitions(data_collector
  PRIVATE $<$<OR:$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>>:QT_QML_DEBUG>)
target_link_libraries(data_collector PRIVATE
    prism::prism
    prism::container
    prism::qt::modular
    prism::qt::core
    prism::qt::ui

    opencv_core
    opencv_imgcodecs

    Qt${QT_VERSION_MAJOR}::Concurrent
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Gui
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::Quick
    Qt${QT_VERSION_MAJOR}::Qml
    Qt${QT_VERSION_MAJOR}::QuickControls2)


set_target_properties(data_collector PROPERTIES
    MACOSX_BUNDLE_GUI_IDENTIFIER my.example.com
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_import_qml_plugins(data_collector)
    qt_finalize_executable(data_collector)
endif()


add_custom_command(TARGET data_collector POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    $<TARGET_FILE:prism_container>
    $<TARGET_FILE:prism_qt_modular>
    $<TARGET_FILE:prism_qt_core>
    $<TARGET_FILE:prism_qt_ui>
    $<TARGET_FILE_DIR:data_collector>
    )
