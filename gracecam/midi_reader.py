import logging
import queue
from pathlib import Path
from queue import Queue
import rtmidi
from rtmidi.midiutil import open_midiinput
from typing import List, Optional

from gracecam.midi_note import MidiNote

_SCRIPT_DIR = Path(__file__).parent.resolve()
_LOG = logging.getLogger()


class MIDIReader:
    """
    Read MIDI "NOTE ON" messages asynchronously (via callback)
    and make them available via the messages attribute.

    This is a context manager object, use similar to:

    with MIDIReader(port='myname') as reader:
        # ...
        pass
    """
    def __init__(self, *, port_name: str, channel: int = 0):
        self.channel = channel
        self.messages = Queue()
        self.midi_in = None  # type: Optional[rtmidi.MidiIn]
        self.port_name = port_name

    @staticmethod
    def valid_ports() -> List[str]:
        return rtmidi.MidiIn().get_ports()

    def __enter__(self):
        if self.midi_in:
            return  # already entered
        try:
            _LOG.debug("Opening MIDI port '{}'".format(self.port_name))
            self.midi_in, port_name = open_midiinput(
                self.port_name, interactive=False)
        except rtmidi.InvalidPortError as e:
            raise ValueError("Invalid port '{}'.  Choose one of {}".format(
                self.port_name, MIDIReader.valid_ports())) from e

        _LOG.debug("MIDI port {} opened as {}".format(
            self.port_name, port_name))
        self.midi_in.set_callback(self._callback)
        return self

    def __exit__(self, *args, **kwargs):
        if self.midi_in:
            _LOG.debug("Closing MIDI port {}".format(self.port_name))
            temp = self.midi_in
            self.midi_in = None
            # temp.cancel_callback()
            temp.close_port()
            del temp
        self.midi_in = None
        self.port_name = "None"

    def _callback(self, event, data=None):
        """
        Callback for MIDI messages (called from rtmidi)
        """
        midi_message, delta_time = event
        status_byte = midi_message[0]
        if not (0x80 <= status_byte < 0xA0):
            # Not a note, too low/high.
            item = f"MIDI Message {midi_message}"
        elif 0x90 > status_byte:
            # Note OFF message
            item = MidiNote(on=False,
                            channel=status_byte - 0x80,
                            pitch=midi_message[1],
                            velocity=midi_message[2])
            if item.on:  # Save ON messages only.
                self.messages.put(item)
        else:
            # Note ON message
            item = MidiNote(on=True,
                            channel=status_byte - 0x90,
                            pitch=midi_message[1],
                            velocity=midi_message[2])
            self.messages.put(item)
        _LOG.debug("Found MIDI Message {}".format(item))

    def get(self) -> Optional[MidiNote]:
        """ Return a message if it is available. """
        try:
            return self.messages.get(timeout=30)
        except queue.Empty:
            return None
