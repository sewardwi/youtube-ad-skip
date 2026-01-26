# Automatically skip Youtube ads

### native

run the native: <br>
```python youtube-skipper-native.py```

usable in regular chrome browser. <br>
<br>
testing so far:
* successfully skipped ad on regular chrome browser when watching video in non-fullscreen mode on Macbook Pro
* only worked on laptop screen not on connected monitor
* should in theory work for any size computer screen

<br>
build executable using: <br>

```python build_executable.py```

<br><br><br>

# Before doing anything

make sure to run from venv or using interpreter after doing ```pip install -r requirements.txt```


<br><br><br>

# Troubleshooting

* if download executable not working on mac run ```xattr -cr YouTubeAdSkipper.app```
* also on mac: The "until you close the app" issue happens with unsigned apps. macOS doesn't persist permissions properly for apps that aren't code-signed Fix: Manually add the app to permissions (persists): Open System Settings → Privacy & Security → Screen Recording Click the + button
Navigate to the .app and add it
Open System Settings → Privacy & Security → Accessibility Click the + button
Add the same .app
