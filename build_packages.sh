#!/bin/bash
"""
GopiAI Cross-Platform Build Script
Builds packages for Linux, Windows, and macOS using Briefcase
"""

set -e

echo "🚀 GopiAI Package Builder"
echo "========================="

# Check if briefcase is available
if ! command -v .venv/bin/briefcase &> /dev/null; then
    echo "❌ Briefcase not found. Please run: pip install briefcase"
    exit 1
fi

# Function to build for a specific platform
build_platform() {
    local platform=$1
    echo
    echo "🏗️ Building for $platform..."
    echo "--------------------------------"
    
    # Create
    echo "📦 Creating $platform build template..."
    .venv/bin/briefcase create $platform
    
    # Build
    echo "🔨 Building $platform package..."
    .venv/bin/briefcase build $platform
    
    # Package
    echo "📦 Packaging $platform application..."
    case $platform in
        "linux")
            .venv/bin/briefcase package $platform appimage
            echo "✅ Linux AppImage created: dist/GopiAI-1.0.0-x86_64.AppImage"
            ;;
        "windows") 
            .venv/bin/briefcase package $platform msi
            echo "✅ Windows installer created: dist/GopiAI-1.0.0.msi"
            ;;
        "macOS")
            .venv/bin/briefcase package $platform dmg
            echo "✅ macOS package created: dist/GopiAI-1.0.0.dmg"
            ;;
    esac
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [linux|windows|macOS|all]"
    echo
    echo "Examples:"
    echo "  $0 linux          # Build only Linux AppImage"
    echo "  $0 windows        # Build only Windows installer"
    echo "  $0 macOS          # Build only macOS package" 
    echo "  $0 all            # Build all platforms"
    exit 1
fi

# Main build logic
case $1 in
    "linux")
        echo "🐧 Building for Linux only..."
        build_platform linux
        ;;
    "windows")
        echo "🪟 Building for Windows only..."
        build_platform windows
        ;;
    "macOS")
        echo "🍎 Building for macOS only..."
        build_platform macOS
        ;;
    "all")
        echo "🌐 Building for all platforms..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "📍 Running on Linux - building Linux AppImage"
            build_platform linux
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "📍 Running on macOS - building macOS package"
            build_platform macOS
        elif [[ "$OSTYPE" == "msys" ]]; then
            echo "📍 Running on Windows - building Windows installer"
            build_platform windows
        else
            echo "⚠️ Unknown platform, attempting Linux build"
            build_platform linux
        fi
        ;;
    *)
        echo "❌ Unknown platform: $1"
        echo "Supported platforms: linux, windows, macOS, all"
        exit 1
        ;;
esac

echo
echo "🎉 Build complete!"
echo
echo "📁 Built packages are in the 'dist/' directory"
echo "📋 For detailed instructions, see PACKAGING_GUIDE.md"
echo
echo "🚀 To distribute:"
echo "   - Linux: Share the .AppImage file"
echo "   - Windows: Share the .msi installer"  
echo "   - macOS: Share the .dmg package"