import uvicorn

from app.web.api import app

if __name__ == "__main__":
    print("🚀 Запускаем веб-интерфейс GopiAI...")
    print("📱 Откройте в браузере: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
