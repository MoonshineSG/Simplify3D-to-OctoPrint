#!/usr/bin/env python
import os, sys
import argparse
from subprocess import call
import daemon
import configparser
import re

def notify(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "default" , "-sender" , "com.Simplify3D.S3D-Software"])

def error(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "Glass.aiff" , "-sender" , "com.Simplify3D.S3D-Software", "-contentImage",  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertStopIcon.icns"])

def success(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "Glass.aiff" , "-sender" , "com.Simplify3D.S3D-Software", "-contentImage",  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarFavoritesIcon.icns"])

def trash(filename):
	call(["/usr/local/bin/trash", filename]) 

pattern = re.compile(ur'printMaterial,(.*)')

def find_material(gcode):
	for i, line in enumerate(open(gcode)):
		matched = pattern.findall(line)
		if matched:
			return matched[0]

def get_renamed(gcode):
	material = find_material(gcode)
	d = os.path.dirname(gcode)
	f = os.path.basename(gcode)
	renamed = os.path.join(d, "%s_%s"%(material,f) )
	os.rename(gcode, renamed)
	return renamed
	
def upload(gcode):
	try:
		name = os.path.basename(gcode)
		notify("Uploading '%s' GCODE to Octoprint..."%name)
		ret = call(["/usr/bin/curl", "--connect-timeout", "15" ,"-H", "Content-Type: multipart/form-data", "-H", "X-Api-Key: {0}".format(OCTOPRINT_KEY), "-F", SELECT, "-F", PRINT, "-F", "file=@{0}".format(gcode), "{0}/api/files/local".format(SERVER)])
		if ret == 0:
			success("Succesfully uploaded '%s' GCODE to Octoprint..."%name)
		else:
			error("Failed to upload [ue] '%s'... "%gcode)
	except Exception as e:
		print (e)
		failed("Failed to upload [ex] '%s'... "%gcode)
	finally:
		TRASH and trash(gcode)
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Upload GCODE to Octoprint.', add_help=False)
	parser.add_argument('--gcode', required=True)
	parser.add_argument('--key')
	parser.add_argument('--server')
	parser.add_argument('--location')
	parser.add_argument('--editor')
	parser.add_argument('switches', nargs='*', choices = ["select", "print", "rename", "trash", "default"], default="default")

	try:
		args = parser.parse_args()
	except Exception as e:
		print(e)
		error("Called with invalid parameters.")
		exit(1)

	#first thing first...
	gcode = os.path.expanduser(args.gcode)
	if not os.path.exists(gcode):
		error("Failed to upload [fnf] '%s'..."%gcode)
		exit(2)

	#default settings
	SERVER = "http://octoprint.local"
	OCTOPRINT_KEY = None
	DEFAULT_LOCATION = "~/Desktop"
	EDITOR = "/usr/local/bin/mate"
	TRASH = False
	RENAME = False
	SELECT = "select=false" 
	PRINT = "print=false"
	
	
	#read settigns from ini file, if available
	try:
		config_file = os.path.join(os.path.expanduser("~"), ".toctoprint.ini")
		if os.path.exists(config_file):
			config = configparser.ConfigParser()
			config.read(config_file)
			
			try:
				SERVER = config['default']['SERVER']
			except:
				pass
			try:	
				OCTOPRINT_KEY = config['default']['OCTOPRINT_KEY']
			except:
				pass
			try:
				DEFAULT_LOCATION = config['default']['DEFAULT_LOCATION']
			except:
				pass
			try:
				EDITOR = config['default']['EDITOR']
			except:
				pass
	except Exception as e:
		error("Error reading configuration.\n%s"%e)
		exit(3)

	#update settigns based on received parameters
	if args.server: 
		SERVER = args.server
	if args.key:
		OCTOPRINT_KEY = args.key
	if args.location:
		DEFAULT_LOCATION = args.location
	if args.editor:
		EDITOR = args.editor

	if args.switches != "default":
		if "print" in args.switches:
			SELECT = "select=true"
			PRINT = "print=true"

		if "select" in args.switches:
			SELECT = "select=true"

		if "trash" in args.switches:
			TRASH = True

		if "rename" in args.switches:
			RENAME = True

	#can't go on without these 2
	if OCTOPRINT_KEY == None or SERVER == None : 
		error("Missing server information.")
		exit(4)
	
	DEFAULT_LOCATION = os.path.expanduser(DEFAULT_LOCATION)

	if gcode.startswith(DEFAULT_LOCATION) and not os.path.basename(gcode).startswith("_"):
		#start the upload in a background process
		with daemon.DaemonContext(initgroups=False):
			if RENAME:
				upload(get_renamed(gcode))
			else:
				upload(gcode)
	else:
		EDITOR and call([EDITOR, gcode])
