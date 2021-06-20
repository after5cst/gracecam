from gracecam.midi_reader import MIDIReader
import logging
import pytest
import rtmidi
from rtmidi.midiutil import open_midioutput
import time

_LOG = logging.getLogger(__name__)


def write_midi_message(*, port_name: str, count: int = 1):
    """ Write data to the MIDI port so we can test reading it. """
    # The port name (which we got from the reader) has the port number
    # in it.  Since we're opening another one, the port number will
    # apparently change: drop the last "word" which is the port number.
    port_name_without_port_num = port_name.rsplit(' ', 1)[0]
    midi_out, new_port_name = open_midioutput(port_name_without_port_num, interactive=False)

    note_on = [0x90, 60, 112]  # channel 1, middle C, velocity 112
    note_off = [0x80, 60, 0]
    for i in range(count):
        logging.debug("Sending note_on to {}".format(new_port_name))
        midi_out.send_message(note_on)
        logging.debug("Sending note_off to {}".format(new_port_name))
        midi_out.send_message(note_off)
    return midi_out


def get_good_port() -> str:
    """
    Guess at a good port name.  The 'possibilities' are
    names that look promising.  Take the first one that matches.
    """
    possibilities = ['loopMIDI', 'virtual']
    valid_ports = MIDIReader.valid_ports()
    for port in valid_ports:
        for possibility in possibilities:
            if possibility.lower() in port.lower():
                _LOG.debug("Found good port '{}'".format(port))
                return port
    assert False, "Could not find good MIDI port on system"


def test_bad_port_raises_exception():
    # This assumes that 'bad port name' is that : a bad port name.
    with pytest.raises(ValueError):
        with MIDIReader(port_name='bad port name') as reader:
            pass


def test_good_port_succeeds():
    with MIDIReader(port_name=get_good_port()) as reader:
        pass


def test_can_read_midi_message():
    port_name = get_good_port()
    MESSAGE_COUNT = 10
    with MIDIReader(port_name=port_name) as reader:
        # I don't understand why, but we can't close the MIDI out until after
        # MIDI in is done or strange things seem to happen.  Since MIDI out
        # is only happening as a part of test, I avoid it by grabbing it and
        # only closing it at the end.
        midi_out = write_midi_message(port_name=port_name, count=MESSAGE_COUNT)
        for i in range(MESSAGE_COUNT):
            if MESSAGE_COUNT == reader.messages.qsize():
                break
            time.sleep(1)
        # Now sleep just a little longer to make sure we don't get extras.
        time.sleep(1)
    items = list()
    while not reader.messages.empty():
        items.append(reader.messages.get())
    assert len(items) == MESSAGE_COUNT
    _LOG.info(str(items))
    midi_out.close_port()
    del midi_out


def test_again():
    test_can_read_midi_message()

# import rtmidi
#
# def test_example():
#     midiout = rtmidi.MidiIn()
#     available_ports = midiout.get_ports()
#     assert available_ports == []

#!/usr/bin/env python
#
# midiin_callback.py
#
"""Show how to receive MIDI input by setting a callback function."""

# import logging
# import sys
# import time
#
# from rtmidi.midiutil import open_midiinput
#
# log = logging.getLogger('midiin_callback')
# logging.basicConfig(level=logging.DEBUG)
#
#
# class MidiInputHandler(object):
#     def __init__(self, port):
#         self.port = port
#         self._wallclock = time.time()
#
#     def __call__(self, event, data=None):
#         message, deltatime = event
#         self._wallclock += deltatime
#         print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
#
#
# # Prompts user for MIDI input port, unless a valid port number or name
# # is given as the first argument on the command line.
# # API backend defaults to ALSA on Linux.
# port = sys.argv[1] if len(sys.argv) > 1 else None
#
# try:
#     midiin, port_name = open_midiinput(port)
# except (EOFError, KeyboardInterrupt):
#     sys.exit()
#
# print("Attaching MIDI input callback handler.")
# midiin.set_callback(MidiInputHandler(port_name))
#
# print("Entering main loop. Press Control-C to exit.")
# try:
#     # Just wait for keyboard interrupt,
#     # everything else is handled via the input callback.
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print('')
# finally:
#     print("Exit.")
#     midiin.close_port()
#     del midiin
