/**
 * FocusFriend — Custom JavaScript
 * Handles: focus timer, breathing animation, break reminders, UI interactions
 */

// ============================================================
// Focus Timer
// ============================================================

let focusTimerId = null;
let focusRemainingSeconds = 0;
let focusTotalSeconds = 0;

function focusStartTimer(durationMinutes) {
    focusTotalSeconds = durationMinutes * 60;
    focusRemainingSeconds = focusTotalSeconds;
    focusUpdateDisplay();
    focusShowTimer();

    if (focusTimerId) clearInterval(focusTimerId);

    focusTimerId = setInterval(() => {
        focusRemainingSeconds--;
        focusUpdateDisplay();

        if (focusRemainingSeconds <= 300) {
            // 5-minute warning
            const timerEl = document.getElementById('ff-focus-timer');
            if (timerEl) timerEl.classList.add('warning');
        }

        if (focusRemainingSeconds <= 0) {
            focusComplete();
        }
    }, 1000);
}

function focusPauseTimer() {
    if (focusTimerId) {
        clearInterval(focusTimerId);
        focusTimerId = null;
    }
}

function focusResumeTimer() {
    if (focusRemainingSeconds > 0 && !focusTimerId) {
        focusTimerId = setInterval(() => {
            focusRemainingSeconds--;
            focusUpdateDisplay();
            if (focusRemainingSeconds <= 0) focusComplete();
        }, 1000);
    }
}

function focusStopTimer() {
    if (focusTimerId) {
        clearInterval(focusTimerId);
        focusTimerId = null;
    }
    focusHideTimer();
}

function focusUpdateDisplay() {
    const mins = Math.floor(focusRemainingSeconds / 60);
    const secs = focusRemainingSeconds % 60;
    const display = document.getElementById('ff-focus-timer');
    if (display) {
        display.textContent =
            String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
}

function focusShowTimer() {
    const timer = document.getElementById('ff-focus-timer');
    if (timer) timer.style.display = 'block';
}

function focusHideTimer() {
    const timer = document.getElementById('ff-focus-timer');
    if (timer) {
        timer.style.display = 'none';
        timer.classList.remove('warning');
    }
}

function focusComplete() {
    clearInterval(focusTimerId);
    focusTimerId = null;

    const artEl = document.querySelector('.ff-pip-art textarea');
    if (artEl) {
        artEl.classList.add('ff-celebrate');
        setTimeout(() => artEl.classList.remove('ff-celebrate'), 1500);
    }

    // Trigger a Gradio event to notify the Python backend
    const event = new CustomEvent('focusfriend:focus-complete', {
        detail: { duration: focusTotalSeconds / 60 }
    });
    document.dispatchEvent(event);
}

function focusGetRemaining() {
    return focusRemainingSeconds;
}

// ============================================================
// Breathing Animation
// ============================================================

let breatheIntervalId = null;
let breathePhaseIndex = 0;
let breatheSecondsInPhase = 0;

const BREATHE_PATTERNS = {
    '4-7-8': [
        { duration: 4, phase: 'in', label: 'Inhale' },
        { duration: 7, phase: 'hold', label: 'Hold' },
        { duration: 8, phase: 'out', label: 'Exhale' },
    ],
    'box': [
        { duration: 4, phase: 'in', label: 'Inhale' },
        { duration: 4, phase: 'hold', label: 'Hold' },
        { duration: 4, phase: 'out', label: 'Exhale' },
        { duration: 4, phase: 'hold', label: 'Hold' },
    ],
    'simple': [
        { duration: 4, phase: 'in', label: 'Inhale' },
        { duration: 6, phase: 'out', label: 'Exhale' },
    ],
};

function breatheStart(technique) {
    breatheStop();
    const pattern = BREATHE_PATTERNS[technique] || BREATHE_PATTERNS['4-7-8'];
    breathePhaseIndex = 0;
    breatheSecondsInPhase = 0;

    const pipEl = document.querySelector('.ff-pip-art textarea');
    const guideEl = document.getElementById('ff-breathe-guide');

    breatheIntervalId = setInterval(() => {
        const phase = pattern[breathePhaseIndex % pattern.length];

        if (breatheSecondsInPhase === 0) {
            // Update Pip's expression
            if (pipEl) {
                pipEl.classList.remove('ff-breathing-in', 'ff-breathing-out');
                if (phase.phase === 'in') {
                    pipEl.classList.add('ff-breathing-in');
                } else if (phase.phase === 'out') {
                    pipEl.classList.add('ff-breathing-out');
                }
            }
            // Update guide text
            if (guideEl) {
                guideEl.textContent = phase.label + ' (' + phase.duration + 's)';
            }
        }

        breatheSecondsInPhase++;

        if (breatheSecondsInPhase >= phase.duration) {
            breatheSecondsInPhase = 0;
            breathePhaseIndex++;
        }
    }, 1000);
}

function breatheStop() {
    if (breatheIntervalId) {
        clearInterval(breatheIntervalId);
        breatheIntervalId = null;
    }
    const pipEl = document.querySelector('.ff-pip-art textarea');
    if (pipEl) {
        pipEl.classList.remove('ff-breathing-in', 'ff-breathing-out');
    }
}

// ============================================================
// Break Reminder
// ============================================================

let breakReminderId = null;
let lastActivityTime = Date.now();

function breakReminderStart(intervalMinutes) {
    breakReminderStop();
    breakReminderId = setInterval(() => {
        const idleMs = Date.now() - lastActivityTime;
        const idleMinutes = idleMs / 60000;
        if (idleMinutes >= intervalMinutes) {
            const event = new CustomEvent('focusfriend:break-reminder', {
                detail: { idleMinutes: Math.round(idleMinutes) }
            });
            document.dispatchEvent(event);
        }
    }, 60000); // Check every minute
}

function breakReminderStop() {
    if (breakReminderId) {
        clearInterval(breakReminderId);
        breakReminderId = null;
    }
}

function breakRecordActivity() {
    lastActivityTime = Date.now();
}

// Track user activity
document.addEventListener('click', breakRecordActivity);
document.addEventListener('keydown', breakRecordActivity);

// ============================================================
// Pip Mood Animations
// ============================================================

function pipSetMood(mood) {
    const artEl = document.querySelector('.ff-pip-art textarea');
    if (!artEl) return;

    // Remove all mood classes
    artEl.classList.remove(
        'ff-breathing-in', 'ff-breathing-out', 'ff-celebrate'
    );

    // Add mood-specific class
    if (mood === 'celebrate') {
        artEl.classList.add('ff-celebrate');
        setTimeout(() => artEl.classList.remove('ff-celebrate'), 1500);
    }
}

// ============================================================
// Page Load Initialization
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('FocusFriend initialized ✦');
    breakRecordActivity();
});

// Expose functions globally so Gradio can call them
window.focusfriend = {
    focusStartTimer,
    focusPauseTimer,
    focusResumeTimer,
    focusStopTimer,
    focusGetRemaining,
    breatheStart,
    breatheStop,
    breakReminderStart,
    breakReminderStop,
    pipSetMood,
};
