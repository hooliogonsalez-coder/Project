import paho.mqtt.client as mqtt
from app.core.lock_driver import LockDriver


class MqttLockDriver(LockDriver):
    def __init__(self, broker: str, topic_prefix: str = "lock"):
        self._broker = broker
        self._topic_prefix = topic_prefix
        self._client = mqtt.Client()
        self._client.connect(broker)
        self._client.loop_start()

    def open(self, room_id: str) -> bool:
        try:
            topic = f"{self._topic_prefix}/{room_id}/open"
            self._client.publish(topic, "1")
            return True
        except Exception:
            return False

    def close(self, room_id: str) -> bool:
        try:
            topic = f"{self._topic_prefix}/{room_id}/close"
            self._client.publish(topic, "0")
            return True
        except Exception:
            return False

    def status(self, room_id: str) -> str:
        return "open"