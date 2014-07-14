#!/usr/bin/python
#####IMPORTS#######
import argparse
import os
import os.path
import time
import csv
import shutil
import sqlite3
import sys

#set all command line arguments
parser = argparse.ArgumentParser(description="This script will take a snapshot file as input and produce a delta directory of all changed files, based on name, Size, and date modified.")
parser.add_argument("-s", "--snapshotFile", required=True, help="File to be used in comparing the base directory")
parser.add_argument("-b", "--baseDirectory", required=True, help="Directory to compare aginst the snapshot file.")
parser.add_argument("-d", "--deltaDirectory", required=True, help="Directory to place the difference files. (Must have write permissions)")

args = parser.parse_args()

#initialize global variables 
changedDict = dict()


#initialize SQL Database 
con = sqlite3.Connection(":memory:")
cur = con.cursor()
cur.execute('CREATE TABLE "files" ("filename" text, "mdate" text, "size" numeric);')

def checkPathExist(path):
	if os.path.exists(path) and os.path.isdir(path):
		return True
	else:
		return False

def checkFileExists(file):
	if os.path.exists(file) and os.path.isfile(file):
		return True
	else:
		return False
		
def status(message, percent=None):
	sys.stdout.flush()
	if not percent:
		percent=0
	sys.stdout.write('\r[{0}] {1}% {2} {3}'.format('#'*(percent/10), percent, message, ' '*len(message)))
		
	
def createCSVtoSQL(snapShotFile):
	#open the file, collect a sample and set inFile back to BOF
	inFile = open(snapShotFile, "r")
	status("opening CSV file...",)
	sample = inFile.readline()
	inFile.seek(0)
	hasHeader = csv.Sniffer().has_header(sample)
	inFileDialect = csv.Sniffer().sniff(sample)
	csvDictReader = csv.DictReader(inFile, dialect=inFileDialect)
	#convert csvDictReader to a list and input into the database.
	status("Creating Database")
	to_db = [(row['fileName'], row['DateModified'], row['Size']) for row in csvDictReader] 
	cur.executemany('INSERT INTO files (filename, mdate, size) VALUES (?,?,?)', to_db)
	#you must create an index of our most used field to make the application run at a decent speed.
	status("Creating Database index on filename field")
	cur.execute('CREATE INDEX IF NOT EXISTS idx_filename on files(filename);')
	#close everything out. 
	cur.close()
	con.commit()
	status("Database created")
	inFile.close()
	 
def compareBaseDirectory(baseDirectory):
	#Define Counter variables for status progress
	totalFileCount = 0
	totalDatabaseCount = 0
	currentFileCount = 0
	currentDatabaseCount = 0
	lstChangedFiles = []
	
	status("Getting the total amount of files in base directory")
	for (path, dirs, files) in os.walk(baseDirectory, topdown=True):
		for fileCount in files:
			totalFileCount += 1
	
	status("Getting the total amount of files in snapshot")	
	cur = con.cursor()
	result = cur.execute('select * from files')
	
	for row in result:
		totalDatabaseCount += 1
		status(str(totalDatabaseCount))
	
	status("Processing Files...")
	for (path, dirs, files) in os.walk(baseDirectory, topdown=True):
		for iFile in files:
			pathFile = path + "/" + iFile
			fileInfo = os.stat(pathFile)
			fileTimeStamp = time.asctime(time.localtime(fileInfo.st_mtime))
			fileSize = fileInfo.st_size
			cur = con.cursor()
			result = cur.execute('select * from files where filename=?', (pathFile,))
			row = result.fetchone()
			if not row:
				lstChangedFiles.append(pathFile)
			else:
				dFileName = str(row[0])
				dTimeStamp = str(row[1])
				dSize = row[2]
				#print dFileName + " : " + pathFile
				if dTimeStamp != fileTimeStamp or dSize != fileSize:
					lstChangedFiles.append(dFileName)
			currentFileCount += 1
			status("processing file " + str(currentFileCount) + " out of " + str(totalFileCount), int((1.0*currentFileCount/totalFileCount)*100))
	
	return lstChangedFiles

	
	
def copyChangedFiles(deltaDirectory, baseDirectory, lstChangedFiles):
	absDeltaDirectory = os.path.abspath(deltaDirectory)
	absBaseDirectory =  os.path.abspath(baseDirectory)
	currentCopyCount = 0
	status("Starting copy of files to delta Directory", currentCopyCount)
	for cFile in lstChangedFiles:
		baseDirOnly = os.path.dirname(cFile.replace(absBaseDirectory, absDeltaDirectory))
		if not os.path.exists(baseDirOnly):
			status("directory deosen't exist. Creating...." + str(currentCopyCount) + " of " + str(len(lstChangedFiles)), int((1.0*currentCopyCount/len(lstChangedFiles))*100))
			os.makedirs(baseDirOnly)
		currentCopyCount += 1
		status("copying " + str(currentCopyCount) + " of " + str(len(lstChangedFiles)), int((1.0*currentCopyCount/len(lstChangedFiles))*100))
		shutil.copy(cFile, cFile.replace(absBaseDirectory, absDeltaDirectory))
		
	

if not checkFileExists(args.snapshotFile):
	print "Snapshot file does not exist."
if not checkPathExist(args.baseDirectory):
	print "Base Directory does not exist"
if not checkPathExist(args.deltaDirectory):
	print "would you like to create it?"
	action = raw_input("(y)yes (n)no: ")
	if action == "y":
		os.makedirs(args.deltaDirectory)
	if action == "n":
		exit
		
createCSVtoSQL(args.snapshotFile)
lstChangedFiles = compareBaseDirectory(args.baseDirectory)
copyChangedFiles(args.deltaDirectory, args.baseDirectory, lstChangedFiles)

		
	
