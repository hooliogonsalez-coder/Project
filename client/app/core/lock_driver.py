from abc import ABC, abstractmethod


class LockDriver(ABC):
    @abstractmethod
    def open(self, room_id: str) -> bool:
        pass

    @abstractmethod
    def close(self, room_id: str) -> bool:
        pass

    @abstractmethod
    def status(self, room_id: str) -> str:
        pass


def create_lock_driver(config) -> LockDriver:
    drivers = {
        "http": lambda: HttpLockDriver(config.LOCK_HTTP_URL, config.API_KEY),
        "dummy": lambda: DummyLockDriver(),
    }

    if config.LOCK_DRIVER == "modbus":
        from app.drivers.modbus_lock import ModbusLockDriver
        drivers["modbus"] = lambda: ModbusLockDriver(config.LOCK_SERIAL_PORT)
    elif config.LOCK_DRIVER == "mqtt":
        from app.drivers.mqtt_lock import MqttLockDriver
        drivers["mqtt"] = lambda: MqttLockDriver(config.MQTT_BROKER)
    elif config.LOCK_DRIVER == "gpio":
        from app.drivers.gpio_lock import GpioLockDriver
        drivers["gpio"] = lambda: GpioLockDriver()

    driver_factory = drivers.get(config.LOCK_DRIVER)
    if not driver_factory:
        raise ValueError(f"Неизвестный драйвер замка: {config.LOCK_DRIVER}")
    return driver_factory()


from app.drivers.http_lock import HttpLockDriver
from app.drivers.dummy_lock import DummyLockDriver