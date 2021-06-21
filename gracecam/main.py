import logging
import random
try:
    from . import (
        Camera, cameras, MidiNote, midi, midi_to_pos,
        Pos, randoms, standby_positions
    )
except ImportError:
    from __init__ import (
        ATEM, ATEM_IP, Camera, cameras, MidiNote, midi,
        midi_to_pos, Pos, randoms, standby_positions
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
program = None  # type: Optional[Camera]


def switch(camera: Camera):
    global program
    program = camera
    logging.info(f"Showing camera '{camera.name}'")
    atem.preview = camera.atem
    atem.exec()

    # Now, move the other cameras to cover standby positions.
    positions = [x for x in standby_positions]
    if program.preset in positions:
        positions.remove(program.preset)
    logging.debug(f"Checking camera coverage for {positions}")
    for camera in cameras:
        if camera == program:
            continue
        if camera.preset in positions:
            logging.debug(f"'{camera.name}' already convering '{camera.preset.name}'")
            positions.remove(camera.preset)
        elif positions:
            pos = list(positions)[0]
            camera.move(preset=pos)
            positions.remove(pos)


def process(message: MidiNote) -> None:
    global program
    try:
        pos = midi_to_pos[message.note]
    except KeyError:
        pos = random.choice(randoms)

    logging.debug('-' * 60)
    logging.info(f"Mapped '{message}' to position '{pos.name}'")

    # Step 1 : If it's already on another camera, switch and we're done.
    for camera in cameras:
        if camera == program:
            continue
        if camera.preset == pos:
            camera.move(preset=pos, callback=switch)
            return

    # Step 2 : Pick a camera to move and move it.
    for camera in cameras:
        if camera != program:
            camera.move(preset=pos, callback=switch)
            return


def main():
    for camera in cameras:
        camera.move(Pos.PULPIT)
    with midi:
        while True:
            message = midi.get()
            if message:
                process(message)
            else:
                time.sleep(1)


if __name__ == '__main__':
    main()
