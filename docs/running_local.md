# Локальный запуск

## Требования

- Python 3.11+
- PostgreSQL 16+
- Webcam (для клиента)

## Сервер

### 1. Установка зависимостей

```bash
cd server
pip install -r requirements.txt
```

### 2. Настройка PostgreSQL

Docker:
```bash
docker run -d ^
  --name biometric-db ^
  -e POSTGRES_PASSWORD=password ^
  -e POSTGRES_DB=biometric_db ^
  -e POSTGRES_USER=biometric ^
  -p 5432:5432 ^
  postgres:16-alpine
```

### 3. Переменные окружения

```cmd
set DATABASE_URL=postgresql+asyncpg://biometric:password@localhost/biometric_db
set API_KEY=your-secret-key-2024
```

### 4. Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Проверка

```bash
curl -H "X-API-Key: your-secret-key-2024" http://localhost:8000/health
```

## Клиент

### 1. Установка зависимостей

```bash
cd client
pip install -r requirements.txt
```

### 2. Настройка .env

Отредактируйте `client/.env`:
```ini
SERVER_URL=http://localhost:8000
API_KEY=your-secret-key-2024
CAMERA_SOURCE=0
LOCK_DRIVER=dummy
```

### 3. Запуск

```bash
cd client
python -m app.main
```

## Docker (альтернатива)

### Сервер

```bash
cd server
docker compose up -d
```

### Клиент

```bash
cd client
docker build -t biometric-client .
docker run -it --rm -e DISPLAY=host.docker.internal:0 biometric-client
```

## Устранение проблем

### Ошибка: "No module named 'app'"

Добавьте путь в PYTHONPATH:
```cmd
set PYTHONPATH=%PYTHONPATH%;D:\Programs\it\Projects\Universitty\my-test\Macksim-project\server
```

### Ошибка подключения к PostgreSQL

Проверьте что PostgreSQL запущен:
```bash
docker ps | grep biometric-db
```

### Ошибка камеры

CAMERA_SOURCE=0 для первой камеры, 1 для второй и т.д.