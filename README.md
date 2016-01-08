For OSX only. With changes, might be usefull on other platforms as well.


Add this to post procesing script in Simplify3D

`"/path/to/toctoprint.py" --gcode "[output_filepath]"`

![screenshot](screenshot_1.png)

Install

```
brew install terminal-notifier
brew install trash
sudo easy_install python-daemon
sudo easy_install configparser
```

create `.toctoprint.ini` in your home folder

```
[default]
\#Octoprint setting
SERVER = http://X.X.X.X
OCTOPRINT_KEY = XXXXXX

\#only gcode files created to this folder will be uploaded
DEFAULT_LOCATION = ~/Desktop

\#change this to None if you don't want to open when saving to a different path
EDITOR = /usr/local/bin/mate

\#remove local gcode file after uploading to Octoprint
TRASH = True
```