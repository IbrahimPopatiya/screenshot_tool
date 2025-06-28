# Advanced Screenshot Tool

A powerful screenshot application built with PyQt5 that provides advanced screenshot functionality with a floating preview window, area selection, and global hotkey support.

## 🚀 Features

### Core Functionality
- **Global Hotkey Support**: Take screenshots from anywhere using customizable hotkeys
- **Area Selection**: Click and drag to select specific screen areas
- **Floating Preview Window**: View screenshots immediately after capture
- **Auto-start**: Automatically starts with Windows boot
- **Persistent Settings**: Remembers your preferred hotkey

### Advanced Features
- **Zoom Functionality**: Ctrl + Mouse Wheel to zoom in/out on preview
- **Draggable Windows**: Move preview windows anywhere on screen
- **Smart File Naming**: Auto-generates unique filenames
- **Organized Storage**: Saves screenshots to Pictures/Screenshots folder
- **Temporary File Management**: Automatically cleans up unsaved screenshots

## 📋 Requirements

### System Requirements
- Windows 10/11
- Python 3.7 or higher
- Administrative privileges (for auto-start setup)

### Python Dependencies
```
keyboard
pyautogui
pillow
PyQt5
pyinstaller
pywin32
```

## 🛠️ Installation

### Method 1: Using Requirements File
1. Clone or download this repository
2. Open command prompt in the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python advanced_screenshot.py
   ```

### Method 2: Manual Installation
1. Install required packages:
   ```bash
   pip install PyQt5 pyautogui keyboard pywin32
   ```
2. Run the application:
   ```bash
   python advanced_screenshot.py
   ```

### Building Executable
To create a standalone .exe file:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed advanced_screenshot.py
```

## 🎯 Usage

### First Run
1. Launch the application
2. A dialog will appear asking you to set a hotkey
3. Press your desired key combination (e.g., F2, Ctrl+R, Alt+S)
4. Click OK to save your preference

### Taking Screenshots
1. **Activate**: Press your configured hotkey from anywhere
2. **Select Area**: Click and drag to select the area you want to capture
3. **Preview**: A floating window will appear showing your screenshot
4. **Save or Destroy**:
   - Click "Save" to save the screenshot permanently
   - Click "Destroy" to discard the screenshot

### Preview Window Features
- **Drag**: Click and drag the window to move it
- **Zoom**: Hold Ctrl and scroll mouse wheel to zoom in/out
- **Save**: Opens file dialog to save screenshot
- **Destroy**: Closes window and deletes temporary file

## 📁 File Structure

```
screenshot/
├── advanced_screenshot.py    # Main application file
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── settings.json            # User preferences (auto-generated)
├── log.txt                  # Application logs (auto-generated)
└── start_advanced_screenshot.bat  # Auto-start batch file (auto-generated)
```

## 🔧 Configuration

### Hotkey Settings
- Stored in `settings.json`
- Format: `{"hotkey": "f2"}` or `{"hotkey": "ctrl+r"}`
- Supported modifiers: Ctrl, Alt, Shift, Win
- Supported keys: All standard keys (F1-F12, letters, numbers, etc.)

### Auto-start Configuration
- Creates shortcut in Windows Startup folder
- Uses batch file to ensure correct working directory
- Only creates once - won't duplicate on subsequent runs

## 🏗️ Architecture

### Main Components

#### 1. **HotkeyListener** (`HotkeyListener` class)
- Listens for global hotkey presses
- Uses `keyboard` library for system-wide hotkey detection
- Emits signals when hotkey is triggered

#### 2. **Selection Overlay** (`Overlay` class)
- Full-screen transparent overlay
- Handles mouse events for area selection
- Displays selection rectangle with dimensions
- Captures screenshot using `pyautogui`

#### 3. **Floating Preview Window** (`FloatingScreenshotWindow` class)
- Displays captured screenshot
- Provides save/destroy functionality
- Supports dragging and zooming
- Manages temporary file cleanup

#### 4. **Settings Management**
- JSON-based configuration storage
- Hotkey persistence across sessions
- Auto-start setup functionality

### Key Functions

#### `setup_autostart()`
- Creates Windows startup shortcut
- Generates batch file for proper execution
- Prevents duplicate shortcuts

#### `get_user_hotkey_gui()`
- Shows hotkey selection dialog
- Captures keyboard input in real-time
- Validates and saves user preferences

#### `get_pictures_screenshot_folder()`
- Creates organized screenshot storage
- Uses standard Pictures directory
- Ensures folder exists

## 🔍 Technical Details

### Screenshot Process
1. **Hotkey Trigger**: Global hotkey activates overlay
2. **Area Selection**: User drags to select screen area
3. **Capture**: `pyautogui.screenshot()` captures selected region
4. **Temporary Storage**: Screenshot saved to temp file
5. **Preview**: Floating window displays screenshot
6. **User Action**: Save to permanent location or destroy

### Threading
- Hotkey listener runs in separate thread
- Main UI runs in main thread
- Thread-safe signal/slot communication

### File Management
- Temporary files: `tempfile.mktemp()`
- Permanent storage: `~/Pictures/Screenshots/`
- Auto-cleanup on window close
- Unique filename generation

## 🐛 Troubleshooting

### Common Issues

#### Hotkey Not Working
- Ensure application has focus on first run
- Check if hotkey conflicts with other applications
- Try different key combinations

#### Screenshot Capture Issues
- Verify pyautogui permissions
- Check if running as administrator
- Ensure no other screenshot tools are interfering

#### Auto-start Not Working
- Check Windows Startup folder permissions
- Verify batch file exists and is executable
- Run application as administrator once

### Error Messages
- `⚠️ Failed to load hotkey`: Settings file corrupted or missing
- `⚠️ Failed to delete temp image`: File permission issues
- `✅ Auto-start shortcut added`: Successful auto-start setup

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add comments and documentation
5. Test thoroughly
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Use descriptive variable names
- Comment complex logic

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🙏 Acknowledgments

- **PyQt5**: GUI framework
- **pyautogui**: Screenshot capture
- **keyboard**: Global hotkey detection
- **pywin32**: Windows integration

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information

---

**Happy Screenshotting! 📸** 


#### DOWNLOAD EXE FROM RELEASE
⚠️ Windows SmartScreen Warning?
This tool is safe to use. You might see a “Windows protected your PC” message because the app is new and not yet verified by Microsoft.
👉 Click "More info" → then "Run anyway" to continue. 

📥 [Download the latest version](https://github.com/IbrahimPopatiya/screenshot_tool/releases/latest)
