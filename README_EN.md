# 🚀 GopiAI - Advanced AI Platform

![GopiAI Logo](GopiAI-Assets/gopiai/assets/GopiAI_LOGO.svg)

GopiAI is an advanced artificial intelligence platform featuring CrewAI agent orchestration with an intuitive Qt-based user interface. It provides seamless AI model rotation, intelligent task management, and a comprehensive toolkit for AI-powered automation.

## ✨ Features

### 🤖 **AI Agent Orchestration**
- **CrewAI Integration**: Advanced multi-agent coordination
- **Intelligent Task Distribution**: Automatic workload balancing
- **Agent Specialization**: Dedicated agents for different tasks

### 🔄 **Smart Model Management**
- **Automatic Model Rotation**: Intelligent switching between AI models
- **Rate Limit Handling**: Seamless quota management
- **Multi-Provider Support**: Gemini, OpenAI, and more

### 🖥️ **Modern User Interface**
- **Qt-Based GUI**: Clean, responsive interface
- **Real-Time Chat**: Interactive AI conversations
- **Dark/Light Themes**: Customizable appearance
- **Multi-Threading**: Smooth, non-blocking operations

### ⚡ **Production Ready**
- **Gunicorn WSGI Server**: Production-grade deployment
- **Comprehensive Logging**: Detailed monitoring and debugging
- **Error Recovery**: Robust fault tolerance
- **Cross-Platform**: Linux, Windows, macOS support

## 📦 Installation & Usage

### Quick Start (Development)
```bash
git clone https://github.com/amritagopi/GopiAI.git
cd GopiAI

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r GopiAI-UI/requirements_ui.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Start the application
./start_linux.sh
```

### Production Deployment
```bash
# Start production server
./GopiAI-CrewAI/start_production_server.sh

# Or use packaged applications (see below)
```

## 📦 Pre-Built Packages

GopiAI is available as standalone packages for easy installation:

### 🐧 **Linux (.AppImage)**
```bash
# Download and run (no installation required)
wget https://releases.gopiai.dev/GopiAI-1.0.0-x86_64.AppImage
chmod +x GopiAI-1.0.0-x86_64.AppImage
./GopiAI-1.0.0-x86_64.AppImage
```

### 🪟 **Windows (.exe/.msi)**
```bash
# Download installer
# https://releases.gopiai.dev/GopiAI-1.0.0.msi
# Double-click to install
```

### 🍎 **macOS (.dmg)**
```bash
# Download and mount
# https://releases.gopiai.dev/GopiAI-1.0.0.dmg
# Drag to Applications folder
```

## 🏗️ Building from Source

To build your own packages:

### Prerequisites
```bash
# Install Briefcase
pip install briefcase

# Linux dependencies
sudo apt install libgirepository1.0-dev libglib2.0-0 libwebkit2gtk-4.1-dev
```

### Build Commands
```bash
# Build for current platform
./build_packages.sh linux

# Build for all platforms
./build_packages.sh all
```

See [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) for detailed instructions.

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
BRAVE_API_KEY=your_brave_api_key
```

### Model Configuration
Configure AI models in `GopiAI-CrewAI/llm_rotation_config.py`:
```python
LLM_MODELS_CONFIG = [
    {
        "name": "Gemini 1.5 Flash",
        "id": "gemini/gemini-1.5-flash",
        "priority": 1,  # Higher priority = preferred
        "rpm": 2,       # Requests per minute
        # ... more config
    }
]
```

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GopiAI-UI     │    │  GopiAI-CrewAI   │    │ GopiAI-Assets   │
│                 │    │                  │    │                 │
│ • Qt Interface  │◄──►│ • Flask API      │    │ • Icons         │
│ • Chat Widget   │    │ • Agent Crews    │    │ • Images        │
│ • Settings      │    │ • Model Rotation │    │ • Themes        │
│ • Themes        │    │ • Tool Integr.   │    │ • Resources     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         └─────── HTTP API ───────┘
               (Port 5052)
```

## 🛠️ Development

### Project Structure
```
GopiAI/
├── src/gopiai_app/         # Briefcase entry point
├── GopiAI-UI/              # Qt-based user interface
│   └── gopiai/ui/          # UI components and logic
├── GopiAI-CrewAI/          # CrewAI backend server
│   ├── crews/              # Agent definitions
│   ├── tools/              # CrewAI tools
│   └── config/             # Configuration files
├── GopiAI-Assets/          # Shared assets
│   └── gopiai/assets/      # Icons, images, themes
├── pyproject.toml          # Packaging configuration
└── build_packages.sh       # Build script
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "unit"          # Unit tests only
pytest -m "integration"   # Integration tests
pytest -m "not slow"      # Skip slow tests
```

### Code Quality
```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📋 Requirements

### System Requirements
- **Python**: 3.10+ required
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB available space
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 11+

### Python Dependencies
- **PySide6**: Qt-based GUI framework
- **CrewAI**: Multi-agent orchestration
- **Flask**: Web server for API
- **LiteLLM**: Universal LLM interface
- **Requests**: HTTP client
- **Pydantic**: Data validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [GopiAI Wiki](https://github.com/amritagopi/GopiAI/wiki)
- **Issues**: [Bug Reports](https://github.com/amritagopi/GopiAI/issues)
- **Releases**: [Download Packages](https://github.com/amritagopi/GopiAI/releases)
- **Discussions**: [Community Forum](https://github.com/amritagopi/GopiAI/discussions)

## 🙏 Acknowledgments

- **CrewAI Team**: For the amazing agent orchestration framework
- **PySide Team**: For the excellent Qt Python bindings
- **BeeWare Team**: For Briefcase packaging tool
- **OpenAI & Google**: For AI model APIs
- **Community Contributors**: For feedback and improvements

---

**Made with ❤️ by the GopiAI Team**

*Empowering the future of AI-human collaboration*