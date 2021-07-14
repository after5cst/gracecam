import logging
import PyATEMMax


class ATEM:
    def __init__(self, *, ip_address: str):
        self.ip = ip_address
        self.mixEffect = 0
        self.switcher = PyATEMMax.ATEMMax()
        self.switcher.connect(self.ip)
        if self.switcher.waitForConnection():
            logging.info(f"Connected to ATEM at {self.ip}")
        else:
            raise RuntimeError(f"Unable to find ATEM at {self.ip}")

    def exec(self):
        logging.debug(f"Sending EXEC to ATEM {self.ip}")
        self.switcher.execAutoME(self.mixEffect)

    @property
    def program(self) -> int:
        return self.switcher.programInput[self.mixEffect].videoSource.value

    @program.setter
    def program(self, value: int):
        logging.info(f"Setting ATEM Program to {value}")
        self.switcher.setProgramInputVideoSource(self.mixEffect, value)
        # assert self.program == value

    @property
    def preview(self):
        return self.switcher.previewInput[self.mixEffect].videoSource.value

    @preview.setter
    def preview(self, value: int):
        logging.info(f"Setting ATEM Preview to {value}")
        self.switcher.setPreviewInputVideoSource(self.mixEffect, value)
        # assert self.preview == value
