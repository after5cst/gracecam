import logging
from .midi_numbers import number_to_note
from pathlib import Path
from queue import Queue
import rtmidi
from rtmidi.midiutil import open_midiinput, list_input_ports
from typing import List, Optional

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
        if 0x90 <= midi_message[0] < 0xA0:
            # NOTE ON message.
            channel_number = midi_message[0] - 0x90
            pitch = midi_message[1]
            velocity = midi_message[2]

            # For our purposes, we don't care about velocity.
            note = number_to_note(pitch)
            _LOG.debug("Found NOTE ON: {} (channel {})".format(
                note, channel_number))
            self.messages.put(note)

        elif 0x80 <= midi_message[0] < 0x90:
            # NOTE ON message.
            channel_number = midi_message[0] - 0x80
            pitch = midi_message[1]
            # velocity = midi_message[2]

            # For our purposes, we don't care about velocity.
            note = number_to_note(pitch)
            _LOG.debug("Skipping NOTE OFF: {} (channel {})".format(
                note, channel_number))
        else:
            _LOG.debug("Found MIDI Message {}".format(midi_message))
