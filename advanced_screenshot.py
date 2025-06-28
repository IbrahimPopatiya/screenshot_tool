"""
Advanced Screenshot Tool with Floating Preview Window
====================================================

This application provides an advanced screenshot functionality with the following features:
- Global hotkey activation for taking screenshots
- Area selection overlay for precise screenshot capture
- Floating preview window with save/destroy options
- Auto-start capability on Windows startup
- Persistent hotkey settings
- Zoom functionality in preview window

Author: [Ibrahim Popatiya]
Version: 1.0
"""

import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import pyautogui
import tempfile
import os
import keyboard
import json
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
import os
import sys
from PyQt5.QtCore import QThread
import shutil
import win32com.client
import time

def setup_autostart():
    """
    Sets up the application to start automatically when Windows boots up.
    
    This function:
    1. Creates a batch file that launches the application
    2. Creates a Windows shortcut in the Startup folder
    3. Only creates the shortcut if it doesn't already exist
    
    The batch file ensures the application runs from the correct directory
    and the shortcut makes it start automatically with Windows.
    """
    # Paths for auto-start setup
    startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    exe_dir = os.path.dirname(sys.executable)  # Directory where .exe runs from
    bat_path = os.path.join(exe_dir, "start_advanced_screenshot.bat")
    shortcut_path = os.path.join(startup_dir, "advanced_screenshot.lnk")

    # Check if shortcut already exists to avoid duplicates
    if not os.path.exists(shortcut_path):
        # Create .bat file that launches the application
        with open(bat_path, "w") as f:
            f.write(f'@echo off\ncd /d "{exe_dir}"\nstart "" "advanced_screenshot.exe"\n')

        # Create Windows shortcut in Startup folder
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = bat_path
        shortcut.WorkingDirectory = exe_dir
        shortcut.WindowStyle = 1  # Normal window
        shortcut.Save()

        print("✅ Auto-start shortcut added to Startup folder")

# ------------------- SETTINGS MANAGEMENT -------------------
SETTINGS_FILE = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "settings.json")

def save_hotkey(hotkey):
    """
    Saves the user's preferred hotkey to a JSON settings file.
    
    Args:
        hotkey (str): The hotkey combination to save (e.g., "f2", "ctrl+r")
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"hotkey": hotkey}, f)

def load_hotkey():
    """
    Loads the previously saved hotkey from the settings file.
    
    Returns:
        str: The saved hotkey, or None if no settings file exists or is invalid
    """
    try:
        with open("settings.json", "r") as f:
            hotkey = json.load(f).get("hotkey")
            if hotkey and isinstance(hotkey, str):
                return hotkey.strip().lower()
    except Exception as e:
        print(f"⚠️ Failed to load hotkey: {e}")
    return None

# ------------------- GUI HOTKEY DIALOG -------------------
class HotkeyDialog(QDialog):
    """
    A dialog window that allows users to set their preferred screenshot hotkey.
    
    This dialog captures keyboard input and displays the selected hotkey combination
    in real-time, allowing users to see what they're selecting before confirming.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set Screenshot Hotkey")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.hotkey = None

        # Create UI elements
        self.label = QLabel("Press your desired hotkey combination (e.g., F2, Ctrl+R)...")
        self.label.setAlignment(Qt.AlignCenter)
        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignCenter)
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.info)
        layout.addWidget(self.ok_btn)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """
        Handles key press events to capture hotkey combinations.
        
        This method:
        1. Detects modifier keys (Ctrl, Alt, Shift, Win)
        2. Captures the main key
        3. Combines them into a hotkey string
        4. Updates the display and enables the OK button
        """
        key_seq = []
        # Check for modifier keys
        if event.modifiers() & Qt.ControlModifier:
            key_seq.append("ctrl")
        if event.modifiers() & Qt.AltModifier:
            key_seq.append("alt")
        if event.modifiers() & Qt.ShiftModifier:
            key_seq.append("shift")
        if event.modifiers() & Qt.MetaModifier:
            key_seq.append("win")
        
        # Get the main key
        key = event.key()
        key_name = QtGui.QKeySequence(key).toString().lower()
        if key_name and key_name not in ["ctrl", "alt", "shift", "win"]:
            key_seq.append(key_name)
        
        # Combine into hotkey string
        self.hotkey = "+".join(key_seq)
        self.info.setText(f"Selected: {self.hotkey}")
        self.ok_btn.setEnabled(True)

def get_user_hotkey_gui():
    """
    Shows the hotkey selection dialog and returns the user's choice.
    
    Returns:
        str: The selected hotkey combination
    """
    dialog = HotkeyDialog()
    dialog.exec_()
    return dialog.hotkey

