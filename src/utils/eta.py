"""
eta.py - Calculates Estimated Time of Arrival for tasks based on progress.
"""
import time
from collections import deque

class ETACalculator:
    def __init__(self, smoothing_window: int = 5):
        """
        Initializes ETA calculator.
        smoothing_window: Number of recent samples to average for smoothing ETA.
        """
        self.start_time = time.perf_counter()
        self.history = deque(maxlen=smoothing_window)
        self.last_pct = 0
    
    def get_eta(self, current_pct: int) -> int | None:
        """
        Calculates smoothed ETA in seconds.
        Returns None if percentage is 0 or 100 (unmeasurable/done).
        """
        if current_pct <= 0 or current_pct >= 100:
            return None
            
        elapsed = time.perf_counter() - self.start_time
        
        # Estimate total time based on current progress
        # If we did X% in Y seconds, 100% takes (Y / (X/100)) seconds
        estimated_total = elapsed / (current_pct / 100.0)
        
        # ETA is total estimated minus elapsed
        raw_eta = max(0.0, estimated_total - elapsed)
        
        # Smooth the ETA so it doesn't jump wildly
        self.history.append(raw_eta)
        smoothed_eta = sum(self.history) / len(self.history)
        
        return int(smoothed_eta)

    def get_elapsed(self) -> int:
        """Returns elapsed time in seconds."""
        return int(time.perf_counter() - self.start_time)
