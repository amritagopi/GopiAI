#!/bin/bash

# Batched dependency installer for GopiAI
# To be run after the virtual environment is created.

echo "--- Starting Batched Dependency Installation ---"

# Activate environment
source .venv/bin/activate

# Function to handle installation and check for errors
install_batch() {
    echo ""
    echo "--- Installing Batch: $1 ---"
    pip install --upgrade pip
    pip install $2
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install batch '$1'. Aborting."
        exit 1
    fi
}

# Batch 1: Core & GUI
install_batch "Core & GUI" "requests>=2.32.3 pyyaml>=6.0.1 python-dotenv>=1.0.1 colorama>=0.4.6 click>=8.1.7 rich>=13.7.1 PySide6==6.7.3 PySide6-Addons==6.7.3 PySide6-Essentials==6.7.3 shiboken6==6.7.3"

# Batch 2: Data Processing & Web
install_batch "Data & Web" "pandas>=2.2.1 numpy>=1.26.4 scipy>=1.13.0 scikit-learn>=1.4.1.post1 fastapi>=0.110.0 uvicorn>=0.27.1 httpx>=0.27.0"

# Batch 3: NLP & Spacy Models
install_batch "NLP & Spacy" "spacy>=3.8.7 pymorphy3>=2.0.4 pymorphy3-dicts-ru>=2.4.417150.4580142"
install_batch "Spacy Models" "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.8.0/ru_core_news_sm-3.8.0-py3-none-any.whl"

# Batch 4: AI & ML (Part 1 - LangChain & Foundational)
install_batch "AI & ML (LangChain)" "openai>=1.30.2 anthropic>=0.18.3 langchain>=0.1.12 langchain-openai>=0.0.8 langchain-anthropic>=0.1.3 langchain-google-genai>=0.0.8 langchain-community>=0.0.27 sentence-transformers>=2.7.0 tiktoken>=0.6.0"

# Batch 5: AI & ML (Part 2 - PyTorch & Transformers)
install_batch "AI & ML (Heavy)" "torch>=2.2.1 transformers>=4.38.2"

# Batch 6: Memory, Search, and the rest
install_batch "Memory & Search" "txtai>=8.2.0 faiss-cpu>=1.8.0 qdrant-client>=1.7.6"
install_batch "Remaining Tools & Utilities" "pytest>=8.0.2 pytest-qt>=4.2.0 jupyter>=1.0.0 jupyterlab>=4.1.5 soundfile>=0.12.1 sounddevice>=0.4.6 pydub>=0.25.1 noisereduce>=2.5.0 openai-whisper>=20231117 python-docx>=1.1.0 pypdf>=4.1.0 reportlab>=4.1.0 beautifulsoup4>=4.12.3 lxml>=5.1.0 selenium>=4.17.2 playwright>=1.41.2 webdriver-manager>=4.0.1 tqdm>=4.66.2 psutil>=5.9.8 python-dateutil>=2.9.0.post0 packaging>=23.2 chardet>=5.2.0"

echo ""
echo "--- All batches installed successfully! ---"

deactivate