# ------------------- UTILITY FUNCTIONS -------------------
def get_next_available_filename(base_name="screenshot", ext=".png", folder="."):
    """
    Generates a unique filename by appending a number if the file already exists.
    
    Args:
        base_name (str): Base name for the file
        ext (str): File extension
        folder (str): Target folder path
    
    Returns:
        str: Full path to the next available filename
    """
    i = 1
    while True:
        filename = f"{base_name}{i}{ext}"
        full_path = os.path.join(folder, filename)
        if not os.path.exists(full_path):
            return full_path
        i += 1

def get_pictures_screenshot_folder():
    """
    Creates and returns the path to a Screenshots folder in the user's Pictures directory.
    
    Returns:
        str: Path to the Screenshots folder
    """
    pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
    screenshot_folder = os.path.join(pictures_dir, "Screenshots")
    os.makedirs(screenshot_folder, exist_ok=True)
    return screenshot_folder

# ------------------- FLOATING PREVIEW WINDOW -------------------
class FloatingScreenshotWindow(QtWidgets.QWidget):
    """
    A floating window that displays the captured screenshot with save/destroy options.
    
    Features:
    - Draggable window
    - Zoom functionality (Ctrl + Mouse Wheel)
    - Save button to save the screenshot
    - Destroy button to close and delete the temporary file
    - Always on top behavior
    """
    def __init__(self, image_path, position=None):
        super().__init__()
        # Window setup - always on top, no frame, transparent background
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.image_path = image_path
        self._drag_active = False
        self._drag_position = None
        self.zoom_factor = 1.0
        self.original_pixmap = QtGui.QPixmap(self.image_path)
        self.init_ui(position)

    def init_ui(self, position):
        """Initializes the user interface for the floating window."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image display label
        self.img_label = QtWidgets.QLabel()
        self.img_label.setAlignment(QtCore.Qt.AlignCenter)
        self.img_label.setPixmap(self.original_pixmap)
        layout.addWidget(self.img_label)

        # Button row at the bottom
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.destroy_btn = QtWidgets.QPushButton("Destroy")
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.destroy_btn)
        btn_row.setContentsMargins(0, 0, 10, 10)
        layout.addLayout(btn_row)

        # Connect button signals
        self.save_btn.clicked.connect(self.save_image)
        self.destroy_btn.clicked.connect(self.close_window)

        self.setLayout(layout)
        self.adjustSize()
        self.resize(self.original_pixmap.size().width(), self.original_pixmap.size().height() + 50)

        # Position the window
        if position:
            self.move(position)
        else:
            self.move(200, 200)

        self.show()

    def save_image(self):
        """
        Opens a file dialog to save the screenshot to a permanent location.
        
        The dialog defaults to the Screenshots folder in Pictures with an auto-generated filename.
        """
        folder = get_pictures_screenshot_folder()
        file_path = get_next_available_filename(folder=folder)
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            file_path,
            "PNG Files (*.png)",
            options=options
        )
        if file_path:
            QtGui.QPixmap(self.image_path).save(file_path, "PNG")
            print(f"\u2705 Screenshot saved as {file_path}")

    def close_window(self):
        """
        Closes the window and deletes the temporary screenshot file.
        
        This ensures no temporary files are left behind when the user
        chooses to destroy the screenshot instead of saving it.
        """
        if os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except Exception as e:
                print(f"⚠️ Failed to delete temp image: {e}")
        self.hide()        
        self.deleteLater()  # ✅ safer cleanup

    def mousePressEvent(self, event):
        """Handles mouse press events for window dragging."""
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handles mouse move events for window dragging."""
        if self._drag_active and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handles mouse release events for window dragging."""
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = False
            event.accept()

    def wheelEvent(self, event):
        """
        Handles mouse wheel events for zooming functionality.
        
        Zoom is activated by holding Ctrl and scrolling the mouse wheel.
        Zoom in: Scroll up
        Zoom out: Scroll down
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                self.zoom_factor *= 1.1  # Zoom in
            else:
                self.zoom_factor /= 1.1  # Zoom out
            self.apply_zoom()

    def apply_zoom(self):
        """
        Applies the current zoom factor to the displayed image.
        
        This method scales the original image according to the zoom factor
        while maintaining aspect ratio and smooth transformation.
        """
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_pixmap.size() * self.zoom_factor,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.img_label.setPixmap(scaled_pixmap)
        self.resize(scaled_pixmap.width(), scaled_pixmap.height() + 50)

