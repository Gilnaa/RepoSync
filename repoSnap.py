#!/usr/bin/python
#### IMPORTS ####
import argparse
import os
import os.path
import time
import csv
import sys

#Set all command line arguments
parser = argparse.ArgumentParser(description="This script will scan a specified directory and create a CSV document that will serve as a snapshot of the directory for future use in copying only newer files to a delta directory")
parser.add_argument("-r", "--recursive", action="store_true", help="Recurse through all directories within the specified path")
parser.add_argument("-o", "--outputFile", required=True, help="Output file of the snapshot")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
parser.add_argument("path", help="The Path of the directory you want to create a snapshot of")
args = parser.parse_args()

#initialize global variables 
pathExists = None
lstFieldNames = list(["fileName","Size","DateModified"])

def status(message, percent=None):
	sys.stdout.flush()
	if not percent:
		percent=0
	sys.stdout.write('\r[{0}] {1}% {2} {3}'.format('#'*(percent/10), percent, message, ' '*len(message)))

#walk the directory function to build file list. 	
def walkDirectory(fullPath):
	
	lines = []
	totalFileCount = 0
	currentFileCount = 0
	i = 0
	#get total file count
	status("Getting total file count")
	for(path, dirs, files) in os.walk(fullPath, topdown=True):
		for fileCount in files:
			totalFileCount += 1
			
	status("walking " + fullPath)
	for(path, dirs, files) in os.walk(fullPath, topdown=True):
		for ifile in files:
			pathFile = path + "/" + ifile
			fileInfo = os.stat(pathFile)
			fileTimeStamp = time.asctime(time.localtime(fileInfo.st_mtime))
			fileSize = fileInfo.st_size
			newLine = dict(zip((lstFieldNames),(pathFile, fileSize, fileTimeStamp)))
			lines.append(newLine)
			currentFileCount += 1
			status("walking file " + str(currentFileCount) + " of " + str(totalFileCount), int((1.0*currentFileCount/totalFileCount)*100))
	
	return lines
			
def createOutputFile(path, fileName):
	status("Creating outputfile at {0}".format(path + "/" + fileName))
	FILE = open(path + "/" + fileName, "w")
	FILE.close()
	return True
	
def writeOutputFile(path, fileName, lines):
	totalLineCount = len(lines)
	print totalLineCount
	currentLineCount = 0
	FILE = open(path + "/" + fileName, "w")
	csvDictWriter = csv.DictWriter(FILE, fieldnames=lstFieldNames)
	csvDictWriter.writeheader()
	for line in lines:
		csvDictWriter.writerow(line)
		currentLineCount += 1
		status("writing line " + str(currentLineCount) + " of " + str(totalLineCount), int((1.0*currentLineCount/totalLineCount)*100))

	FILE.close()
	
def doWork():
	isOutFileCreated = createOutputFile(os.getcwd(), args.outputFile)
	if isOutFileCreated:
		lines = []
		lines = walkDirectory(args.path)
		writeOutputFile(os.getcwd(), args.outputFile, lines)
	

#make sure the scan path exist 
if args.path != None and os.path.exists(args.path):
	#make sure the path is a Directory
	if os.path.isdir(args.path):
		#Check to see if the path and file specified in argument -o exist.
		print "Checking to see if the output file exists"
		outFile = args.outputFile
		if os.path.exists(os.getcwd() + "/" + outFile):
			isValid = None
			while not isValid:
				action = raw_input("(o)overwrite, (c)cancel:")
				if action == "o":
					isValid = True
					doWork()
				elif action == "c":
					exit
				else:
					isValid = False
		else:
			#create file 
			doWork()
	else:
		print args.path + " is not a directory, please specify a directory"
		exit
else:
	print "Path doesn't exist on this system"
	exit
	





