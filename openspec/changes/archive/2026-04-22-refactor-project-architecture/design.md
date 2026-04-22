## Context

Проект "Контроль выдачи ключей" использует Tkinter GUI с OpenCV/MediaPipe для распознавания лиц. Текущая архитектура имеет следующие проблемы:

- `MainWindow` напрямую создаёт `Database(config.DATABASE_PATH)` — жёсткая связность
- `DataStore` смешивает data access (`get_key`) и бизнес-логику (`issue_key`)
- Нет интерфейсов — невозможно мокать зависимости в тестах
- Единая точка сборки отсутствует — сложно управлять жизненным циклом

## Goals / Non-Goals

**Goals:**
- DI-контейнер как единая точка сборки приложения
- Интерфейсы для всех сервисов
- Чистое разделение: DataStore — только data access, KeyService — бизнес-логика
- Тестируемость без реальной БД

**Non-Goals:**
- Полноценный IoC-фреймворк (сложная библиотека не требуется)
- Изменение API для UI компонентов
- Миграция на другую СУБД

## Decisions

### 1. Простой DI-контейнер (без библиотек)

**Решение:** Ручная реализация без внешних библиотек.

**Обоснование:** Проект небольшой, зависимостей мало. Внешняя библиотека (injector/dependency-injector) добавит зависимость без существенной пользы.

```python
class Container:
    _services: dict[type, object] = {}
    
    def register(self, cls: type, instance: object):
        _services[cls] = instance
    
    def get(self, cls: type) -> object:
        if cls not in _services:
            raise KeyError(f"Service {cls} not registered")
        return _services[cls]
```

### 2. Абстрактные базовые классы для репозиториев

**Решение:** Python ABC (Abstract Base Classes).

**Обоснование:** Встроенный механизм, не требует зависимостей. Простой и понятный.

```python
from abc import ABC, abstractmethod

class KeyRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Key]: ...
```

### 3. DataStore становится Repository Coordinator

**Решение:** `DataStore` остаётся, но убирает бизнес-логику.

**До рефакторинга:**
```python
class DataStore:
    def issue_key(self, cabinet, emp):  # бизнес-логика
        ...
```

**После рефакторинга:**
```python
class DataStore:
    @property
    def keys(self) -> KeyRepository: ...
```

### 4. Миграции через версионирование схемы

**Решение:** Таблица `schema_version` + функция `run_migrations()`.

```python
CURRENT_VERSION = 1

def get_schema_version(conn) -> int:
    # SELECT version FROM schema_version
    ...

def run_migrations():
    version = get_schema_version()
    if version < CURRENT_VERSION:
        for v in range(version + 1, CURRENT_VERSION + 1):
            exec(migration_scripts[v])
        update_version(CURRENT_VERSION)
```

## Risks / Trade-offs

| Риск | mitigation |
|------|------------|
| Смешанные изменения сломают историю git | Изменения по одному per-commit |
| Tkinter виджеты зависят от сервисов | DI передаёт готовые экземпляры в конструктор |
| Existing tests сломаются | Адаптеры для обратной совместимости |

## Open Questions

1. Сохранять ли обратную совместимость с `DataStore.issue_key()`?
2. Нужен ли event bus для асинхронных событий?