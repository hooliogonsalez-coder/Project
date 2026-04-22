 Контроль выдачи ключей

Система контроля выдачи ключей с распознаванием лица для идентификации сотрудников.

## Функциональность

- Распознавание лица сотрудника через веб-камеру
- Хранение данных сотрудников в SQLite (ФИО, должность, фото, эмбеддинг лица)
- Выдача и приём ключей от шкафчиков
- Логирование событий
- Интерфейс на Tkinter

## Требования

- Python 3.10+
- OpenCV
- MediaPipe
- NumPy
- Pillow

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python main.py
```

## Структура БД

### Таблица employees
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | ID сотрудника (PK) |
| full_name | TEXT | ФИО сотрудника |
| position | TEXT | Должность |
| face_encoding | BLOB | Эмбеддинг лица (128 float) |
| photo | BLOB | Фото сотрудника |

### Таблица keys
| Поле | Тип | Описание |
|------|-----|----------|
| cabinet | TEXT | Номер шкафчика (PK) |
| status | TEXT | Статус (AVAILABLE/ISSUED) |
| holder_id | INTEGER | ID сотрудника, взявший ключ |
| holder_name | TEXT | ФИО сотрудника |

## Использование

1. Выберите камеру из выпадающего списка
2. Нажмите "РАСПОЗНАТЬ ЛИЦО" для идентификации сотрудника
3. Выберите шкафчик в таблице
4. Нажмите "ВЫДАТЬ КЛЮЧ" или "ПРИНЯТЬ КЛЮЧ"

## Добавление сотрудников

Для добавления сотрудника используйте метод `add_employee_with_photo`:

```python
from database import Database
from services import FaceService
from data import DataStore

db = Database("data.db")
store = DataStore(db)
face_service = FaceService(store)

with open("photo.jpg", "rb") as f:
    photo_data = f.read()

emp_id = face_service.add_employee_with_photo(
    full_name="Иванов Иван Иванович",
    position="Завхоз",
    photo_data=photo_data
)
```

## Настройки

Параметры находятся в `config.py`:

- `DATABASE_PATH` - путь к файлу БД
- `FACE_THRESHOLD` - порог схожести лиц (0.0-1.0, меньше = строже)
- `VIDEO_UPDATE_INTERVAL_MS` - частота обновления видео
