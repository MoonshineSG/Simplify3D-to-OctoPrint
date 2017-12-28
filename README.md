Developed for OSX. With (minor?) changes, could be usefull on other platforms as well.

## Install:

```
brew install terminal-notifier
brew install trash
sudo easy_install python-daemon
sudo easy_install configparser
```

## Usage

`/path/to/toctoprint.py select print trash --location ~/Desktop --editor /usr/local/bin/mate --server http://octoprint.local --key 00000000000000000  --gcode ~/Desktop/gcode.gcode`

Except for the parameter --gcode all options can be set in `ini` file

The commands "select", "print", "rename" and "trash" can only be specified via the command line. If you specify "print" you don't need to specify "select"

### Settings
--server & --key - OctoPrint setting

--editor - the editor used for opening files not placed in the default folder. change this to None if you don't want to open when saving to a different path or if the file name starts with `_`

trash - remove local gcode file after uploading to Octoprint

rename - will add the name of the material (from the selected AUto Configure material name) at the begining of the file name (abc.gcode -> PLA_abc.gcode)

select - select file after upload

print - start print after upload

insecure - don't verify SSL certificate (for self signed SSL) - use carefully!!

You can create `.toctoprint.ini` in your home folder with any (or all) following settings or pass as command line parameters

```
[default]
SERVER = http://octoprint.local
OCTOPRINT_KEY = 00000000000000000000000
EDITOR = /usr/local/bin/mate
```

#### ini file settings vs command line

```
--server    -   SERVER
--key       -   OCTOPRINT_KEY
--editor    -   EDITOR
```

## Simplify3D

Add this to post procesing script in Simplify3D:

`/path/to/toctoprint.py select rename trash --location ~/Desktop --editor /usr/local/bin/mate --key 00000000000000000 --server http://octoprint.local --gcode "[output_filepath]"`

- settings passed as parameters overwrite the ones in the ini file.
- [output_filepath] will be replaced by Simplify3D with the full path of the saved GCODE file.

UPDATE: put [output_filepath] between double quotes "[output_filepath]" to allow you use spaces in the file name

UPDATE (28/04/2016): added rename option

UPDATE (09/05/2016): added estimate option (see https://github.com/MoonshineSG/marlin-estimate as well)

UPDATE (31/05/2016): changed estimation format to meta data

UPDATE (01/08/2016): removed estimate option (OctoPrint estimates improved to acceptable levels)

UPDATE (01/08/2016): added "insecure" mode for self signed SSL

UPDATE (13/10/2016): removed LOCATION and moved all processing to background


![screenshot](screenshot_1.png)


### Donate

Accepting [beer tips](https://paypal.me/ovidiuhossu)...

