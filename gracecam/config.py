try:
    from .camera import Pos, Camera
    from .midi_reader import MIDIReader
except ImportError:
    from camera import Pos, Camera
    from midi_reader import MIDIReader

from collections import defaultdict

# TESTING: Choose 'loop' for Windows testing, 'IAC' for OSX production
midi = MIDIReader(port_name='IAC')
# midi = MIDIReader(port_name='loop')

cameras = (
    Camera(name='booth', ip_address='192.168.2.109'),
    Camera(name='left', ip_address='192.168.2.107'),
    Camera(name='center', ip_address='192.168.2.106'),
    Camera(name='right', ip_address='192.168.2.108'),
)
for index, camera in enumerate(cameras):
    camera.atem = index + 1

# TESTING: Use .250 for Windows testing, .105 for OSX production
ATEM_IP = "192.168.2.105"
# ATEM_IP = "192.168.1.250"

midi_to_pos = defaultdict(lambda: Pos.UNKNOWN)
midi_to_pos["C"] = Pos.PULPIT
midi_to_pos["C#"] = Pos.PULPIT
midi_to_pos["D"] = Pos.LEADER
midi_to_pos["D#"] = Pos.LEADER
midi_to_pos["E"] = Pos.WIDE
midi_to_pos["F"] = Pos.ORGAN
midi_to_pos["F#"] = Pos.ORGAN
midi_to_pos["G"] = Pos.MIDDLE
midi_to_pos["G#"] = Pos.MIDDLE
midi_to_pos["A"] = Pos.PIANO
midi_to_pos["A#"] = Pos.PIANO


standby_positions = [
    Pos.LEADER,
    Pos.PULPIT
]

program_staging = {
    'booth': dict(preview='right', standby='left'),
    'left': dict(preview='right', standby='booth'),
    'center': dict(preview='left', standby='booth'),
    'right': dict(preview='left', standby='booth'),
}
# multiple entries of the same type in 'randoms' increase
# the odds of it being selected.
randoms = [
    Pos.LEADER,
    Pos.ORGAN,
    Pos.MIDDLE,
    Pos.PIANO,
    Pos.WIDE
]
