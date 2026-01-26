"""
Build script to create standalone executable.

Install: pip install -r requirements.txt
Run: python build_executable.py

NOTE: PyInstaller can only build for the OS it's running on.
To create executables for both platforms:
  - Run this script on a Mac to build the macOS app
  - Run this script on Windows to build the Windows exe

Alternatively, use GitHub Actions to build for both (see below).
"""

import subprocess
import sys
import platform

APP_NAME = "YouTubeAdSkipper"
SCRIPT = "youtube-skipper-native.py"


def build():
    current_os = platform.system()
    
    print(f"Building {APP_NAME} for {current_os}...")
    print()
    
    # Base command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", APP_NAME,
    ]
    
    # Add the image file with correct path separator
    if current_os == "Windows":
        cmd.extend(["--add-data", "skip_button.png;."])
    else:
        cmd.extend(["--add-data", "skip_button.png:."])
    
    # macOS: create .app bundle
    if current_os == "Darwin":
        cmd.append("--windowed")
    
    cmd.append(SCRIPT)
    
    subprocess.run(cmd, check=True)
    
    print()
    print("=" * 50)
    print("Build complete!")
    print("=" * 50)
    print()
    
    if current_os == "Darwin":
        print("Output: dist/YouTubeAdSkipper.app")
        print()
        print("To run:")
        print("  1. Right-click the app → Open (first time only)")
        print("  2. Grant accessibility permissions when prompted")
    elif current_os == "Windows":
        print("Output: dist/YouTubeAdSkipper.exe")
        print()
        print("To run:")
        print("  Double-click YouTubeAdSkipper.exe")
    else:
        print(f"Output: dist/{APP_NAME}")
    
    print()
    print("=" * 50)
    print("CROSS-PLATFORM BUILDS")
    print("=" * 50)
    print()
    print("To build for the OTHER platform, you have two options:")
    print()
    print("1. Run this script on that OS directly")
    print()
    print("2. Use GitHub Actions (free CI/CD):")
    print("   - Push this project to GitHub")
    print("   - Add the workflow file (see github_workflow.yml)")
    print("   - GitHub will build for both Mac and Windows automatically")


if __name__ == "__main__":
    build()