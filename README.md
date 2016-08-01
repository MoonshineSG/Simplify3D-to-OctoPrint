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

The commands "select", "print", "rename" and "trash" can only be specified via the command line. If you specify "print" you don't need to specify "select"

### Settings
--server & --key - OctoPrint setting

--location - only gcode files created to this folder will be uploaded

--editor - the editor used for opening files not placed in the default folder. change this to None if you don't want to open when saving to a different path or if the file name starts with `_`

trash - remove local gcode file after uploading to Octoprint

rename - will add the name of the material (from the selected AUto Configure material name) at the begining of the file name (abc.gcode -> PLA_abc.gcode)

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

`/path/to/toctoprint.py select rename trash --location ~/Desktop --editor /usr/local/bin/mate --key 00000000000000000 --server http://octoprint.local --gcode "[output_filepath]"`

- settings passed as parameters overwrite the ones in the ini file.
- [output_filepath] will be replaced by Simplify3D with the full path of the saved GCODE file.

UPDATE: put [output_filepath] between double quotes "[output_filepath]" to allow you use spaces in the file name

UPDATE (28/04/2016): added rename option

UPDATE (09/05/2016): added estimate option (see https://github.com/MoonshineSG/marlin-estimate as well)

UPDATE (31/05/2016): changed estimation format to meta data

UPDATE (01/08/2016): removed estimate option (OctoPrint estimates improved to acceptable levels)


![screenshot](screenshot_1.png)


#More....


_This is part of a integrated solution to create a smooth 3D printing experience by "gluing" the individual software and hardware players_

##Simplify3D - the slicer

Models (downloaded or created by Fusion360) are loaded and sliced based on selected material/quality/extruder-nozzle combo.

The "auto-select" `material` and `extruders` have names that will eventually be displyed in the "Info" tab of the mobile octoprint

The "Starting Script" ends with `"; ------------ START GCODE ----------"`. This will be used later.

Once the code file gets generated, Simplify3D executes the postprocessing sequence 

```
{REPLACE "; layer" "M808 zchange Layer"} 
{REPLACE " Z = " " "}
/full_path_to/toctoprint.py  trash select  --gcode "[output_filepath]"
```

See https://github.com/MoonshineSG/Simplify3D-to-OctoPrint

## RaspberryPi - the brain 

runs Octoprint and has a couple of opto relays connected to the GPIO pins as well as direct control over the reset PIN 
of the 3D printer board (see  https://github.com/MoonshineSG/emergency-button).

## Octoprint - the controler 

A few plugins assist the main software:

* replacemnt UI for octoprint on mobile devices mobile https://github.com/MoonshineSG/OctoPrint-Mobile

* GPIO are controlled by https://github.com/MoonshineSG/OctoPrint-Switch

* MP3 sounds https://github.com/MoonshineSG/OctoPrint-Sound

* additional tiny helpers https://github.com/MoonshineSG/OctoPrint-Plugins

## Marlin - the firmware

customised firmware with additional commands

* M808: echo parameters as `//action:`

* M889: cooling fan for end of print sequence (works with `TEMP_STAT_LEDS`)

around line #8372
```
digitalWrite(STAT_LED_BLUE, new_led ? LOW : HIGH);
if (! new_led ) {
  enqueue_and_echo_commands_P(PSTR("M889 C0"));
  SERIAL_PROTOCOLLN("//action:cooled");
}

```

* M890: swappable extruder (see https://github.com/MarlinFirmware/Marlin/issues/3980)

_All changes available at_ https://github.com/MoonshineSG/Marlin

## Opto relays the workers
used as printer power and IR lights switches