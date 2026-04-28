import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from app.config import settings
from app.core.db import get_connection, init_db
from app.core.api_client import APIClient
from app.core.biometric import FaceRecognizer
from app.core.sync_manager import SyncManager
from app.gui.main_window import main


def setup_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    Path("./logs").mkdir(parents=True, exist_ok=True)
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",
        retention="7 days",
        level=settings.LOG_LEVEL,
    )


def init_application():
    Path("./data").mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)

    setup_logging()

    conn = get_connection(settings.SQLITE_DB_PATH, settings.SQLITE_KEY)
    init_db(conn)

    biometric = FaceRecognizer(
        model_name=settings.FACE_MODEL,
        threshold=settings.FACE_RECOGNITION_THRESHOLD,
    )

    sync_manager = None
    try:
        api = APIClient()
        sync_manager = SyncManager(api, conn, biometric)
        sync_manager.startup_sync()
        logger.info("Синхронизация завершена")
    except Exception as e:
        logger.warning(f"Офлайн режим: {e}")
        if sync_manager:
            employees = sync_manager._load_employees()
            biometric.load_from_db(employees)

    return conn, biometric


if __name__ == "__main__":
    try:
        init_application()
    except Exception as e:
        print(f"Ошибка инициализации: {e}")

    main()