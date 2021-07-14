import logging
import random
import texttable

try:
    from . import (
        ATEM, ATEM_IP, Camera, cameras, MidiNote, midi,
        midi_to_pos, Pos, program_staging, randoms, standby_positions
    )
except ImportError:
    from __init__ import (
        ATEM, ATEM_IP, Camera, cameras, MidiNote, midi,
        midi_to_pos, Pos, program_staging, randoms, standby_positions
    )

from pathlib import Path
import time
from typing import Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%M:%S')  # datefmt='%Y-%m-%d %H:%M:%S'

atem = ATEM(ip_address=ATEM_IP)

# This variable is used to detect when something else has changed
# what camera is showing on the ATEM.  When that happens, we need
# to not trust that the camera positions we have set are correct.
lastAtemPos = -1


class Stations:
    # A 'struct' that contains cameras by their current role:
    # -- program : currently showing on the ATEM
    # -- preview : currently ready to be EXEC'd by the ATEM
    # -- standby : Neither of the other two.
    def __init__(self):
        # Just assign some defaults.  They will be overridden.
        self.program = cameras[0]
        self.preview = cameras[1]
        self.standby = cameras[-1]

    def set_from_atem(self):
        """Read the ATEM and set program/preview/standby to match"""
        program_id = atem.program
        preview_id = atem.preview
        logging.debug(f"ids:  program={program_id} preview={preview_id}")

        for camera in cameras:
            if camera.atem == program_id:
                self.program = camera
                logging.debug(f"Program is currently {camera.name}")
            if camera.atem == preview_id:
                self.preview = camera
                logging.debug(f"Preview is currently {camera.name}")

        staging = Stations().set_from_staging()
        if staging.preview == self.preview:
            # AHA!  staging matches current for program/preview.
            self.standby = staging.standby
            logging.debug(f"Standby is currently {camera.name}")
        else:
            # They don't match: just find something.
            for camera in cameras:
                if camera not in (self.program, self.preview):
                    self.standby = camera
                    logging.debug(f"Standby defaulted to {camera.name}")
                    break
        return self

    def set_from_staging(self):
        """Read the ATEM and set preview/standby from program"""
        program_id = atem.program
        self.program = cameras[program_id-1]
        # logging.debug(f"Program is currently {self.program.name}")
        staging = program_staging[self.program.name]
        for camera in cameras:
            if camera.name == staging['preview']:
                self.preview = camera
                atem.preview = camera.atem
                # logging.debug(f"Preview is staged as {camera.name}")
            elif camera.name == staging['standby']:
                self.standby = camera
                # logging.debug(f"Standby is staged as {camera.name}")
        return self


def switch(nextCamera: Optional[Camera]):
    global lastAtemPos

    prev = Stations().set_from_atem()
    # Cache off the camera presets.  When the camera moves, so will the presets.
    prev.program_preset = prev.program.preset
    prev.preview_preset = prev.preview.preset
    prev.standby_preset = prev.standby.preset

    if 'UNKNOWN' in (prev.program_preset.name, prev.preview_preset.name):
        logging.info(f"Unknown camera state.  Setting up cameras")
        atem.preview = nextCamera.atem
    elif prev.program == nextCamera:
        logging.info(f"Program camera '{nextCamera.name}' already showing")
        return
    elif prev.preview == nextCamera:
        logging.info(f"Moving preview camera '{nextCamera.name}' to program")
    elif prev.standby == nextCamera:
        logging.info(f"Moving standby camera '{nextCamera.name}' to program")
        atem.preview = nextCamera.atem
    else:
        logging.warning(f"Moving SURPRISE camera '{nextCamera.name}' to program")
        atem.preview = nextCamera.atem

    atem.exec()
    time.sleep(1.5)  # Wait for the transition to happen.
    curr = Stations().set_from_staging()

    lastAtemPos = curr.program.atem

    # Always set preview to be a random camera.
    next_preview_pos = move_preview_to_random(curr)

    # Now move the standby camera.  If the standby position is already active, choose
    # the backup standby position.
    pos = standby_positions[0]
    if pos in (next_preview_pos, curr.program.preset):
        pos = standby_positions[-1]
    curr.standby.move(preset=pos)

    time.sleep(2)
    curr.program_preset = curr.program.preset
    curr.preview_preset = curr.preview.preset
    curr.standby_preset = curr.standby.preset

    # And make me a happy little table.
    table = texttable.Texttable(80)
    table.set_cols_align(["l", "c", "c", "c"])
    table.add_rows([
        ["", "program", "preview", "standby"],
        ["Before",
         f"{prev.program_preset.name}({prev.program.name})",
         f"{prev.preview_preset.name}({prev.preview.name})",
         f"{prev.standby_preset.name}({prev.standby.name})",
         ],
        ["after",
         f"{curr.program_preset.name}({curr.program.name})",
         f"{curr.preview_preset.name}({curr.preview.name})",
         f"{curr.standby_preset.name}({curr.standby.name})",
         ],
    ])
    lines = table.draw().splitlines()
    for line in lines:
        logging.info(line)


def move_preview_to_random(curr, callback=None):
    pos = random.choice(randoms)
    while curr.program and pos.name in (curr.program.preset.name, curr.preview.preset.name):
        logging.debug(f"Re-picking random position '{pos.name}'")
        pos = random.choice(randoms)
    if curr.program and pos:
        logging.debug(f"Random '{pos.name}' picked for preview")
    curr.preview.move(preset=pos, callback=callback)
    return pos


def process(message: MidiNote) -> None:
    global lastAtemPos
    curr = Stations().set_from_atem()
    try:
        pos = midi_to_pos[message.note]
    except KeyError:
        if curr.preview.preset.name != 'UNKNOWN':
            pos = curr.preview.preset
        else:
            if curr.preview.atem == curr.program.atem:
                # They're the same: pick a different camera.
                curr.preview = curr.standby
            move_preview_to_random(curr, switch)
            return

    logging.debug('-' * 60)
    logging.info(f"Mapped '{message}' to position '{pos.name}'")

    lastAtemPos = curr.program.atem
    for camera in cameras:
        if camera.preset == pos:
            camera.move(preset=pos, callback=switch)
            return

    curr.preview.move(preset=pos, callback=switch)


def main():
    with midi:
        # Flush anything out there already.
        if midi.get(0.1):
            logging.info("Flushing MIDI messages")
            while midi.get(0.1):
                pass
            logging.info("Flush complete")

        while True:
            message = midi.get()
            if message:
                process(message)
                time.sleep(0.5)
            elif atem.program != lastAtemPos:
                # Detected somebody else changed
                # the program.  Assume cameras moved, too.
                logging.info("Detected ATEM program change")
                for camera in cameras:
                    camera.preset = Pos.UNKNOWN
            else:
                logging.debug("No MIDI message available.")
                time.sleep(1)


if __name__ == '__main__':
    main()
