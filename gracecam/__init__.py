"""
gracecam: Main module

Copyright 2021, Joe Marley
Licensed under MIT.
"""

import queue
try:
    # Attempt imports as if we are a package
    from .atem import ATEM
    from .camera import Camera, Pos
    from .config import midi, cameras, midi_to_pos, program_staging, randoms, standby_positions, ATEM_IP
    from .midi_note import MidiNote
except ImportError:
    # Attempt imports as if we're running inside the directory
    from atem import ATEM
    from camera import Camera, Pos
    from config import midi, cameras, midi_to_pos, program_staging, randoms, standby_positions, ATEM_IP
    from midi_note import MidiNote

pending_positions = queue.SimpleQueue()
