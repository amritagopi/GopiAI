#!/bin/bash
# Install missing development packages for Linux Mint 22.1/Ubuntu 24.04
# This script installs the packages needed for Briefcase Linux builds

echo "🔧 Installing Linux development dependencies for GopiAI packaging..."
echo "==============================================================="

# Install the missing packages without the conflicting libglib2.0-0
echo "Installing libgirepository1.0-dev, libgirepository-2.0-dev, and libwebkit2gtk-4.1-dev..."
sudo apt update
sudo apt install -y libgirepository1.0-dev libgirepository-2.0-dev libwebkit2gtk-4.1-dev

echo "✅ Dependencies installed successfully!"
echo ""
echo "📦 Ready to build Linux package with:"
echo "     ./build_packages.sh linux"