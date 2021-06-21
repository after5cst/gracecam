import PyATEMMax


class ATEM:
    def __init__(self, *, ip_address: str):
        self.ip = ip_address
        self.mixEffect = 0
        self.switcher = PyATEMMax.ATEMMax()
        self.switcher.connect(ip_address)
        self.switcher.waitForConnection(infinite=False, timeout=60.0)

    def exec(self):
        self.switcher.execAutoME(self.mixEffect)

    @property
    def program(self) -> int:
        return self.switcher.programInput[self.mixEffect].videoSource.value

    @program.setter
    def program(self, value: int):
        self.switcher.setProgramInputVideoSource(self.mixEffect, value)

    @property
    def preview(self):
        return self.switcher.previewInput[self.mixEffect].videoSource.value

    @preview.setter
    def preview(self, value: int):
        self.switcher.setPreviewInputVideoSource(self.mixEffect, value)
