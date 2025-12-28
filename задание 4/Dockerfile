FROM node:18-alpine

WORKDIR /app

# Копирование package.json и установка зависимостей
COPY package*.json ./
RUN npm install --production

# Копирование исходного кода
COPY proto/ ./proto/
COPY src/ ./src/

# Создание директории для БД
RUN mkdir -p /app/data

# Переменные окружения
ENV HOST=0.0.0.0
ENV PORT=50051

# Порт
EXPOSE 50051

# Запуск сервера
CMD ["node", "src/server.js"]

