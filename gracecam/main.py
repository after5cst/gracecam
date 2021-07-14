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


@app.route("/preset/<number>")
def select_preset(number):
    pos = Pos(int(number))
    pending_positions.put(pos)
    time.sleep(10)
    return f"{pos.name}"


def main():
    # Start the worker thread
    threading.Thread(target=worker, daemon=True).start()
    # And then start Flask (runs forever)
    app.run()


if __name__ == '__main__':
    main()
