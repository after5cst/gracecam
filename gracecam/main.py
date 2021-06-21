import logging
import random
import texttable

try:
    from . import (
        ATEM, ATEM_IP, Camera, cameras, MidiNote, midi,
        midi_to_pos, Pos, randoms, standby_positions
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
lastAtemPos = -1


def switch(nextCamera: Optional[Camera]):
    global lastAtemPos
    if nextCamera:
        logging.info(f"Showing camera '{nextCamera.name}'")
        atem.preview = nextCamera.atem
        atem.exec()
    lastAtemPos = nextCamera.atem

    what_is_where = dict()
    for camera in cameras:
        fmt = "-->{}<--" if camera == nextCamera else "{}"
        what_is_where[camera.name] = fmt.format(camera.preset.name)

    positions = [x for x in standby_positions]
    # This would eliminate duplicates.  But since we want 'LEADER'
    # always ready, this is currently commented out.
    if nextCamera.preset in positions:
        positions.remove(nextCamera.preset)

    delay_time = 1.0

    logging.debug(f"Checking camera coverage for {positions}")
    for camera in cameras:
        if camera.atem == lastAtemPos:
            continue
        if camera.preset in positions:
            logging.debug(f"'{camera.name}' already covering '{camera.preset.name}'")
            positions.remove(camera.preset)
        elif positions:
            # Make sure the transition is complete above so we don't
            # see the camera start moving during fade.
            time.sleep(delay_time)
            delay_time = 0

            pos = list(positions)[0]
            camera.move(preset=pos)
            positions.remove(pos)
            what_is_where[camera.name] = pos.name

    # And make me a happy little table.
    tableObj = texttable.Texttable(80)
    tableObj.set_cols_align(['c'] * len(what_is_where))
    header_items = [x for x in what_is_where.keys()]
    data_items = [what_is_where[x] for x in header_items]
    tableObj.add_rows([header_items, data_items])
    lines = tableObj.draw().splitlines()
    for line in lines:
        logging.info(line)


def process(message: MidiNote) -> None:
    global lastAtemPos
    try:
        pos = midi_to_pos[message.note]
    except KeyError:
        pos = random.choice(randoms)

    logging.debug('-' * 60)
    logging.info(f"Mapped '{message}' to position '{pos.name}'")

    # Step 1 : If it's already on another camera, switch and we're done.
    lastAtemPos = atem.program
    for camera in cameras:
        if camera.atem == lastAtemPos:
            #  skip the 'live' camera.
            continue
        if camera.preset == pos:
            camera.move(preset=pos, callback=switch)
            return

    # Step 2 : Pick a camera to move and move it.
    for camera in cameras:
        if camera.atem != lastAtemPos:
            camera.move(preset=pos, callback=switch)
            return


def main():
    with midi:
        while True:
            message = midi.get()
            if message:
                process(message)
                time.sleep(0.5)
            elif atem.program != lastAtemPos:
                # Detected somebody else changpush
                # ed
                # the program.  Assume cameras moved, too.
                for camera in cameras:
                    camera.preset = Pos.UNKNOWN


if __name__ == '__main__':
    main()
