"""
Focus / Pomodoro mode for FocusFriend.

Pip helps you stay focused for timed work sessions.
Standard Pomodoro: 25 min work, 5 min break.
"""

import time
import threading
from typing import Optional, Callable


class FocusSession:
    """Manages a focus/Pomodoro session."""

    def __init__(
        self,
        duration_minutes: int = 25,
        on_complete: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
    ):
        self.duration_seconds = duration_minutes * 60
        self.remaining_seconds = self.duration_seconds
        self.running = False
        self.paused = False
        self.completed = False
        self.on_complete = on_complete
        self.on_tick = on_tick
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the focus timer in a background thread."""
        if self.running:
            return
        self.running = True
        self.paused = False
        self.completed = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def pause(self):
        """Pause the timer."""
        self.paused = True

    def resume(self):
        """Resume a paused timer."""
        self.paused = False

    def stop(self):
        """Stop the timer early."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self):
        """Background timer loop."""
        while self.running and self.remaining_seconds > 0:
            if not self.paused:
                time.sleep(1)
                self.remaining_seconds -= 1
                if self.on_tick:
                    self.on_tick(self.remaining_seconds)
            else:
                time.sleep(0.1)

        if self.remaining_seconds <= 0 and self.running:
            self.completed = True
            self.running = False
            if self.on_complete:
                self.on_complete()

    def get_time_display(self) -> str:
        """Return MM:SS formatted time string."""
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def get_progress(self) -> float:
        """Return progress as a fraction (0.0 to 1.0)."""
        if self.duration_seconds == 0:
            return 1.0
        return 1.0 - (self.remaining_seconds / self.duration_seconds)


# Pre-written Pip messages for focus sessions

FOCUS_START_MESSAGES = [
    "Alright, {duration} minutes of focus. [mood: focus]\n"
    "One task. No phone. I believe in you — and I'm annoyingly persistent.",

    "Focus mode: ON. [mood: determined]\n"
    "{duration} minutes. You've done harder things before breakfast.\n"
    "Let's go.",

    "Here we go. [mood: focus]\n"
    "{duration} minutes of uninterrupted work. I'll keep time.\n"
    "You just do your thing.",
]

FOCUS_COMPLETE_MESSAGES = [
    "Done! {duration} minutes in the books. [mood: celebrate]\n"
    "Doesn't matter what you accomplished — you showed up. That's the hard part.",

    "Time's up. [mood: proud]\n"
    "Take a breath. Stretch. You earned a break.\n"
    "Not a long one though. We're not done yet. 😏",

    "Session complete. [mood: celebrate]\n"
    "Look at you, being all productive.\n"
    "Seriously — good job. Now go drink some water.",
]

BREAK_REMINDER_MESSAGES = [
    "Hey. [mood: break_time]\n"
    "Your eyes have been staring at this screen for a while.\n"
    "20-20-20 rule: look at something 20 feet away for 20 seconds.",

    "Quick check-in. [mood: concerned]\n"
    "Shoulders down. Unclench your jaw. Breathe.\n"
    "Okay, carry on.",

    "Break time. [mood: break_time]\n"
    "Stand up. Walk to the other room and back.\n"
    "Your body will thank you. Your brain will too.",
]