# ------------------- SCREENSHOT SELECTION OVERLAY -------------------
class Overlay(QtWidgets.QWidget):
    """
    A full-screen overlay that allows users to select an area for screenshot capture.
    
    Features:
    - Semi-transparent overlay covering the entire screen
    - Visual selection rectangle with blue border
    - Real-time size display (width x height)
    - Cross cursor for precise selection
    """
    def __init__(self):
        super().__init__()
        # Window setup - full screen, no frame, always on top, tool window
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.start = None
        self.end = None
        self.selection_rect = None
        self.show()

    def paintEvent(self, event):
        """
        Custom paint event that draws the overlay and selection rectangle.
        
        This method:
        1. Fills the entire screen with a semi-transparent dark overlay
        2. Clears the selected area to show the screen content
        3. Draws a blue border around the selection
        4. Displays the selection dimensions
        """
        painter = QtGui.QPainter(self)
        # Semi-transparent overlay
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 150))
        
        if self.start and self.end:
            selection = QtCore.QRect(self.start, self.end).normalized()
            # Clear the selected area to show screen content
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.fillRect(selection, QtCore.Qt.transparent)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            
            # Draw blue border around selection
            pen = QtGui.QPen(QtGui.QColor(0, 120, 215), 2)
            painter.setPen(pen)
            painter.drawRect(selection)
            
            # Display selection dimensions
            w, h = selection.width(), selection.height()
            size_text = f"{w} x {h} px"
            font = QtGui.QFont()
            font.setPointSize(10)
            painter.setFont(font)
            text_rect = QtCore.QRect(selection.left(), selection.top() - 25, 100, 20)
            painter.setPen(QtGui.QColor(255,255,255))
            painter.drawText(text_rect, QtCore.Qt.AlignLeft, size_text)

    def mousePressEvent(self, event):
        """Handles mouse press to start selection."""
        if event.button() == QtCore.Qt.LeftButton:
            self.start = event.pos()
            self.end = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        """Handles mouse move to update selection rectangle."""
        if self.start:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release to finalize selection and capture screenshot.
        
        When the user releases the mouse button:
        1. Finalizes the selection rectangle
        2. Hides the overlay
        3. Captures the selected area using pyautogui
        4. Creates a temporary file
        5. Opens the floating preview window
        """
        if event.button() == QtCore.Qt.LeftButton and self.start:
            self.end = event.pos()
            self.update()
            selection = QtCore.QRect(self.start, self.end).normalized()
            self.hide()
            QtWidgets.QApplication.processEvents()
            QtCore.QThread.msleep(100)  # Small delay for smooth transition
            
            # Calculate screenshot coordinates
            geo = self.geometry()
            x = geo.x() + selection.x()
            y = geo.y() + selection.y()
            w = selection.width()
            h = selection.height()
            
            # Capture screenshot if selection is large enough
            if w > 5 and h > 5:
                screenshot = pyautogui.screenshot(region=(x, y, w, h))
                temp_file = tempfile.mktemp(suffix='.png')
                screenshot.save(temp_file)
                global_pos = QtGui.QCursor.pos()
                floating_window = FloatingScreenshotWindow(temp_file, position=QtCore.QPoint(x, y))
                floating_windows.append(floating_window)

            QtCore.QTimer.singleShot(200, self.close)

# ------------------- HOTKEY LISTENER -------------------
class HotkeyListener(QtCore.QObject):
    """
    A QObject that listens for global hotkey presses and emits a signal when triggered.
    
    This class uses the keyboard library to register a global hotkey that works
    even when the application doesn't have focus.
    """
    trigger_overlay = QtCore.pyqtSignal()  # Signal emitted when hotkey is pressed

    def __init__(self, hotkey):
        super().__init__()
        self.hotkey = hotkey

    def start_listening(self):
        """Registers the hotkey with the keyboard library."""
        keyboard.add_hotkey(self.hotkey, self.trigger_overlay.emit)

def launch_overlay():
    """
    Creates and shows a new screenshot selection overlay.
    
    This function is called when the hotkey is pressed and creates
    a new Overlay instance for area selection.
    """
    overlay = Overlay()
    overlay.show()
    overlays.append(overlay)

# ------------------- MAIN APPLICATION ENTRY POINT -------------------
if __name__ == "__main__":
    # Wait 5 seconds before starting to allow system to stabilize
    time.sleep(5)
    
    # Setup auto-start functionality
    setup_autostart()
    
    # Initialize Qt application
    app = QtWidgets.QApplication(sys.argv)
    overlays = []  # Keep track of active overlays
    floating_windows = []  # Keep track of floating preview windows

    # Load or get user hotkey
    hotkey = load_hotkey()
    if not hotkey:
        hotkey = get_user_hotkey_gui()
        save_hotkey(hotkey)

    print(f"🟢 Press {hotkey.upper()} to snip and preview with floating buttons.")
    
    # Setup hotkey listener
    hotkey_listener = HotkeyListener(hotkey)
    hotkey_listener.trigger_overlay.connect(launch_overlay)

    # Start hotkey listener in separate thread
    listener_thread = QtCore.QThread()
    hotkey_listener.moveToThread(listener_thread)
    listener_thread.started.connect(hotkey_listener.start_listening)
    listener_thread.start()

    # Log application start
    with open("log.txt", "a") as log:
        log.write("App started\n")

    # Start the application event loop
    sys.exit(app.exec_())
