
try:
    from .camera import Pos, Camera
    from .midi_reader import MIDIReader
except ImportError:
    from camera import Pos, Camera
    from midi_reader import MIDIReader

midi = MIDIReader(port_name='loop')
# Order is important:  The last camera is least likely to be used.
cameras = (
    Camera(name='left', ip_address='192.168.2.105', atem=2),
    Camera(name='right', ip_address='192.168.2.107', atem=4),
    Camera(name='center', ip_address='192.168.2.106', atem=3),
)

ATEM_IP = "192.168.1.250"

midi_to_pos = {
    "C": Pos.PULPIT,
    "C#": Pos.PULPIT,
    "D": Pos.LEADER,
    "D#": Pos.LEADER,
    "E": Pos.WIDE,
    "F": Pos.ORGAN,
    "F#": Pos.ORGAN,
    "G": Pos.MIDDLE,
    "G#": Pos.MIDDLE,
    "A": Pos.PIANO,
    "A#": Pos.PIANO
}

standby_positions = [
    Pos.LEADER,
    Pos.PULPIT
]

randoms = [
    Pos.LEADER,
    Pos.ORGAN,
    Pos.MIDDLE,
    Pos.PIANO
]
