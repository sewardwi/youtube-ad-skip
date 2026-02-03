"""
YouTube Ad Skipper - Native Mouse Click Version
Runs in background and clicks the skip button using real mouse input.

Install: pip install -r requirements.txt
Run: python youtube-skipper-native.py

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
import threading
import platform
from PIL import ImageGrab
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont

# Windows DPI awareness
if platform.system() == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except:
        pass

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True


def get_resource_path(filename):
    """Get path to resource, works for dev and PyInstaller."""
    if getattr(sys, '_MEIPASS', None):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


SKIP_BUTTON_IMAGE = get_resource_path('skip_button.png')


def find_skip_button():
    """Locate the skip button on all screens using OpenCV template matching."""
    try:
        # Capture all screens
        try:
            screenshot = ImageGrab.grab(all_screens=True)
        except:
            screenshot = ImageGrab.grab()

        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        # Load template
        template = cv2.imread(SKIP_BUTTON_IMAGE, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return None

        # Try multiple scales for different DPI
        best_match = None
        best_confidence = 0

        for scale in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            if scale != 1.0:
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                if width < 10 or height < 10:
                    continue
                scaled_template = cv2.resize(template, (width, height))
            else:
                scaled_template = template

            result = cv2.matchTemplate(screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_confidence:
                best_confidence = max_val
                h, w = scaled_template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                best_match = (center_x, center_y)

        if best_match and best_confidence >= 0.6:
            # Convert screenshot pixels to screen coordinates
            # Get the screenshot and screen sizes
            screenshot_width = screenshot.size[0]
            screen_size = pyautogui.size()
            scale_factor = screenshot_width / screen_size[0]

            # Convert to screen coordinates
            screen_x = int(best_match[0] / scale_factor)
            screen_y = int(best_match[1] / scale_factor)

            return (screen_x, screen_y, best_confidence)

    except Exception:
        pass

    return None


def click_at(x, y):
    """Perform a real mouse click at coordinates."""
    pyautogui.click(x, y)


class SignalEmitter(QObject):
    """Helper class to emit signals from worker thread."""
    update_status = Signal(str, int)
    stop_requested = Signal()


class YouTubeAdSkipper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.thread = None
        self.clicks_count = 0
        self.signals = SignalEmitter()

        self.signals.update_status.connect(self._on_status_update)
        self.signals.stop_requested.connect(self._stop)

        self.image_found = os.path.exists(SKIP_BUTTON_IMAGE)

        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        self.setWindowTitle("YouTube Ad Skipper")
        self.setFixedSize(300, 220)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("YouTube Ad Skipper")
        title.setFont(QFont("Helvetica", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # Status row
        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignCenter)

        status_text = QLabel("Status:")
        status_layout.addWidget(status_text)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: gray; font-size: 16px;")
        status_layout.addWidget(self.status_dot)

        self.status_label = QLabel("Stopped")
        self.status_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.status_label)

        layout.addLayout(status_layout)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: gray; font-size: 12px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Counter
        self.counter_label = QLabel("Ads skipped: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.counter_label)

        layout.addSpacing(5)

        # Toggle button
        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.setFixedHeight(35)
        self.toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_btn)

        # Warning if image not found
        if not self.image_found:
            self.toggle_btn.setEnabled(False)
            warning = QLabel("skip_button.png not found!\nSee setup instructions.")
            warning.setStyleSheet("color: red;")
            warning.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning)

        layout.addStretch()

    def _center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.running = True
        self.toggle_btn.setText("Stop")
        self.status_label.setText("Running")
        self.status_label.setStyleSheet("color: #22c55e;")
        self.status_dot.setStyleSheet("color: #22c55e; font-size: 16px;")

        self.thread = threading.Thread(target=self._skipper_loop, daemon=True)
        self.thread.start()

    def _stop(self):
        self.running = False
        self.toggle_btn.setText("Start")
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("color: gray;")
        self.status_dot.setStyleSheet("color: gray; font-size: 16px;")
        self.info_label.setText("")

    def _skipper_loop(self):
        while self.running:
            try:
                result = find_skip_button()

                if result:
                    x, y, confidence = result
                    click_at(x, y)
                    self.clicks_count += 1
                    self.signals.update_status.emit(f"Clicked! ({confidence:.0%} match)", self.clicks_count)
                    time.sleep(2)
                else:
                    self.signals.update_status.emit("Scanning...", self.clicks_count)
                    time.sleep(0.5)

            except pyautogui.FailSafeException:
                self.signals.update_status.emit("Failsafe triggered", self.clicks_count)
                self.signals.stop_requested.emit()
                break
            except Exception:
                time.sleep(0.5)

    def _on_status_update(self, status, count):
        self.info_label.setText(status)
        self.counter_label.setText(f"Ads skipped: {count}")

    def closeEvent(self, event):
        self.running = False
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = YouTubeAdSkipper()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
