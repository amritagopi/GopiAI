# Автоматическая установка всех модулей GopiAI в правильном порядке

echo "🚀 Установка модулей GopiAI"
echo "=" * 50

# Устанавливаем модули в порядке зависимостей

echo "📦 Устанавливаем GopiAI-Core..."
cd GopiAI-Core
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-Core установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-Core"
    exit 1
fi
cd ..

echo "📦 Устанавливаем GopiAI-Widgets..."
cd GopiAI-Widgets
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-Widgets установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-Widgets"
    exit 1
fi
cd ..

echo "📦 Устанавливаем GopiAI-UI..."
cd GopiAI-UI
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-UI установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-UI"
    exit 1
fi
cd ..

echo "📦 Устанавливаем GopiAI-Extensions..."
cd GopiAI-Extensions
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-Extensions установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-Extensions"
    exit 1
fi
cd ..

echo "📦 Устанавливаем GopiAI-Extensions..."
cd GopiAI-Extensions
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-Extensions установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-Extensions"
    exit 1
fi
cd ..

echo "📦 Устанавливаем GopiAI-App..."
cd GopiAI-App
pip install -e .
if [ $? -eq 0 ]; then
    echo "✅ GopiAI-App установлен успешно"
else
    echo "❌ Ошибка установки GopiAI-App"
    exit 1
fi
cd ..

echo ""
echo "🎉 Все модули установлены!"
echo "Теперь можно запускать:"
echo "python GopiAI-UI/gopiai/ui/main.py"
