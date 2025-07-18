# Cross-Platform Keylogger (Python)

## Security Overview  
- Logs typed characters to a local file with timestamped entries  
- Supports macOS, Linux, and Windows  
- Optional silent mode disables terminal output  
- Buffers keystrokes for efficient log writes  
- Safe shutdown using ESC or Ctrl+C  

## Implementation Summary

### Startup Example
<pre><code>python3 keylogger.py --silent --buffersize 30 --flushinterval 5</code></pre>

### Command-line Arguments
<pre><code>--silent            Disable terminal output  
--logfile PATH      Custom path for log file  
--buffersize N      Buffer size before flush  
--flushinterval S   Time (in seconds) between auto-flushes</code></pre>

### Default Log Paths
<pre><code>macOS:    ~/Documents/keylog.txt  
Linux:    ~/keystrokes.log  
Windows:  %APPDATA%\keystrokes.log</code></pre>

### Requirements
<pre><code>Python 3.x  
pynput (install with: pip install pynput)</code></pre>
