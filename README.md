Developed for OSX. With (minor?) changes, could be usefull on other platforms as well.

##Install:

```
brew install terminal-notifier
brew install trash
sudo easy_install python-daemon
sudo easy_install configparser
```

## Usage

`/path/to/toctoprint.py select print trash --location ~/Desktop --editor /usr/local/bin/mate --server http://octoprint.local --key 00000000000000000  --gcode ~/Desktop/gcode.gcode`

Except for the parameter --gcode all options can be set in `ini` file

The commands "select", "print" and "trash" can only be specified via the command line. If you specify "print" you don't need to specify "select"

### Settings
--server & --key - OctoPrint setting

--location - only gcode files created to this folder will be uploaded

--editor - the editor used for opening files not placed in the default folder. change this to None if you don't want to open when saving to a different path

trash - remove local gcode file after uploading to Octoprint

select - select file after upload

print - start print after upload

You can create `.toctoprint.ini` in your home folder with any (or all) following settings or pass as command line parameters

```
[default]
SERVER = http://octoprint.local
OCTOPRINT_KEY = 00000000000000000000000
DEFAULT_LOCATION = ~/Desktop
EDITOR = /usr/local/bin/mate
```

####ini file settings vs command line

```
--server    -   SERVER
--key       -   OCTOPRINT_KEY
--location  -   DEFAULT_LOCATION
--editor    -   EDITOR
```

## Simplify3D

Add this to post procesing script in Simplify3D:

`/path/to/toctoprint.py select trash --location ~/Desktop --editor /usr/local/bin/mate --key 00000000000000000 --server http://octoprint.local --gcode [output_filepath]`

- settings passed as parameters overwrite the ones in the ini file.
- [output_filepath] will be replaced by Simplify3D with the full path of the saved GCODE file.


![screenshot](screenshot_1.png)

