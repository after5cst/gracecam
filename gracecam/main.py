import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%M:%S')  # datefmt='%Y-%m-%d %H:%M:%S'

try:
    from .worker import worker
except ImportError:
    from worker import worker

if __name__ == '__main__':
    worker()
