#!/bin/bash
# Install Docker buildx plugin

echo "🐳 Installing Docker buildx plugin..."
echo "======================================="

# Create the plugins directory
mkdir -p ~/.docker/cli-plugins

# Download the latest buildx plugin
echo "Downloading Docker buildx plugin..."
curl -SL https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64 \
     -o ~/.docker/cli-plugins/docker-buildx

# Make it executable
chmod +x ~/.docker/cli-plugins/docker-buildx

# Verify installation
echo "✅ Docker buildx installed successfully!"
echo ""
echo "🔍 Verifying installation:"
docker buildx version

echo ""
echo "📦 Ready to create AppImage with:"
echo "     .venv/bin/briefcase package linux appimage"