# 📦 GopiAI Packaging Guide

This guide explains how to package GopiAI for different platforms using Briefcase.

## 🛠️ Prerequisites

### Required System Dependencies

#### Ubuntu/Debian
```bash
sudo apt install libgirepository1.0-dev libglib2.0-0 libwebkit2gtk-4.1-dev \
                 libxcb-xinerama0 libxcb1 libx11-xcb1 libgirepository-1.0-1 \
                 libcairo-gobject2 libpango-1.0-0 libwebkit2gtk-4.1-0
```

#### Fedora/RHEL
```bash
sudo dnf install gobject-introspection-devel glib2-devel webkit2gtk4.1-devel \
                 libXinerama libxcb libX11-xcb gobject-introspection \
                 cairo-gobject-devel pango-devel webkit2gtk4.1
```

#### macOS
```bash
brew install cairo pango gdk-pixbuf libffi
```

## 📋 Package Configuration

The project is configured in `pyproject.toml` with the following structure:

- **Entry Point**: `src/gopiai_app/app.py`
- **Main Components**:
  - GopiAI-UI (Qt-based interface)
  - GopiAI-CrewAI (AI server backend)
  - GopiAI-Assets (icons, images)

## 🏗️ Building Packages

### 1. Linux (.AppImage)

```bash
# Install system dependencies first
sudo apt install libgirepository1.0-dev libglib2.0-0 libwebkit2gtk-4.1-dev

# Create Linux build
.venv/bin/briefcase create linux

# Build the package
.venv/bin/briefcase build linux

# Create AppImage
.venv/bin/briefcase package linux appimage
```

**Output**: `dist/GopiAI-1.0.0-x86_64.AppImage`

### 2. Windows (.exe)

```bash
# Create Windows build (requires Windows or cross-compilation)
.venv/bin/briefcase create windows

# Build the package
.venv/bin/briefcase build windows

# Create installer
.venv/bin/briefcase package windows msi
```

**Output**: `dist/GopiAI-1.0.0.msi`

### 3. macOS (.app/.dmg)

```bash
# Create macOS build (requires macOS)
.venv/bin/briefcase create macOS

# Build the package  
.venv/bin/briefcase build macOS

# Create DMG
.venv/bin/briefcase package macOS dmg
```

**Output**: `dist/GopiAI-1.0.0.dmg`

## 🔧 Development Workflow

### Test in Development Mode
```bash
# Test the app without packaging
.venv/bin/briefcase dev
```

### Update Existing Build
```bash
# Update sources in existing build
.venv/bin/briefcase update linux

# Build after updates
.venv/bin/briefcase build linux
```

## 📁 Project Structure for Packaging

```
GopiAI/
├── src/gopiai_app/          # Main app entry point
│   ├── __init__.py
│   └── app.py               # Briefcase entry point
├── GopiAI-UI/              # UI components
├── GopiAI-CrewAI/          # Backend server
├── GopiAI-Assets/          # Assets (icons, images)
├── pyproject.toml          # Packaging configuration
├── LICENSE                 # MIT License
└── PACKAGING_GUIDE.md      # This guide
```

## ⚙️ Configuration Details

### Key Configuration in pyproject.toml:
- **App Name**: GopiAI
- **Bundle ID**: com.gopiai
- **Version**: 1.0.0
- **License**: MIT
- **Dependencies**: PySide6, CrewAI, LiteLLM, Flask, etc.

### Platform-Specific Settings:
- **Linux**: Uses system GTK/WebKit dependencies
- **Windows**: Bundles required DLLs
- **macOS**: Code signing and notarization ready

## 🚨 Common Issues

### 1. System Dependencies Missing
**Error**: `Unable to build gopiai due to missing system dependencies`
**Solution**: Install the required system packages listed above

### 2. License Warning
**Error**: `WARNING: License Definition for the Project is Deprecated`
**Solution**: Already fixed - using `license = {file = "LICENSE"}`

### 3. Module Import Issues
**Error**: Python modules not found at runtime
**Solution**: Ensure all required modules are listed in `requires` section

### 4. Asset Path Issues  
**Error**: Icons/images not found in packaged app
**Solution**: Check `sources` paths in configuration

## 📊 Build Results

After successful packaging, you'll get:

| Platform | Output Format | Typical Size | Distribution |
|----------|---------------|--------------|--------------|
| Linux | .AppImage | 200-300MB | Single executable file |
| Windows | .msi/.exe | 150-250MB | Installer package |
| macOS | .app/.dmg | 200-300MB | Application bundle |

## 🔄 CI/CD Integration

For automated builds, use GitHub Actions:

```yaml
name: Build Packages
on: [push, release]
jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: sudo apt install libgirepository1.0-dev libglib2.0-0 libwebkit2gtk-4.1-dev
      - name: Build package
        run: |
          .venv/bin/briefcase create linux
          .venv/bin/briefcase build linux
          .venv/bin/briefcase package linux appimage
```

## 🎯 Next Steps

1. **Install system dependencies** (requires sudo)
2. **Run `briefcase create linux`** to setup build environment
3. **Build with `briefcase build linux`** 
4. **Package with `briefcase package linux appimage`**
5. **Test the generated .AppImage file**

The packaged application will be a standalone executable that includes all dependencies and can run on any compatible Linux system without requiring Python or other dependencies to be pre-installed.