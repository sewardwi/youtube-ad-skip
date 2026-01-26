"""
YouTube Ad Skipper - Native Mouse Click Version
Runs in background and clicks the skip button using real mouse input.

Install: pip install pyautogui pillow opencv-python
Run: python youtube_skipper_native.py

Setup:
1. Go to YouTube and wait for an ad with a skip button
2. Screenshot JUST the skip button (crop tightly)
3. Save as 'skip_button.png' in the same folder as this script

Note: On macOS, grant accessibility permissions when prompted.
"""

import pyautogui
import time
import sys
import os
from PIL import ImageGrab
import cv2
import numpy as np

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SKIP_BUTTON_IMAGE = 'skip_button.png'


def get_display_scaling():
    """Detect display scaling factor (Retina/HiDPI support)."""
    screenshot = ImageGrab.grab()
    screenshot_width = screenshot.size[0]
    screen_width = pyautogui.size()[0]
    scale = screenshot_width / screen_width
    return scale


def find_skip_button(scale):
    """Locate the skip button on screen using OpenCV template matching."""
    try:
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        template = cv2.imread(SKIP_BUTTON_IMAGE, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return None

        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= 0.7:
            h, w = template.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            # Adjust for display scaling
            screen_x = int(center_x / scale)
            screen_y = int(center_y / scale)

            print(f'[Ad Skipper] Found button at ({screen_x}, {screen_y}) confidence: {max_val:.2f}')
            return (screen_x, screen_y)

    except Exception as e:
        print(f'[Ad Skipper] Error: {e}')

    return None


def click_at(x, y):
    """Perform a real mouse click at coordinates."""
    pyautogui.click(x, y)
    print(f'[Ad Skipper] Clicked at ({x}, {y})')


def main():
    if not os.path.exists(SKIP_BUTTON_IMAGE):
        print(f'[Ad Skipper] ERROR: {SKIP_BUTTON_IMAGE} not found!')
        print()
        print('Setup instructions:')
        print('1. Go to YouTube and wait for an ad with a skip button')
        print('2. Screenshot JUST the skip button (crop it tightly)')
        print(f'3. Save as "{SKIP_BUTTON_IMAGE}" in this folder')
        sys.exit(1)

    scale = get_display_scaling()
    print(f'[Ad Skipper] Detected display scaling: {scale}x')
    print('[Ad Skipper] Running...')
    print('[Ad Skipper] Move mouse to top-left corner to stop')
    print()

    while True:
        try:
            pos = find_skip_button(scale)

            if pos:
                click_at(pos[0], pos[1])
                time.sleep(2)
            else:
                time.sleep(0.5)

        except pyautogui.FailSafeException:
            print('\n[Ad Skipper] Failsafe triggered - exiting.')
            sys.exit(0)
        except KeyboardInterrupt:
            print('\n[Ad Skipper] Stopped.')
            sys.exit(0)


if __name__ == '__main__':
    main()