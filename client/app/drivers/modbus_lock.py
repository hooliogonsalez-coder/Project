import serial
import struct
from app.core.lock_driver import LockDriver


class ModbusLockDriver(LockDriver):
    def __init__(self, port: str, baudrate: int = 9600, unit_id: int = 1):
        self._port = port
        self._baudrate = baudrate
        self._unit_id = unit_id

    def _write_coil(self, coil_address: int, value: bool) -> bool:
        try:
            with serial.Serial(self._port, self._baudrate, timeout=1) as ser:
                payload = struct.pack(
                    ">BBHH",
                    self._unit_id, 0x05, coil_address, 0xFF00 if value else 0x0000
                )
                crc = self._calc_crc(payload)
                ser.write(payload + crc)
                response = ser.read(8)
                return len(response) == 8
        except Exception:
            return False

    def open(self, room_id: str) -> bool:
        coil = int(room_id) - 1
        return self._write_coil(coil, True)

    def close(self, room_id: str) -> bool:
        coil = int(room_id) - 1
        return self._write_coil(coil, False)

    def status(self, room_id: str) -> str:
        return "unknown"

    @staticmethod
    def _calc_crc(data: bytes) -> bytes:
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return struct.pack("<H", crc)