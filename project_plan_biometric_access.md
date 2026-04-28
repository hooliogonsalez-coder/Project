# План разработки: Система биометрического контроля доступа

> **Версия:** 1.0  
> **Стек:** FastAPI · PostgreSQL · CustomTkinter · InsightFace · SQLite · Docker  
> **Архитектура:** Сервер (Python-бэкенд) + Универсальное десктопное приложение  

---

## Содержание

1. [Подготовка среды и репозитория](#этап-1-подготовка-среды-и-репозитория)
2. [Серверная часть — ядро](#этап-2-серверная-часть--ядро)
3. [Десктопное приложение — GUI и камера](#этап-3-десктопное-приложение--gui-и-камера)
4. [Биометрическое ядро](#этап-4-биометрическое-ядро)
5. [Режим Администратора](#этап-5-режим-администратора)
6. [Режим Терминала](#этап-6-режим-терминала)
7. [Интеграция с замками](#этап-7-интеграция-с-замками)
8. [Офлайн-режим и синхронизация](#этап-8-офлайн-режим-и-синхронизация)
9. [Безопасность](#этап-9-безопасность)
10. [Тестирование](#этап-10-тестирование)
11. [Упаковка и развёртывание](#этап-11-упаковка-и-развёртывание)

---

## Этап 1. Подготовка среды и репозитория

### 1.1 Структура репозитория

```
biometric-access/
├── server/                   # FastAPI бэкенд
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py         # Settings через pydantic-settings
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── employee.py
│   │   │   └── room.py
│   │   ├── schemas/          # Pydantic-схемы запросов/ответов
│   │   │   ├── employee.py
│   │   │   └── room.py
│   │   ├── routers/
│   │   │   ├── employees.py
│   │   │   └── rooms.py
│   │   ├── services/
│   │   │   ├── crypto.py     # Шифрование face_embedding
│   │   │   └── sync.py       # Логика синхронизации
│   │   └── middleware/
│   │       └── auth.py       # API-key middleware
│   ├── alembic/              # Миграции БД
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── client/                   # Десктопное приложение
│   ├── app/
│   │   ├── main.py           # Точка входа
│   │   ├── config.py         # .env конфигурация
│   │   ├── gui/
│   │   │   ├── main_window.py
│   │   │   ├── admin/
│   │   │   │   ├── employees_tab.py
│   │   │   │   ├── rooms_tab.py
│   │   │   │   └── register_form.py
│   │   │   └── terminal/
│   │   │       └── terminal_view.py
│   │   ├── core/
│   │   │   ├── camera.py     # Захват видео (OpenCV)
│   │   │   ├── biometric.py  # InsightFace wrapper
│   │   │   ├── db.py         # SQLite (SQLCipher) локальная БД
│   │   │   ├── api_client.py # httpx клиент
│   │   │   ├── room_manager.py # In-memory занятость кабинетов
│   │   │   └── lock_driver.py  # Абстрактный драйвер замка
│   │   ├── drivers/          # Конкретные реализации замков
│   │   │   ├── http_lock.py
│   │   │   ├── modbus_lock.py
│   │   │   └── mqtt_lock.py
│   │   └── utils/
│   │       └── crypto.py
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
│
├── docs/
│   ├── admin_manual.md
│   └── terminal_manual.md
└── README.md
```

### 1.2 Зависимости

**server/requirements.txt:**
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.0
pydantic-settings==2.4.0
cryptography==43.0.0
python-jose[cryptography]==3.3.0
httpx==0.27.0
loguru==0.7.2
```

**client/requirements.txt:**
```
customtkinter==5.2.2
opencv-python==4.10.0.84
insightface==0.7.3
onnxruntime==1.19.0
numpy==1.26.4
faiss-cpu==1.8.0
httpx==0.27.0
sqlcipher3==0.5.3
cryptography==43.0.0
python-dotenv==1.0.1
loguru==0.7.2
pyserial==3.5         # для Modbus
paho-mqtt==2.1.0      # для MQTT
```

### 1.3 Конфигурация через .env

**client/.env.example:**
```ini
# Сервер
SERVER_URL=https://your-server.local
API_KEY=your-secret-api-key

# Биометрия
FACE_RECOGNITION_THRESHOLD=0.50   # cosine similarity порог
FACE_MODEL=buffalo_l               # InsightFace модель

# Камера
CAMERA_SOURCE=0                    # 0 = USB, или rtsp://...
CAMERA_FPS=15

# Кабинеты
ROOM_TIMEOUT_MINUTES=480           # авто-освобождение через N минут

# БД
SQLITE_DB_PATH=./data/local.db
SQLITE_KEY=change-me-in-production

# Замок
LOCK_DRIVER=http                   # http | modbus | mqtt | gpio
LOCK_HTTP_URL=http://192.168.1.10/lock

# Логирование
LOG_LEVEL=INFO
LOG_FILE=./logs/client.log
```

### 1.4 Git-стратегия

- `main` — стабильная ветка, только через PR
- `develop` — основная ветка разработки
- Ветки фич: `feature/admin-gui`, `feature/biometric-core` и т.д.
- Коммиты по стандарту Conventional Commits: `feat:`, `fix:`, `chore:`

---

## Этап 2. Серверная часть — ядро

### 2.1 Схема базы данных (PostgreSQL)

```sql
-- server/alembic/versions/001_initial.py

CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    surname       VARCHAR(100) NOT NULL,
    department    VARCHAR(200),
    position      VARCHAR(200),
    face_embedding BYTEA NOT NULL,       -- AES-256-GCM зашифрованный вектор
    created_at    TIMESTAMP DEFAULT NOW(),
    updated_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rooms (
    id          SERIAL PRIMARY KEY,
    room_number VARCHAR(50)  NOT NULL UNIQUE,
    description TEXT,
    is_active   SMALLINT     NOT NULL DEFAULT 1,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### 2.2 SQLAlchemy модели

```python
# server/app/models/employee.py
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    id            = Column(Integer, primary_key=True)
    name          = Column(String(100), nullable=False)
    surname       = Column(String(100), nullable=False)
    department    = Column(String(200))
    position      = Column(String(200))
    face_embedding = Column(LargeBinary, nullable=False)  # зашифровано
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 2.3 Pydantic-схемы с сериализацией embedding'ов

```python
# server/app/schemas/employee.py
import base64
from pydantic import BaseModel, field_validator

class EmployeeCreate(BaseModel):
    name: str
    surname: str
    department: str | None
    position: str | None
    face_embedding_b64: str  # base64(AES-GCM(float32 numpy array))

    @field_validator("face_embedding_b64")
    @classmethod
    def validate_embedding(cls, v: str) -> str:
        try:
            data = base64.b64decode(v)
            assert len(data) > 32, "Embedding слишком мал"
        except Exception:
            raise ValueError("Некорректный face_embedding")
        return v

class EmployeeOut(BaseModel):
    id: int
    name: str
    surname: str
    department: str | None
    position: str | None
    face_embedding_b64: str
    updated_at: str

    model_config = {"from_attributes": True}
```

### 2.4 REST API роутеры

```python
# server/app/routers/employees.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut
import base64

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("/", response_model=list[EmployeeOut])
async def list_employees(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Employee))
    return result.scalars().all()

@router.post("/", response_model=EmployeeOut, status_code=201)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_session)):
    emp = Employee(
        name=data.name,
        surname=data.surname,
        department=data.department,
        position=data.position,
        face_embedding=base64.b64decode(data.face_embedding_b64),
    )
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp

@router.put("/{emp_id}", response_model=EmployeeOut)
async def update_employee(emp_id: int, data: EmployeeCreate, db: AsyncSession = Depends(get_session)):
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404, "Сотрудник не найден")
    for field, value in data.model_dump().items():
        setattr(emp, field, value)
    await db.commit()
    return emp

@router.delete("/{emp_id}", status_code=204)
async def delete_employee(emp_id: int, db: AsyncSession = Depends(get_session)):
    emp = await db.get(Employee, emp_id)
    if not emp:
        raise HTTPException(404)
    await db.delete(emp)
    await db.commit()
```

**Аналогичный роутер создаётся для `/api/rooms`.**

### 2.5 API-key аутентификация

```python
# server/app/middleware/auth.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(key: str = Security(api_key_header)):
    if key != settings.API_KEY:
        raise HTTPException(403, "Неверный API-ключ")
```

### 2.6 Синхронизация (POST /api/sync)

Эндпоинт принимает `since` (ISO timestamp) и возвращает только изменившиеся записи:

```python
@router.post("/api/sync")
async def sync(since: str, db: AsyncSession = Depends(get_session)):
    since_dt = datetime.fromisoformat(since)
    employees = await db.execute(
        select(Employee).where(Employee.updated_at > since_dt)
    )
    rooms = await db.execute(
        select(Room).where(Room.updated_at > since_dt)
    )
    return {
        "employees": employees.scalars().all(),
        "rooms": rooms.scalars().all(),
        "server_time": datetime.utcnow().isoformat(),
    }
```

### 2.7 Docker-конфигурация сервера

```yaml
# server/docker-compose.yml
version: "3.9"
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: biometric_db
      POSTGRES_USER: biometric
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "443:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://biometric:${DB_PASSWORD}@db/biometric_db
      API_KEY: ${API_KEY}
    depends_on:
      - db
    volumes:
      - ./certs:/certs

volumes:
  pgdata:
```

---

## Этап 3. Десктопное приложение — GUI и камера

### 3.1 Главное окно с переключением режимов

```python
# client/app/gui/main_window.py
import customtkinter as ctk
from app.gui.admin.employees_tab import EmployeesTab
from app.gui.terminal.terminal_view import TerminalView

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Система контроля доступа")
        self.geometry("1280x800")
        self._current_mode = None
        self._build_mode_selector()

    def _build_mode_selector(self):
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkButton(frame, text="Режим администратора",
                      command=self._open_admin).pack(pady=10)
        ctk.CTkButton(frame, text="Режим терминала",
                      command=self._open_terminal).pack(pady=10)

    def _open_admin(self):
        pwd = ctk.CTkInputDialog(text="Введите пароль:", title="Администратор")
        if pwd.get_input() == settings.ADMIN_PASSWORD:
            self._switch_to(AdminView(self))

    def _open_terminal(self):
        self._switch_to(TerminalView(self))

    def _switch_to(self, view):
        if self._current_mode:
            self._current_mode.destroy()
        self._current_mode = view
        view.pack(fill="both", expand=True)
```

### 3.2 Захват видеопотока в отдельном потоке

```python
# client/app/core/camera.py
import threading
import queue
import cv2

class CameraThread(threading.Thread):
    def __init__(self, source=0, fps=15):
        super().__init__(daemon=True)
        self.source = source
        self.fps = fps
        self.frame_queue = queue.Queue(maxsize=2)
        self._stop_event = threading.Event()

    def run(self):
        cap = cv2.VideoCapture(self.source)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        while not self._stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()  # сбрасываем старый кадр
                self.frame_queue.put(frame)
        cap.release()

    def get_frame(self):
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._stop_event.set()
```

### 3.3 Отображение видеопотока в CustomTkinter

```python
# client/app/gui/terminal/terminal_view.py
from PIL import Image, ImageTk
import customtkinter as ctk
import cv2

class TerminalView(ctk.CTkFrame):
    REFRESH_MS = 67  # ~15 fps

    def __init__(self, master):
        super().__init__(master)
        self.camera = CameraThread(source=settings.CAMERA_SOURCE)
        self.camera.start()
        self._canvas = ctk.CTkLabel(self, text="")
        self._canvas.pack(fill="both", expand=True)
        self._status = ctk.CTkLabel(self, text="Ожидание лица...", font=("Arial", 24))
        self._status.pack()
        self._update_frame()

    def _update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(img))
            self._canvas.configure(image=photo)
            self._canvas.image = photo
        self.after(self.REFRESH_MS, self._update_frame)

    def destroy(self):
        self.camera.stop()
        super().destroy()
```

### 3.4 Локальная SQLite база

```python
# client/app/core/db.py
import sqlite3

def get_connection(db_path: str, key: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(f"PRAGMA key='{key}'")       # SQLCipher шифрование
    conn.execute("PRAGMA journal_mode=WAL")   # производительность
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id              INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            surname         TEXT NOT NULL,
            department      TEXT,
            position        TEXT,
            face_embedding  BLOB NOT NULL,
            updated_at      TEXT
        );
        CREATE TABLE IF NOT EXISTS rooms (
            id          INTEGER PRIMARY KEY,
            room_number TEXT NOT NULL UNIQUE,
            description TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1,
            updated_at  TEXT
        );
        CREATE TABLE IF NOT EXISTS sync_meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    conn.commit()
```

---

## Этап 4. Биометрическое ядро

### 4.1 InsightFace обёртка

```python
# client/app/core/biometric.py
import numpy as np
import insightface
from insightface.app import FaceAnalysis

class FaceRecognizer:
    def __init__(self, model_name="buffalo_l", threshold=0.50):
        self.app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.threshold = threshold
        self._embeddings: list[tuple[int, np.ndarray]] = []  # (employee_id, vector)

    def load_from_db(self, employees: list[dict]):
        """Загружает эмбеддинги из локальной БД в оперативную память."""
        self._embeddings = []
        for emp in employees:
            raw = emp["face_embedding"]       # bytes (расшифровано)
            vec = np.frombuffer(raw, dtype=np.float32)
            self._embeddings.append((emp["id"], vec))

    def detect_and_embed(self, frame: np.ndarray) -> np.ndarray | None:
        """Возвращает embedding первого найденного лица или None."""
        faces = self.app.get(frame)
        if not faces:
            return None
        # Берём лицо с наибольшей площадью bbox
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        return face.normed_embedding  # уже нормализованный float32 вектор

    def identify(self, embedding: np.ndarray) -> int | None:
        """Возвращает employee_id ближайшего совпадения или None."""
        if not self._embeddings:
            return None
        ids, vecs = zip(*self._embeddings)
        matrix = np.stack(vecs)  # (N, 512)
        scores = matrix @ embedding  # cosine similarity (вектора нормализованы)
        best_idx = int(np.argmax(scores))
        if scores[best_idx] >= self.threshold:
            return ids[best_idx]
        return None

    def capture_template(self, frames: list[np.ndarray]) -> np.ndarray | None:
        """
        Регистрация: захватывает несколько кадров, усредняет embedding.
        Возвращает финальный нормализованный вектор или None при ошибке.
        """
        embeddings = []
        for frame in frames:
            emb = self.detect_and_embed(frame)
            if emb is not None:
                embeddings.append(emb)
        if len(embeddings) < 3:
            return None
        mean_emb = np.mean(embeddings, axis=0)
        return mean_emb / np.linalg.norm(mean_emb)  # нормализация
```

### 4.2 Шифрование embedding'ов

```python
# client/app/utils/crypto.py
import os
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EmbeddingCrypto:
    def __init__(self, key_hex: str):
        # key_hex — 64 hex-символа = 32 байта (AES-256)
        self.key = bytes.fromhex(key_hex)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, embedding: np.ndarray) -> bytes:
        plaintext = embedding.astype(np.float32).tobytes()
        nonce = os.urandom(12)  # 96-bit nonce для GCM
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext  # nonce || ciphertext || tag

    def decrypt(self, data: bytes) -> np.ndarray:
        nonce, ciphertext = data[:12], data[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return np.frombuffer(plaintext, dtype=np.float32)
```

### 4.3 Liveness-проверка (базовая)

```python
# client/app/core/biometric.py (дополнение)
def check_liveness(self, frame: np.ndarray, face) -> bool:
    """
    Базовая anti-spoofing проверка через InsightFace.
    Возвращает True если лицо — живое.
    """
    # InsightFace buffalo_l включает модель 2D106det + anti-spoof
    # score > 0.5 — живое, < 0.5 — фото/маска
    if hasattr(face, "det_score") and face.det_score < 0.85:
        return False  # низкая уверенность детекции
    # При наличии anti-spoof модели в пакете:
    try:
        spoof_score = face.spoof_score if hasattr(face, "spoof_score") else 1.0
        return spoof_score > 0.5
    except Exception:
        return True  # при отсутствии модели — пропускаем
```

---

## Этап 5. Режим Администратора

### 5.1 Вкладки интерфейса

```
AdminView
├── CTkTabview
│   ├── "Сотрудники"     → EmployeesTab
│   ├── "Кабинеты"       → RoomsTab
│   └── "Синхронизация"  → SyncTab
└── Панель статуса
```

### 5.2 Форма регистрации сотрудника

```python
# client/app/gui/admin/register_form.py
class RegisterForm(ctk.CTkToplevel):
    CAPTURE_FRAMES = 10   # кол-во кадров для усреднения

    def __init__(self, master, biometric: FaceRecognizer, db, api_client):
        super().__init__(master)
        self.title("Новый сотрудник")
        self._biometric = biometric
        self._db = db
        self._api = api_client
        self._captured_frames = []
        self._build_ui()

    def _build_ui(self):
        # Левая колонка — видеопросмотр
        self._video_label = ctk.CTkLabel(self, text="")
        self._video_label.grid(row=0, column=0, padx=10, pady=10)

        # Правая колонка — поля формы
        fields = ctk.CTkFrame(self)
        fields.grid(row=0, column=1, padx=10)
        self._name_entry     = ctk.CTkEntry(fields, placeholder_text="Имя")
        self._surname_entry  = ctk.CTkEntry(fields, placeholder_text="Фамилия")
        self._dept_entry     = ctk.CTkEntry(fields, placeholder_text="Подразделение")
        self._pos_entry      = ctk.CTkEntry(fields, placeholder_text="Должность")
        for w in [self._name_entry, self._surname_entry, self._dept_entry, self._pos_entry]:
            w.pack(pady=5)

        # Кнопки
        ctk.CTkButton(self, text="Захватить лицо", command=self._capture).grid(row=1, column=0)
        ctk.CTkButton(self, text="Сохранить", command=self._save).grid(row=1, column=1)
        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.grid(row=2, columnspan=2)

    def _capture(self):
        """Захватывает N кадров для построения шаблона."""
        self._captured_frames = []
        self._status_label.configure(text="Смотрите в камеру...")
        self._do_capture()

    def _do_capture(self):
        frame = self.master.camera.get_frame()
        if frame is not None:
            self._captured_frames.append(frame)
        if len(self._captured_frames) < self.CAPTURE_FRAMES:
            self.after(100, self._do_capture)
        else:
            self._status_label.configure(
                text=f"Захвачено {len(self._captured_frames)} кадров ✓"
            )

    def _save(self):
        embedding = self._biometric.capture_template(self._captured_frames)
        if embedding is None:
            self._status_label.configure(text="Ошибка: лицо не обнаружено")
            return
        # Шифруем и сохраняем
        crypto = EmbeddingCrypto(settings.EMBEDDING_KEY)
        encrypted = crypto.encrypt(embedding)
        employee_data = {
            "name":       self._name_entry.get(),
            "surname":    self._surname_entry.get(),
            "department": self._dept_entry.get(),
            "position":   self._pos_entry.get(),
            "face_embedding": encrypted,
        }
        # Сохранение локально + отправка на сервер
        threading.Thread(target=self._save_async, args=(employee_data,), daemon=True).start()

    def _save_async(self, data):
        # 1. Локальная БД
        self._db.save_employee(data)
        # 2. Сервер
        try:
            self._api.post("/api/employees", data)
            self.after(0, lambda: self._status_label.configure(text="Сохранено ✓"))
        except Exception as e:
            self.after(0, lambda: self._status_label.configure(text=f"Ошибка сервера: {e}"))
```

### 5.3 Синхронизация с сервером

```python
# client/app/core/api_client.py
import httpx
import base64
from app.config import settings

class APIClient:
    def __init__(self):
        self._client = httpx.Client(
            base_url=settings.SERVER_URL,
            headers={"X-API-Key": settings.API_KEY},
            verify=True,     # True для production (Let's Encrypt)
            timeout=10.0,
        )

    def sync(self, since: str) -> dict:
        resp = self._client.post("/api/sync", json={"since": since})
        resp.raise_for_status()
        return resp.json()

    def full_sync(self) -> dict:
        """Полная синхронизация при первом запуске."""
        employees = self._client.get("/api/employees").json()
        rooms = self._client.get("/api/rooms").json()
        return {"employees": employees, "rooms": rooms}
```

---

## Этап 6. Режим Терминала

### 6.1 Менеджер занятости кабинетов (in-memory)

```python
# client/app/core/room_manager.py
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RoomOccupancy:
    room_id: int
    room_number: str
    employee_id: int
    assigned_at: float = field(default_factory=time.time)

class RoomManager:
    def __init__(self, timeout_minutes: int = 480):
        self._lock = threading.Lock()
        self._rooms: dict[int, dict]        = {}   # room_id → room_data
        self._occupied: dict[int, RoomOccupancy] = {}  # room_id → occupancy
        self._employee_room: dict[int, int]  = {}  # employee_id → room_id
        self.timeout_seconds = timeout_minutes * 60

    def load_rooms(self, rooms: list[dict]):
        """Загружает список активных кабинетов из БД. Все помечаются свободными."""
        with self._lock:
            self._rooms = {r["id"]: r for r in rooms if r["is_active"] == 1}
            self._occupied.clear()
            self._employee_room.clear()

    def assign(self, employee_id: int) -> Optional[dict]:
        """Назначает свободный кабинет сотруднику. Возвращает room_data или None."""
        with self._lock:
            if employee_id in self._employee_room:
                # Сотрудник уже имеет кабинет — возвращаем
                room_id = self._employee_room[employee_id]
                return self._rooms.get(room_id)

            free_rooms = [
                r for rid, r in self._rooms.items()
                if rid not in self._occupied
            ]
            if not free_rooms:
                return None

            room = min(free_rooms, key=lambda r: r["room_number"])
            self._occupied[room["id"]] = RoomOccupancy(
                room_id=room["id"],
                room_number=room["room_number"],
                employee_id=employee_id,
            )
            self._employee_room[employee_id] = room["id"]
            return room

    def release_by_employee(self, employee_id: int) -> bool:
        """Освобождает кабинет сотрудника (повторное предъявление лица)."""
        with self._lock:
            room_id = self._employee_room.pop(employee_id, None)
            if room_id is None:
                return False
            self._occupied.pop(room_id, None)
            return True

    def release_by_room(self, room_id: int):
        """Ручное освобождение администратором."""
        with self._lock:
            occ = self._occupied.pop(room_id, None)
            if occ:
                self._employee_room.pop(occ.employee_id, None)

    def auto_release_expired(self):
        """Вызывается по таймеру — освобождает просроченные кабинеты."""
        now = time.time()
        with self._lock:
            expired = [
                rid for rid, occ in self._occupied.items()
                if now - occ.assigned_at > self.timeout_seconds
            ]
            for rid in expired:
                occ = self._occupied.pop(rid)
                self._employee_room.pop(occ.employee_id, None)

    def get_status(self) -> list[dict]:
        """Возвращает статус всех активных кабинетов для отображения."""
        with self._lock:
            result = []
            for rid, room in self._rooms.items():
                occ = self._occupied.get(rid)
                result.append({
                    "room_number": room["room_number"],
                    "occupied": occ is not None,
                    "employee_id": occ.employee_id if occ else None,
                })
            return result
```

### 6.2 Основной цикл терминала

```python
# client/app/gui/terminal/terminal_view.py (расширение)

class TerminalView(ctk.CTkFrame):
    RECOGNITION_INTERVAL_MS = 500   # распознавание раз в 0.5 сек

    def __init__(self, master, biometric, room_manager, lock_driver, db):
        super().__init__(master)
        self._biometric = biometric
        self._rooms = room_manager
        self._lock = lock_driver
        self._db = db
        self._last_employee_id: int | None = None
        self._build_ui()
        self._recognition_thread = None
        self._schedule_recognition()

    def _schedule_recognition(self):
        threading.Thread(target=self._recognition_loop, daemon=True).start()

    def _recognition_loop(self):
        while True:
            frame = self.master.camera.get_frame()
            if frame is not None:
                self._process_frame(frame)
            time.sleep(self.RECOGNITION_INTERVAL_MS / 1000)

    def _process_frame(self, frame):
        embedding = self._biometric.detect_and_embed(frame)
        if embedding is None:
            self.after(0, lambda: self._status.configure(text="Ожидание лица..."))
            return

        employee_id = self._biometric.identify(embedding)
        if employee_id is None:
            self.after(0, lambda: self._status.configure(text="Неизвестный сотрудник"))
            return

        employee = self._db.get_employee(employee_id)
        full_name = f"{employee['surname']} {employee['name']}"

        # Проверяем: сотрудник уже имеет кабинет → возврат ключа
        if self._rooms._employee_room.get(employee_id):
            self._rooms.release_by_employee(employee_id)
            self.after(0, lambda: self._status.configure(
                text=f"{full_name} — ключ возвращён ✓"
            ))
            return

        # Назначаем кабинет
        room = self._rooms.assign(employee_id)
        if room is None:
            self.after(0, lambda: self._status.configure(text="Нет свободных кабинетов"))
            return

        # Открываем замок
        threading.Thread(
            target=self._lock.open, args=(room["room_number"],), daemon=True
        ).start()

        self.after(0, lambda: self._status.configure(
            text=f"{full_name} → Кабинет {room['room_number']} ✓"
        ))
        self.after(0, self._update_room_table)
```

---

## Этап 7. Интеграция с замками

### 7.1 Абстрактный базовый класс

```python
# client/app/core/lock_driver.py
from abc import ABC, abstractmethod

class LockDriver(ABC):
    @abstractmethod
    def open(self, room_id: str) -> bool:
        """Открыть замок. Возвращает True при успехе."""

    @abstractmethod
    def close(self, room_id: str) -> bool:
        """Закрыть замок."""

    @abstractmethod
    def status(self, room_id: str) -> str:
        """Получить статус: 'open' | 'closed' | 'error'"""
```

### 7.2 HTTP-реализация (сетевые контроллеры СКУД)

```python
# client/app/drivers/http_lock.py
import httpx
from app.core.lock_driver import LockDriver

class HttpLockDriver(LockDriver):
    def __init__(self, base_url: str, api_key: str, open_duration_sec: int = 5):
        self._client = httpx.Client(base_url=base_url,
                                     headers={"Authorization": f"Bearer {api_key}"},
                                     timeout=5.0)
        self._duration = open_duration_sec

    def open(self, room_id: str) -> bool:
        try:
            resp = self._client.post(f"/lock/{room_id}/open",
                                      json={"duration": self._duration})
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Lock open failed for {room_id}: {e}")
            return False

    def close(self, room_id: str) -> bool:
        try:
            resp = self._client.post(f"/lock/{room_id}/close")
            return resp.status_code == 200
        except Exception:
            return False

    def status(self, room_id: str) -> str:
        try:
            resp = self._client.get(f"/lock/{room_id}/status")
            return resp.json().get("state", "error")
        except Exception:
            return "error"
```

### 7.3 Modbus RTU реализация (RS-485)

```python
# client/app/drivers/modbus_lock.py
import serial
import struct
from app.core.lock_driver import LockDriver

class ModbusLockDriver(LockDriver):
    """Управление замком через Modbus RTU по RS-485."""

    def __init__(self, port: str, baudrate: int = 9600, unit_id: int = 1):
        self._port = port
        self._baudrate = baudrate
        self._unit_id = unit_id

    def _write_coil(self, coil_address: int, value: bool) -> bool:
        with serial.Serial(self._port, self._baudrate, timeout=1) as ser:
            # Modbus FC05: Write Single Coil
            payload = struct.pack(">BBHH",
                self._unit_id, 0x05, coil_address, 0xFF00 if value else 0x0000)
            crc = self._calc_crc(payload)
            ser.write(payload + crc)
            response = ser.read(8)
            return len(response) == 8

    def open(self, room_id: str) -> bool:
        coil = int(room_id) - 1  # маппинг room_number → coil address
        return self._write_coil(coil, True)

    def close(self, room_id: str) -> bool:
        coil = int(room_id) - 1
        return self._write_coil(coil, False)

    def status(self, room_id: str) -> str:
        return "unknown"  # реализуется через FC01 Read Coils

    @staticmethod
    def _calc_crc(data: bytes) -> bytes:
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return struct.pack("<H", crc)
```

### 7.4 Фабрика драйверов

```python
# client/app/core/lock_driver.py
def create_lock_driver(config) -> LockDriver:
    drivers = {
        "http":   lambda: HttpLockDriver(config.LOCK_HTTP_URL, config.API_KEY),
        "modbus": lambda: ModbusLockDriver(config.LOCK_SERIAL_PORT),
        "mqtt":   lambda: MqttLockDriver(config.MQTT_BROKER),
        "gpio":   lambda: GpioLockDriver(),
        "dummy":  lambda: DummyLockDriver(),  # для тестирования без железа
    }
    driver_factory = drivers.get(config.LOCK_DRIVER)
    if not driver_factory:
        raise ValueError(f"Неизвестный драйвер замка: {config.LOCK_DRIVER}")
    return driver_factory()
```

---

## Этап 8. Офлайн-режим и синхронизация

### 8.1 Стратегия работы без сети

```
Запуск приложения
       │
       ▼
  Попытка подключения к серверу
       │
   ┌───┴───────────────────────────┐
успех                           неудача
   │                               │
   ▼                               ▼
Инкрементальная              Работа полностью
синхронизация (since=...)    по локальной SQLite
   │
   ▼
Загрузка эмбеддингов
в FaceRecognizer
```

### 8.2 Менеджер синхронизации

```python
# client/app/core/sync_manager.py
from datetime import datetime, UTC
from loguru import logger

class SyncManager:
    def __init__(self, api_client, db, biometric):
        self._api = api_client
        self._db = db
        self._biometric = biometric

    def startup_sync(self):
        """Вызывается при запуске приложения."""
        try:
            last_sync = self._db.get_meta("last_sync_at") or "1970-01-01T00:00:00"
            data = self._api.sync(since=last_sync)
            self._apply_changes(data)
            self._db.set_meta("last_sync_at", datetime.now(UTC).isoformat())
            logger.info(f"Синхронизация завершена: "
                        f"{len(data['employees'])} сотрудников, "
                        f"{len(data['rooms'])} кабинетов")
        except Exception as e:
            logger.warning(f"Нет связи с сервером, работаем офлайн: {e}")

        # В любом случае загружаем локальные данные
        employees = self._db.get_all_employees()
        self._biometric.load_from_db(employees)

    def _apply_changes(self, data: dict):
        for emp in data.get("employees", []):
            self._db.upsert_employee(emp)
        for room in data.get("rooms", []):
            self._db.upsert_room(room)

    def push_local_employee(self, employee_data: dict):
        """Отправляет нового сотрудника на сервер (если есть связь)."""
        try:
            result = self._api.post("/api/employees", employee_data)
            self._db.update_employee_server_id(
                local_id=employee_data["id"],
                server_id=result["id"]
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить сотрудника на сервер: {e}")
```

---

## Этап 9. Безопасность

### 9.1 Чеклист безопасности

| Область | Мера | Реализация |
|---------|------|------------|
| Данные в покое | Шифрование face_embedding | AES-256-GCM (cryptography) |
| Локальная БД | Шифрование SQLite-файла | SQLCipher + PRAGMA key |
| Транспорт | TLS 1.3 | nginx + Let's Encrypt |
| API-аутентификация | API-key в заголовке | X-API-Key middleware |
| Пароль администратора | Хэш вместо plaintext | bcrypt |
| Ключи шифрования | В .env, не в коде | python-dotenv |
| Подделка лица | Liveness detection | InsightFace anti-spoof |
| Логи | Ротация, без PII | Loguru + маскирование ФИО |

### 9.2 Генерация ключей

```bash
# Генерация ключа шифрования embedding'ов (256 бит)
python -c "import secrets; print(secrets.token_hex(32))"

# Генерация API-ключа
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Пароль администратора (bcrypt)
python -c "import bcrypt; print(bcrypt.hashpw(b'mypassword', bcrypt.gensalt()).decode())"
```

### 9.3 Nginx конфигурация (TLS)

```nginx
server {
    listen 443 ssl http2;
    server_name your-server.local;

    ssl_certificate     /certs/fullchain.pem;
    ssl_certificate_key /certs/privkey.pem;
    ssl_protocols       TLSv1.3;
    ssl_ciphers         ECDHE-ECDSA-AES256-GCM-SHA384;

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}

server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

---

## Этап 10. Тестирование

### 10.1 Серверные тесты (pytest + httpx)

```python
# server/tests/test_employees.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_employee():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/employees",
            json={
                "name": "Иван",
                "surname": "Иванов",
                "department": "ИТ",
                "position": "Разработчик",
                "face_embedding_b64": "<base64_string>",
            },
            headers={"X-API-Key": "test-key"},
        )
    assert response.status_code == 201
    assert response.json()["name"] == "Иван"
```

### 10.2 Клиентские тесты

```python
# client/tests/test_biometric.py
import numpy as np
from app.core.biometric import FaceRecognizer

def test_identify_known_employee():
    recognizer = FaceRecognizer(threshold=0.50)
    vec = np.random.rand(512).astype(np.float32)
    vec /= np.linalg.norm(vec)
    recognizer._embeddings = [(42, vec)]

    # Слегка зашумлённый вектор того же человека
    noisy = vec + np.random.normal(0, 0.05, 512)
    noisy /= np.linalg.norm(noisy)

    assert recognizer.identify(noisy) == 42

def test_reject_unknown():
    recognizer = FaceRecognizer(threshold=0.50)
    vec1 = np.random.rand(512).astype(np.float32); vec1 /= np.linalg.norm(vec1)
    vec2 = np.random.rand(512).astype(np.float32); vec2 /= np.linalg.norm(vec2)
    recognizer._embeddings = [(1, vec1)]
    assert recognizer.identify(vec2) is None
```

### 10.3 Параметры оценки качества распознавания

| Параметр | Целевое значение |
|----------|----------------|
| FAR (False Acceptance Rate) | < 0.1% |
| FRR (False Rejection Rate) | < 1% |
| Время распознавания | < 300 мс |
| Работа при освещении 200–1000 лк | ✓ |
| Работа с очками | ✓ |
| Работа в маске | Ограниченно |

---

## Этап 11. Упаковка и развёртывание

### 11.1 Сборка клиентского приложения

```bash
# Установка PyInstaller
pip install pyinstaller

# Сборка в один файл
pyinstaller \
  --onefile \
  --windowed \
  --name "BiometricAccess" \
  --add-data "models:models" \
  --add-data ".env.example:.env.example" \
  --hidden-import "insightface" \
  --hidden-import "onnxruntime" \
  client/app/main.py

# Результат: dist/BiometricAccess.exe (Windows)
#            dist/BiometricAccess     (Linux)
```

### 11.2 Развёртывание сервера

```bash
# На сервере (Ubuntu 22.04)
git clone https://github.com/your-org/biometric-access.git
cd biometric-access/server

# Создаём .env
cp .env.example .env
nano .env  # вставляем DB_PASSWORD, API_KEY

# Запускаем
docker compose up -d

# Проверяем
curl -H "X-API-Key: your-key" https://your-server.local/api/rooms
```

### 11.3 Установка клиента на терминал

```
1. Скопировать BiometricAccess.exe на машину терминала
2. Создать .env рядом с exe:
   SERVER_URL=https://your-server.local
   API_KEY=your-secret-key
   CAMERA_SOURCE=0
   LOCK_DRIVER=http
   LOCK_HTTP_URL=http://192.168.1.10
3. Запустить — при первом старте произойдёт полная синхронизация
4. Добавить в автозапуск (Windows: Task Scheduler / Linux: systemd)
```

### 11.4 systemd-unit для Linux-терминала

```ini
# /etc/systemd/system/biometric-terminal.service
[Unit]
Description=Biometric Access Terminal
After=network.target

[Service]
Type=simple
User=terminal
WorkingDirectory=/opt/biometric
ExecStart=/opt/biometric/BiometricAccess
Restart=on-failure
RestartSec=5
Environment="DISPLAY=:0"

[Install]
WantedBy=graphical.target
```

---

## Контрольный список MVP

- [ ] **Этап 1:** Репозиторий, структура, .env конфигурация
- [ ] **Этап 2:** FastAPI CRUD для employees + rooms, аутентификация, Docker
- [ ] **Этап 3:** CustomTkinter каркас, видеопоток, локальная SQLite
- [ ] **Этап 4:** InsightFace детекция + embedding, шифрование, поиск
- [ ] **Этап 5:** Форма регистрации, просмотр и редактирование списков
- [ ] **Этап 6:** Непрерывное распознавание, RoomManager, выдача/возврат ключей
- [ ] **Этап 7:** Драйвер замка под конкретное оборудование
- [ ] **Этап 8:** Офлайн-режим, инкрементальная синхронизация
- [ ] **Этап 9:** Полное шифрование, TLS, bcrypt для admin-пароля
- [ ] **Этап 10:** Unit-тесты биометрики и API, полевые испытания
- [ ] **Этап 11:** PyInstaller-сборка, Docker deploy, документация
