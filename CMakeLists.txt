cmake_minimum_required(VERSION 3.14)
#set(Boost_NO_WARN_NEW_VERSIONS 1)
set(QT_CREATOR_SKIP_VCPKG_SETUP ON)
project(train_ai_play_minsweeper VERSION 1.0.0)


option(BUILD_PRISM_ALL "BUILD_PRISM_ALL" ON)
option(BUILD_DATA_COLLECTOR "data_collector" ON)





set(USING_PRISM_QT_UI_VNCITEM ON)
add_compile_definitions(USING_PRISM_QT_UI_VNCITEM)


if(BUILD_DATA_COLLECTOR)
    add_subdirectory(third-party/prism_all)
endif()
if(BUILD_PRISM_ALL)
    add_subdirectory(data_collector)
endif()

