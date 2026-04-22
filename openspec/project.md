# Проект: Контроль выдачи ключей

Система контроля выдачи ключей с распознаванием лица для идентификации сотрудников.

## Технологический стек

- **Python 3.10+**
- **Tkinter** — GUI фреймворк
- **SQLite** — база данных
- **OpenCV** — обработка изображений
- **MediaPipe** — детекция лица (SCRFD)
- **ArcFace (ONNX)** — эмбеддинги лица
- **NumPy, Pillow** — работа с массивами и изображениями

## Архитектура проекта

```
PythonProject/
├── main.py              # Точка входа
├── config.py           # Конфигурация (цвета, шрифты, пути)
├── requirements.txt   # Зависимости
├── ui/                # Интерфейс (MainWindow, VideoPanel, KeysTable, диалоги)
├── services/          # Бизнес-логика (CameraService, FaceService, KeyService)
├── database/         # Работа с SQLite
├── models/            # Dataclasses (Employee, Key)
├── data/             # DataStore
└── docs/             # Диаграммы PlantUML
```

## Соглашения

- **Язык интерфейса:** русский
- **Стиль кода:** Python dataclasses для моделей
- **Конфигурация:** модуль `config.py`
- **Логирование:** стандартный `logging`
- **Именование:** snake_case для переменных, CamelCase для классов
- **Типизация:** аннотации в стиле Python 3.10+