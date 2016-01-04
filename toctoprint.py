#!/usr/bin/env python
import os, sys
import argparse
from subprocess import call
import daemon
import configparser

def notify(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "default" , "-sender" , "com.Simplify3D.S3D-Software"])

def error(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "Glass.aiff" , "-sender" , "com.Simplify3D.S3D-Software", "-contentImage",  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertStopIcon.icns"])

def trash(filename):
	call(["/usr/local/bin/trash", filename]) 

def upload(gcode):
	try:
		name = os.path.basename(gcode)
		notify("Uploading '%s' GCODE to Octoprint..."%name)
		ret = call(["/usr/bin/curl", "--connect-timeout", "15" ,"-H", "Content-Type: multipart/form-data", "-H", "X-Api-Key: {0}".format(OCTOPRINT_KEY), "-F", "select=true", "-F", "print=false", "-F", "file=@{0}".format(gcode), "{0}/api/files/local".format(SERVER)])
		if ret == 0:
			notify("Succesfully uploaded '%s' GCODE to Octoprint..."%name)
		else:
			error("Failed to upload '%s'..."%gcode)
	except:
		failed("Failed to upload '%s'..."%gcode)
	finally:
		TRASH and trash(gcode)

def run(gcode):
		if not os.path.exists(gcode):
			error("Failed to upload '%s'.\n\n[file does not exist]"%gcode)
			exit(2)
		if gcode.startswith(DEFAULT_LOCATION):
			upload(gcode)
		else:
			EDITOR and call([EDITOR, gcode])
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Upload GCODE to Octoprint.', add_help=False)
	parser.add_argument('-g', '--gcode', required=True)
	
	try:
		args = parser.parse_args()
	except:
		error("Not enough arguments.")
		exit(1)
	
	try:
		config = configparser.ConfigParser()
		config_file = os.path.join(os.path.expanduser("~"), ".toctoprint.ini")
		if not os.path.exists(config_file):
			error("Config file '%s' does not exist."%config_file)
			exit(2)
		
		config.read(config_file)
		
		SERVER = config['default']['SERVER']
		OCTOPRINT_KEY = config['default']['OCTOPRINT_KEY']
		DEFAULT_LOCATION = os.path.expanduser(config['default']['DEFAULT_LOCATION'])
		EDITOR = config['default']['EDITOR']
		TRASH = config['default']['TRASH']
		
	except Exception as e:
		error("Error reading configuration.\n%s"%e)
		exit(3)
	
	with daemon.DaemonContext(initgroups=False):	
		run(args.gcode)
