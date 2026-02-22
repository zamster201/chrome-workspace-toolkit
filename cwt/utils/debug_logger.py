# utils/debug_logger.py

log_callback = None

def set_log_callback(callback):
    global log_callback
    log_callback = callback

def log_debug(message):
    if log_callback:
        log_callback(message)
    else:
        print(message)  # fallback to console

def log(level, msg): log_debug(f"[{level.upper()}] {msg}")

def log_info(msg):
    log_debug(f"[INFO] {msg}")

def log_error(msg):
    log_debug(f"[ERROR] {msg}")