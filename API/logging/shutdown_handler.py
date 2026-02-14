import signal
import threading
import os
import logging
from API.logging.send_telegram_alert import send_telegram_alert


_shutdown_notified = False
_lock = threading.Lock()

logger = logging.getLogger(__name__)

def notify_shutdown(reason: str):
    global _shutdown_notified
    with _lock:
        if _shutdown_notified:
            return
        _shutdown_notified = True
    logger.info(f"API has been stopped: {reason}")
    send_telegram_alert(f"yam transaction report generator: API has been stopped: {reason}")

    # On Windows, if we don't re-raise the interruption, Waitress may keep running.
    if os.name == "nt":
        raise KeyboardInterrupt


def _handle_sigterm(signum, frame):
    notify_shutdown("docker stop")

def _handle_sigint(signum, frame):
    notify_shutdown("ctrl+c")

def install_signal_handlers():
    signal.signal(signal.SIGTERM, _handle_sigterm)
    signal.signal(signal.SIGINT, _handle_sigint)
