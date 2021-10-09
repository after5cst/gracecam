import enum
import logging
import requests
import threading
from typing import Optional


@enum.unique
class Pos(enum.Enum):
    PULPIT = 0
    LEADER = 2
    PRESET3 = 3
    ORGAN = 5
    MIDDLE = 7
    PIANO = 9
    WIDE = 4
    UNKNOWN = -1


class Camera:
    """A PTZ Optics Camera and related state.

    Attributes:
        ip      The IP address of the camera
        name    A friendly name for the camera
        preset  The current known preset position
        atem    The ATEM source position
    """
    def __init__(self, *, name: str, ip_address: str, num: int):
        self.ip = ip_address
        self.name = name
        self.atem = -1
        self.num = num
        self.preset = Pos.UNKNOWN

    def move(self, preset: Pos, callback: Optional[callable] = None):
        """ Move to specified preset"""
        def move_callback():
            self._moved(preset)
            if callback:
                callback(self)

        if preset == self.preset:
            move_callback()
            return

        msg = f"Moving '{self.name}' from {self.preset.name} to {preset.name}"
        logging.info(msg)
        cmd = f"http://{self.ip}/cgi-bin/ptzctrl.cgi?ptzcmd&poscall&{preset.value}"

        # TESTING: Comment out these next two lines to test without cameras
        try:
            response = requests.get(cmd)
            logging.debug(response)
        except Exception:
            logging.error("Exception thrown making camera request")

        self.preset = Pos.UNKNOWN
        threading.Timer(1.0, move_callback).start()

    def _moved(self, preset: Pos):
        logging.info(f"Camera '{self.name}' at preset {preset.name}")
        self.preset = preset
