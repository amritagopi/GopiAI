import litellm
import os

# Убедись, что GEMINI_API_KEY установлен в твоей системе
# os.environ["GEMINI_API_KEY"] = "ТВОЙ_КЛЮЧ_API"

# Получаем список моделей
models = litellm.model_list

# Фильтруем только Gemini модели
gemini_models = [m for m in models if m.startswith("gemini/")]

for model in gemini_models:
    print(model)
