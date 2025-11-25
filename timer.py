"""
Timer module providing timer state management.
Supports mock mode for testing purposes.
"""

import time
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class TimerState(Enum):
    """Timer state enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class TimerData:
    """Timer data structure for API responses."""
    state: str
    remaining_seconds: float
    total_seconds: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "state": self.state,
            "remaining_seconds": self.remaining_seconds,
            "total_seconds": self.total_seconds
        }


class Timer:
    """
    Timer class for managing timer state and countdown.
    Supports mock mode for testing.
    """
    
    def __init__(self, mock_mode: bool = False):
        """
        Initialize the timer.
        
        Args:
            mock_mode: If True, use mock time for testing.
        """
        self._mock_mode = mock_mode
        self._mock_current_time: float = 0.0
        
        self._state = TimerState.IDLE
        self._total_seconds: float = 0.0
        self._remaining_seconds: float = 0.0
        self._start_time: Optional[float] = None
        self._pause_remaining: Optional[float] = None
    
    def _get_current_time(self) -> float:
        """Get current time (mock or real)."""
        if self._mock_mode:
            return self._mock_current_time
        return time.time()
    
    def set_mock_time(self, mock_time: float) -> None:
        """Set mock time for testing."""
        if not self._mock_mode:
            raise RuntimeError("Cannot set mock time when not in mock mode")
        self._mock_current_time = mock_time
    
    def advance_mock_time(self, seconds: float) -> None:
        """Advance mock time by specified seconds."""
        if not self._mock_mode:
            raise RuntimeError("Cannot advance mock time when not in mock mode")
        self._mock_current_time += seconds
    
    def start(self, duration_seconds: float) -> bool:
        """
        Start the timer with specified duration.
        
        Args:
            duration_seconds: Duration in seconds.
            
        Returns:
            True if timer started successfully, False otherwise.
        """
        if duration_seconds <= 0:
            return False
        
        self._total_seconds = duration_seconds
        self._remaining_seconds = duration_seconds
        self._start_time = self._get_current_time()
        self._pause_remaining = None
        self._state = TimerState.RUNNING
        return True
    
    def pause(self) -> bool:
        """
        Pause the timer.
        
        Returns:
            True if timer paused successfully, False otherwise.
        """
        if self._state != TimerState.RUNNING:
            return False
        
        self._pause_remaining = self._get_remaining_seconds()
        self._state = TimerState.PAUSED
        return True
    
    def resume(self) -> bool:
        """
        Resume the timer from paused state.
        
        Returns:
            True if timer resumed successfully, False otherwise.
        """
        if self._state != TimerState.PAUSED:
            return False
        
        if self._pause_remaining is not None and self._pause_remaining > 0:
            self._start_time = self._get_current_time()
            self._remaining_seconds = self._pause_remaining
            self._pause_remaining = None
            self._state = TimerState.RUNNING
            return True
        return False
    
    def stop(self) -> bool:
        """
        Stop the timer and reset to idle state.
        
        Returns:
            True if timer stopped successfully, False otherwise.
        """
        if self._state == TimerState.IDLE:
            return False
        
        self._state = TimerState.IDLE
        self._start_time = None
        self._pause_remaining = None
        self._remaining_seconds = 0.0
        return True
    
    def reset(self) -> bool:
        """
        Reset the timer to initial duration and restart.
        
        Returns:
            True if timer reset successfully, False otherwise.
        """
        if self._total_seconds <= 0:
            return False
        
        return self.start(self._total_seconds)
    
    def _get_remaining_seconds(self) -> float:
        """Calculate remaining seconds based on current state."""
        if self._state == TimerState.IDLE:
            return 0.0
        
        if self._state == TimerState.PAUSED:
            return self._pause_remaining if self._pause_remaining else 0.0
        
        if self._start_time is None:
            return 0.0
        
        elapsed = self._get_current_time() - self._start_time
        remaining = self._remaining_seconds - elapsed
        return max(0.0, remaining)
    
    def get_state(self) -> TimerState:
        """Get current timer state."""
        remaining = self._get_remaining_seconds()
        if self._state == TimerState.RUNNING and remaining <= 0:
            self._state = TimerState.IDLE
            self._remaining_seconds = 0.0
        return self._state
    
    def get_data(self) -> TimerData:
        """
        Get current timer data for API response.
        
        Returns:
            TimerData containing current state and timing information.
        """
        state = self.get_state()
        remaining = self._get_remaining_seconds()
        
        return TimerData(
            state=state.value,
            remaining_seconds=round(remaining, 2),
            total_seconds=round(self._total_seconds, 2)
        )
