from flask import Flask
import logging
import threading
import time

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%M:%S')  # datefmt='%Y-%m-%d %H:%M:%S'

try:
    worker = None
    from . import pending_positions, Pos
    from .worker import worker
except ImportError:
    from __init__ import pending_positions, Pos
    from worker import worker

app = Flask(__name__)
MINIMUM_PRESET_DELAY = 5.0
last_preset_time = time.time() - MINIMUM_PRESET_DELAY


@app.route("/preset/<number>")
def select_preset(number):
    global last_preset_time
    now = time.time()
    if last_preset_time < (now - MINIMUM_PRESET_DELAY):
        pos = Pos(int(number))
        pending_positions.put(pos)
        last_preset_time = now
        return f"{pos.name}"
    logging.debug(f"Preset {number} ignored:  too soon.")
    return "Not yet."


def main():
    # Start the worker thread
    threading.Thread(target=worker, daemon=True).start()
    # And then start Flask (runs forever)
    app.run(port=8050)


if __name__ == '__main__':
    main()
