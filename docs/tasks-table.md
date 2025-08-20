# ModelSwitchRefactor
Refactor backend and frontend to support stable provider switching between Gemini and OpenRouter

> ## 📈 Project Summary
> 
> **✅ Done**: 4 | **🔄 In Progress**: 0 | **⬜ Todo**: 5 | **❌ Blocked**: 0
> 
> **Progress**: 44% `█████████░░░░░░░░░░░` 4/9 tasks
> 
> **Priorities**: 🚨 **Critical**: 0 | 🔴 **High**: 4 | 🟡 **Medium**: 5 | 🟢 **Low**: 0

## Tasks

| ID | Status | Priority | Title | Description |
|:--:|:------:|:--------:|:------|:------------|
| #1 | ⬜ todo | 700 | **Project Setup: ModelSwitchRefactor** | Refactor backend and frontend... |
| #2 | ✅ done | 701 | **Refactor backend llm_rotation_config.py to support OpenRouter and remove duplicates** | Add OpenRouter provider suppo... |
| #3 | ✅ done | 699 | **Refactor model_selector_widget.py to single-provider dropdown and remove duplicate signals** | Frontend widget should:
- Pre... |
| #4 | ✅ done | 702 | **Implement provider/model state file synchronization** | Create ~/.gopiai_state.json s... |


### Task #2: Refactor backend llm_rotation_config.py to support OpenRouter and remove duplicates - Subtasks

| ID | Status | Title |
|:--:|:------:|:------|
| #2.1 | ✅ done | Introduce PROVIDERS dict with Gemini and OpenRouter models |
| #2.2 | ✅ done | Create UsageTracker class and replace scattered usage dicts |

### Task #3: Refactor model_selector_widget.py to single-provider dropdown and remove duplicate signals - Subtasks

| ID | Status | Title |
|:--:|:------:|:------|
| #3.1 | ✅ done | Replace two provider buttons with QComboBox |
| #3.2 | ✅ done | Refactor model loading to use get_available_models |
| #3.3 | ✅ done | Unify API key handling and save to .env |
