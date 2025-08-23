"""Simplified Model Selector Widget with REST API Integration
----------------------------------
A lightweight replacement for the old gigantic widget.
Focuses on:
• Single QComboBox for provider selection.
• Dynamic model list from backend (llm_rotation_config).
• Single API-key input saved into .env under correct ENV-var.
• No duplicated signals; no separate buttons per provider.
• REST API integration for state synchronization.

Dependencies: PySide6, requests
"""
from __future__ import annotations

import os
import sys
import requests
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from gopiai.ui.utils.icon_helpers import create_icon_button

"""
Backend helpers
Robustly resolve import of llm_rotation_config located in GopiAI-CrewAI.
Handles various run contexts by falling back to direct file import.
"""
_repo_root = Path(__file__).resolve().parents[2]  # .../GopiAI-UI
_modules_root = _repo_root.parent                 # .../GOPI_AI_MODULES
crewai_dir = _modules_root / "GopiAI-CrewAI"

# Try regular import first
try:
    from llm_rotation_config import (  # type: ignore
        PROVIDER_KEY_ENV,
        get_api_key_for_provider,
        get_available_models,
    )
except Exception:
    # Ensure CrewAI dir is on sys.path and try again
    try:
        if str(crewai_dir) not in sys.path:
            sys.path.append(str(crewai_dir))
        from llm_rotation_config import (  # type: ignore
            PROVIDER_KEY_ENV,
            get_api_key_for_provider,
            get_available_models,
        )
    except Exception:
        # Final fallback: import module directly from file path
        llm_cfg_path = crewai_dir / "llm_rotation_config.py"
        if llm_cfg_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("llm_rotation_config", str(llm_cfg_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules["llm_rotation_config"] = mod
                spec.loader.exec_module(mod)
                PROVIDER_KEY_ENV = getattr(mod, "PROVIDER_KEY_ENV")
                get_api_key_for_provider = getattr(mod, "get_api_key_for_provider")
                get_available_models = getattr(mod, "get_available_models")
            else:
                raise ImportError(f"Cannot load llm_rotation_config from {llm_cfg_path}")
        else:
            raise ImportError("llm_rotation_config.py not found under GopiAI-CrewAI")

# Path to user .env


# Backend API base URL
from gopiai.ui.utils.network import get_crewai_server_base_url
BACKEND_BASE_URL = get_crewai_server_base_url()


class ModelSelectorWidget(QWidget):
    provider_changed = Signal(str)  # provider name
    model_changed = Signal(str)  # model id

    # ------------------------------------------------------------------
    # init
    # ------------------------------------------------------------------
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()
        self._wire_signals()
        self._populate_providers()
        # Load initial state from backend
        self._load_initial_state()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        main = QVBoxLayout(self)

        # Provider & API key
        self.provider_combo = QComboBox()
        self.api_key_edit = QLineEdit()
        # Use QLineEdit.EchoMode.Password for PySide6 type safety
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.save_key_btn = create_icon_button("key", "Сохранить API ключ")

        form = QFormLayout()
        form.addRow("Provider", self.provider_combo)
        form.addRow("API key", self.api_key_edit)
        form.addRow("", self.save_key_btn)
        main.addLayout(form)

        # Models
        self.model_combo = QComboBox()
        self.refresh_models_btn = create_icon_button("refresh-cw", "Обновить список моделей")
        hl = QHBoxLayout()
        hl.addWidget(self.model_combo, 1)
        hl.addWidget(self.refresh_models_btn)
        main.addLayout(hl)

        # Status
        self.status_lbl = QLabel()
        # Use Qt.AlignmentFlag.AlignLeft for PySide6 type safety
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main.addWidget(self.status_lbl)

    def _wire_signals(self) -> None:
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.save_key_btn.clicked.connect(self._save_key)
        self.refresh_models_btn.clicked.connect(self._reload_models)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)

    # ------------------------------------------------------------------
    # state handling
    # ------------------------------------------------------------------
    def _load_initial_state(self):
        """Load initial state from backend API."""
        try:
            response = requests.get(f"{BACKEND_BASE_URL}/internal/state", timeout=5)
            if response.status_code == 200:
                state = response.json()
                provider = state.get("provider", "gemini")
                model_id = state.get("model_id", "")
                
                # Set provider in combo box
                index = self.provider_combo.findText(provider)
                if index >= 0:
                    self.provider_combo.setCurrentIndex(index)
                
                # Load models for this provider
                self._reload_models()
                
                # Set model in combo box if available
                if model_id:
                    for i in range(self.model_combo.count()):
                        if self.model_combo.itemData(i) == model_id:
                            self.model_combo.setCurrentIndex(i)
                            break
                            
        except Exception as e:
            print(f"[WARNING] Could not load initial state from backend: {e}")
            # Fall back to default behavior
            self._on_provider_changed(self.provider_combo.currentText())

    # ------------------------------------------------------------------
    # provider handling
    # ------------------------------------------------------------------
    def _populate_providers(self):
        self.provider_combo.clear()
        for prov in PROVIDER_KEY_ENV.keys():
            self.provider_combo.addItem(prov)
        # trigger initial load
        self._on_provider_changed(self.provider_combo.currentText())

    def _on_provider_changed(self, provider: str):
        # fill api key field
        current_key = get_api_key_for_provider(provider) or ""
        self.api_key_edit.setText(current_key)
        self._reload_models()
        self.provider_changed.emit(provider)
        
        # Notify backend about provider change
        try:
            current_model_id = self.model_combo.currentData()
            if current_model_id:
                requests.post(f"{BACKEND_BASE_URL}/internal/state", 
                            json={"provider": provider, "model_id": current_model_id},
                            timeout=5)
        except Exception as e:
            print(f"[WARNING] Could not notify backend about provider change: {e}")

    # ------------------------------------------------------------------
    # model handling
    # ------------------------------------------------------------------
    def _reload_models(self):
        provider = self.provider_combo.currentText()
        
        try:
            # Try to get models from backend API first
            response = requests.get(f"{BACKEND_BASE_URL}/internal/models?provider={provider}", timeout=5)
            if response.status_code == 200:
                models = response.json()
            else:
                # Fall back to local backend helpers
                models = [m for m in get_available_models("dialog") if m["provider"] == provider]
        except Exception as e:
            print(f"[WARNING] Could not fetch models from backend API: {e}")
            # Fall back to local backend helpers
            models = [m for m in get_available_models("dialog") if m["provider"] == provider]
        
        self.model_combo.clear()
        for m in models:
            self.model_combo.addItem(m["display_name"], m["id"])
        if not models:
            self.model_combo.addItem("<no available models>")
        self.status_lbl.setText(f"{len(models)} models loaded for {provider}.")

    def _on_model_changed(self, display_name: str):
        model_id = self.model_combo.currentData()
        if model_id:
            self.model_changed.emit(model_id)
            
            # Notify backend about model change
            provider = self.provider_combo.currentText()
            try:
                requests.post(f"{BACKEND_BASE_URL}/internal/state", 
                            json={"provider": provider, "model_id": model_id},
                            timeout=5)
            except Exception as e:
                print(f"[WARNING] Could not notify backend about model change: {e}")

    # ------------------------------------------------------------------
    # env helpers
    # ------------------------------------------------------------------
    def _save_key(self):
        provider = self.provider_combo.currentText()
        env_var = PROVIDER_KEY_ENV[provider]
        key_val = self.api_key_edit.text().strip()

        if not key_val:
            QMessageBox.warning(self, "Empty key", "Please enter a value")
            return

        # Ensure .env exists
        if not ENV_PATH.exists():
            ENV_PATH.write_text("")

        # Read current content
        content = ENV_PATH.read_text().splitlines()
        
        # Remove any existing lines with this env var
        new_lines: list[str] = []
        for line in content:
            if not line.startswith(f"{env_var}="):
                new_lines.append(line)
        
        # Add the new key
        new_lines.append(f"{env_var}={key_val}")
        
        # Write back to file
        ENV_PATH.write_text("\n".join(new_lines) + "\n")
        self.status_lbl.setText(f"Saved {env_var} to .env → restart backend to apply.")


# Convenience for manual run
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = ModelSelectorWidget()
    w.setWindowTitle("Model Selector Test")
    w.resize(400, 200)
    w.show()
    sys.exit(app.exec())
