"""
Logging utility for the RPG game.
"""

import os
import datetime

class Logger:
    """Simple logging utility."""
    
    def __init__(self, log_file="game.log"):
        """Initialize the logger."""
        self.log_file = log_file
        # Clear the log file at startup
        with open(self.log_file, 'w') as f:
            f.write("=== New Game Session ===\n")
            
    def log(self, message: str):
        """Log a message to both console and file."""
        # Print to console
        print(message)
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(f"{message}\n")
            
    def debug(self, message: str):
        """Log a debug message to both console and file."""
        debug_msg = f"DEBUG: {message}"
        print(debug_msg)
        with open(self.log_file, 'a') as f:
            f.write(f"{debug_msg}\n")
            
    def error(self, message: str):
        """Log an error message to both console and file."""
        error_msg = f"ERROR: {message}"
        print(error_msg)
        with open(self.log_file, 'a') as f:
            f.write(f"{error_msg}\n")
            
# Global logger instance
logger = Logger() 