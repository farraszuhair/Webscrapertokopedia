"""
logger.py - Structured logging system.
Formats logs consistently with timestamp, level, and tags.
"""
import datetime
import sys

def log(tag: str, msg: str, level: str = "INFO"):
    """
    Logs a message to stdout.
    Levels: INFO, WARN, ERROR, DEBUG
    """
    now = datetime.datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",  # Blue
        "WARN": "\033[93m",  # Yellow
        "ERROR": "\033[91m", # Red
        "DEBUG": "\033[90m"  # Gray
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    
    formatted = f"[{now}] {color}[{level}]{reset} [{tag}] {msg}"
    print(formatted, flush=True)

class Logger:
    def __init__(self, tag: str):
        self.tag = tag

    def info(self, msg: str):
        log(self.tag, msg, "INFO")

    def warn(self, msg: str):
        log(self.tag, msg, "WARN")

    def error(self, msg: str):
        log(self.tag, msg, "ERROR")

    def debug(self, msg: str):
        log(self.tag, msg, "DEBUG")
