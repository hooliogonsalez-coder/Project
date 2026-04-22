## Why

Текущая архитектура проекта имеет проблемы связности и тестируемости: `MainWindow` напрямую создаёт `Database` и сервисы, отсутствуют абстракции, а `DataStore` смешивает доступ к данным и бизнес-логику. Это затрудняет тестирование, расширение и поддержку кода.

## What Changes

- Внедрение **Dependency Injection (DI)** для управления зависимостями
- Создание **интерфейсов** для сервисов с чёткими контрактами
- Рефакторинг `DataStore` — только доступ к данным, убрать бизнес-логику
- Добавление **DI-контейнера** как единой точки сборки приложения
- Улучшение **тестируемости** — возможность подмены зависимостей через моки

## Capabilities

### New Capabilities
- `di-container`: DI-контейнер для управления жизненным циклом зависимостей
- `service-interfaces`: Интерфейсы `KeyRepository`, `EmployeeRepository`, `FaceRecognizer`
- `key-lending-spec`: Спецификация логики выдачи/приёма ключей
- `data-migration`: Миграция данных при изменении схемы БД

### Modified Capabilities
- `key-management`: Перенести логику выдачи/приёма из `DataStore` в `KeyService`

## Impact

- `database/database.py` — рефакторинг методов
- `data/store.py` — только data access, убрать `issue_key`, `return_key`
- `services/key_service.py` — расширить с учётом интерфейса репозитория
- `ui/main_window.py` — получение зависимостей через DI-контейнер
- Новые файлы: `core/container.py`, `core/interfaces.py`
- Тесты: возможность мокать `Database` и сервисы