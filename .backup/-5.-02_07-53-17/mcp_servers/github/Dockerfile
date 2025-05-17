FROM node:18-alpine

WORKDIR /app

# Установка зависимостей
RUN npm install -g @modelcontextprotocol/server-github

# Запуск сервера при старте контейнера
ENTRYPOINT ["npx", "@modelcontextprotocol/server-github"]
