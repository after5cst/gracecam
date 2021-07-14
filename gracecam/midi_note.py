class MidiNote:
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    OCTAVES = list(range(11))
    NOTES_IN_OCTAVE = len(NOTES)

    def __init__(self, *, on: bool, channel: int, pitch: int, velocity: int):
        self.on = on
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity

    @property
    def off(self):
        return not self.on

    @property
    def octave(self) -> int:
        """ Return the octave number for the note. """
        return (self.pitch // self.NOTES_IN_OCTAVE) - 2

    @property
    def note(self) -> str:
        """Return a string representation of the note"""
        return self.NOTES[self.pitch % self.NOTES_IN_OCTAVE]

    def __str__(self):
        on_off = 'ON' if self.on else 'OFF'
        return f"MIDI {self.note}{self.octave} {on_off}"

    def __repr__(self):
        on_off = 'On' if self.on else 'Off'
        return f"{{MidiNote{on_off}({self.note}{self.octave})}}"
