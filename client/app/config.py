from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVER_URL: str = "https://your-server.local"
    API_KEY: str = "your-secret-api-key"

    FACE_RECOGNITION_THRESHOLD: float = 0.50
    FACE_MODEL: str = "buffalo_l"

    CAMERA_SOURCE: int = 0
    CAMERA_FPS: int = 15

    ROOM_TIMEOUT_MINUTES: int = 480

    SQLITE_DB_PATH: str = "./data/local.db"
    SQLITE_KEY: str = "change-me-in-production"

    LOCK_DRIVER: str = "http"
    LOCK_HTTP_URL: str = "http://192.168.1.10/lock"
    LOCK_SERIAL_PORT: str = "COM1"
    MQTT_BROKER: str = "localhost"

    EMBEDDING_KEY: str = "change-me-in-production"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/client.log"

    ADMIN_PASSWORD: str = "admin123"


settings = Settings()