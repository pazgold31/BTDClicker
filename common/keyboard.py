import ctypes

VALID_LANGUAGE_IDS = [
    0x409  # English - United States
]


def get_keyboard_language():
    """
    Gets the keyboard language in use by the current
    active window process.
    """

    user32 = ctypes.WinDLL('user32', use_last_error=True)

    # Get the current active window handle
    handle = user32.GetForegroundWindow()

    # Get the thread id from that window handle
    thread_id = user32.GetWindowThreadProcessId(handle, 0)

    # Get the keyboard layout id from the thread id
    layout_id = user32.GetKeyboardLayout(thread_id)

    # Extract the keyboard language id from the keyboard layout id
    return layout_id & (2 ** 16 - 1)


def is_language_valid() -> bool:
    return get_keyboard_language() in VALID_LANGUAGE_IDS
