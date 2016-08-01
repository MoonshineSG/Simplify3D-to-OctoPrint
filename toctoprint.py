#!/usr/bin/env python
import os, sys
import argparse
from subprocess import call, check_output
import daemon
import configparser
import re
import json

def notify(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "default" , "-sender" , "com.Simplify3D.S3D-Software"])

def error(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "Glass.aiff" , "-sender" , "com.Simplify3D.S3D-Software", "-contentImage",  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertStopIcon.icns"])

def success(message):
	call(["/usr/local/bin/terminal-notifier",  "-message" , str(message), "-title" , "Simplify3D" , "-sound" , "Glass.aiff" , "-sender" , "com.Simplify3D.S3D-Software", "-contentImage",  "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarFavoritesIcon.icns"])

def trash(filename):
	call(["/usr/local/bin/trash", filename]) 

material_pattern = re.compile(ur'printMaterial,(.*)')
speed_pattern = re.compile(ur'defaultSpeed,(.*)')
primary_extruder_pattern = re.compile(ur'primaryExtruder,(.*)')
extruder_diameter_pattern = re.compile(ur'extruderDiameter,(.*)')
hotend_pattern = re.compile(ur'printExtruders,(.*)')
layer_height_pattern = re.compile(ur'layerHeight,(.*)')
extrusion_width_pattern = re.compile(ur'extruderWidth,(.*)')

#first line in the custom start gcode set in Simplify3D
start_code_pattern = re.compile(ur'^; ------------ START GCODE ----------')

def get_info(gcode):
	material = ""
	layer_height = ""
	extruders_width = ""
	hotend = ""
	extruders = ""
	primary = 0
	speed = ""

	for i, line in enumerate(open(gcode)):
		matched = material_pattern.findall(line)
		if matched:
			material = matched[0]

		matched = layer_height_pattern.findall(line)
		if matched:
			layer_height =  matched[0]

		matched = extrusion_width_pattern.findall(line)
		if matched:
			extruders_width =  matched[0]

		matched = hotend_pattern.findall(line)
		if matched:
			hotend =  re.sub(r'[\d\.]*', '', matched[0]) 

		matched = extruder_diameter_pattern.findall(line)
		if matched:
			extruders =  matched[0]

		matched = primary_extruder_pattern.findall(line)
		if matched:
			primary =  matched[0]

		matched = speed_pattern.findall(line)
		if matched:
			speed = matched[0]

		matched = start_code_pattern.findall(line)
		if matched:			
			break #end of info section - don't parse the rest of the file
	
	return dict(hotend=hotend, nozzle = extruders.split(",")[int(primary)], layer = layer_height, width = extruders_width.split(",")[int(primary)], speed = speed, material = material)
	
def get_renamed(gcode):
	MAX_LENGTH = 60
	d = os.path.dirname(gcode)
	n, e = os.path.splitext( os.path.basename(gcode) )
	if len(n) > MAX_LENGTH:
		renamed = os.path.join(d, n[:MAX_LENGTH]+"  "+e)
		os.rename(gcode, renamed)
		return renamed
	else:
		return gcode
		
def upload(gcode):
	try:		
		name = os.path.basename(gcode).replace(" ", "_")
		notify("Uploading '%s' ..."%name)
		
		USER_DATA = "userdata="+json.dumps(get_info(gcode))

		try:
			call(["/usr/bin/curl", "--connect-timeout", "15" ,"-H", "Content-Type: multipart/form-data", "-H", "X-Api-Key: {0}".format(OCTOPRINT_KEY), "-X", "DELETE",  "{0}/api/files/local/{1}".format(SERVER, name)])
		except:
			pass
		ret = call(["/usr/bin/curl", "--connect-timeout", "15" ,"-H", "Content-Type: multipart/form-data", "-H", "X-Api-Key: {0}".format(OCTOPRINT_KEY), "-F", SELECT, "-F", PRINT, "-F", USER_DATA, "-F", "file=@{0}".format(gcode), "{0}/api/files/local".format(SERVER)])
		
		if ret == 0:
			success("""Upload succesfull...
%s
			"""%gcode)
		else:
			error("""Failed to upload [UE]...
%s
			"""%gcode)
	except Exception as e:
		error("""Failed to upload [EX]...
%s
		"""%gcode)
	finally:
		TRASH and trash(gcode)
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Upload GCODE to Octoprint.', add_help=False)
	parser.add_argument('--gcode', required=True)
	parser.add_argument('--key')
	parser.add_argument('--server')
	parser.add_argument('--location')
	parser.add_argument('--editor')
	parser.add_argument('switches', nargs='*', choices = ["select", "print", "trash", "default"], default="default")

	try:
		args = parser.parse_args()
	except Exception as e:
		print(e)
		error("Called with invalid parameters.")
		exit(1)

	#first thing first...
	gcode = os.path.expanduser(args.gcode)
	if not os.path.exists(gcode):
		error("""Failed to upload [fnf]...
%s"""%gcode)
		exit(2)

	#default settings
	SERVER = "http://octoprint.local"
	OCTOPRINT_KEY = None
	DEFAULT_LOCATION = "~/Desktop"
	EDITOR = "/usr/local/bin/mate"
	TRASH = False
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

	#can't go on without these 2
	if OCTOPRINT_KEY == None or SERVER == None : 
		error("Missing server information.")
		exit(4)
	
	DEFAULT_LOCATION = os.path.expanduser(DEFAULT_LOCATION)

	if gcode.startswith(DEFAULT_LOCATION) and not os.path.basename(gcode).startswith("_"):
		if os.path.basename(gcode).startswith(" "):
			call([EDITOR, "-w",  gcode])
		#start the upload in a background process
		with daemon.DaemonContext(initgroups=False):
			upload( get_renamed(gcode) )
	else:
		EDITOR and call([EDITOR, gcode])
