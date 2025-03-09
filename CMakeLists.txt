cmake_minimum_required(VERSION 3.21.1)

option(LINK_INSIGHT "Link Qt Insight Tracker library" ON)
option(BUILD_QDS_COMPONENTS "Build design studio components" ON)

project(QllamaTalkApp LANGUAGES CXX)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/download_llama_model.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/llama_setup.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/llmRemoteServer_setup.cmake)

# Include paths for fastText
# include_directories(/home/caio/fastText/src/fasttext)

include_directories(/usr/local/include)


# FAISS and Poppler includes (adjust if needed)
# include_directories(/usr/local/include)
set(CMAKE_AUTOMOC ON)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
find_package(Qt6 6.2 REQUIRED COMPONENTS Core Gui Qml Quick QuickControls2 TextToSpeech Core5Compat)
find_library(FAISS_LIB NAMES faiss HINTS /usr/local/lib /usr/lib)

if (Qt6_VERSION VERSION_GREATER_EQUAL 6.3)
    qt_standard_project_setup()
endif()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
qt_add_executable(QllamaTalkApp
    src/main.cpp
)

include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/download_whisper_model.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/whisper_setup.cmake)


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
qt_add_resources(QllamaTalkApp "configuration"
    PREFIX "/"
    FILES
        qtquickcontrols2.conf
)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
target_link_libraries(QllamaTalkApp PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Qml
    Qt6::Quick
    Qt6::QuickControls2
    Qt6::TextToSpeech
    Qt6::Core5Compat
    ${FAISS_LIB}  # Link FAISS
    # poppler-qt5
    # fasttext
    # pthread
)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
if (BUILD_QDS_COMPONENTS)
    include(${CMAKE_CURRENT_SOURCE_DIR}/qmlcomponents)
endif()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
include(${CMAKE_CURRENT_SOURCE_DIR}/qmlmodules)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
if (LINK_INSIGHT)
    include(${CMAKE_CURRENT_SOURCE_DIR}/insight)
endif()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
include(GNUInstallDirs)
install(TARGETS QllamaTalkApp
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# make IDEs aware of the QML import path
set(QML_IMPORT_PATH ${PROJECT_BINARY_DIR}/qml CACHE PATH
    "Path to the custom QML components defined by the project")

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
if(ANDROID)
    include(FetchContent)
    FetchContent_Declare(
        android_openssl
        DOWNLOAD_EXTRACT_TIMESTAMP true
        URL https://github.com/KDAB/android_openssl/archive/refs/heads/master.zip
    )
    FetchContent_MakeAvailable(android_openssl)
    include(${android_openssl_SOURCE_DIR}/android_openssl.cmake)

    add_android_openssl_libraries(QllamaTalkApp)
    target_link_libraries(QllamaTalkApp PRIVATE ${android_extra_libs})

    set(LLAMA_SO_PATH "${LLAMA_DYNAMIC_LIB_FILE_DIR}/libllama.so")
    file(GLOB GGML_SO_PATHS "${GGML_DYNAMIC_LIB_FILE_DIR}/libggml*.so")

    # llama
    add_library(llama SHARED IMPORTED)
    set_target_properties(llama PROPERTIES
        IMPORTED_LOCATION "${LLAMA_SO_PATH}"
        ANDROID_PACKAGE_SHARED_LIBS ON
    )
    target_link_libraries(QllamaTalkApp PRIVATE llama)

    list(LENGTH GGML_SO_PATHS GGML_COUNT)
    if(GGML_COUNT GREATER 0)
        foreach(ggml_file IN LISTS GGML_SO_PATHS)
            get_filename_component(ggml_name ${ggml_file} NAME_WE)
            string(REPLACE "-" "_" ggml_target_name ${ggml_name})
            add_library(${ggml_target_name} SHARED IMPORTED)
            set_target_properties(${ggml_target_name} PROPERTIES
                IMPORTED_LOCATION "${ggml_file}"
                ANDROID_PACKAGE_SHARED_LIBS ON
            )
            target_link_libraries(QllamaTalkApp PRIVATE ${ggml_target_name})
        endforeach()
    endif()

    # whisper
    add_library(whisper SHARED IMPORTED)
    set_target_properties(whisper PROPERTIES
        IMPORTED_LOCATION "${WHISPER_LIB_FILE_DIR}/libwhisper.so"
        ANDROID_PACKAGE_SHARED_LIBS ON
    )
    target_link_libraries(QllamaTalkApp PRIVATE whisper)

    message(STATUS "IMPORTED llama => ${LLAMA_SO_PATH}")
    message(STATUS "IMPORTED ggml  => ${GGML_SO_PATHS}")
    message(STATUS "IMPORTED whisper => ${WHISPER_LIB_FILE_DIR}/libwhisper.so")
endif()
