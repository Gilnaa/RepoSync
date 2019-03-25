#!/usr/bin/python3
import argparse
import os
import os.path
import time
import csv
import sys
import sqlite3


def walk_directory(dir_path):
    for (path, dirs, files) in os.walk(dir_path, topdown=True):
        for ifile in files:
            pathFile = os.path.join(path, ifile)
            fileInfo = os.stat(pathFile)
            fileTimeStamp = time.asctime(time.localtime(fileInfo.st_mtime))

            yield [os.path.relpath(pathFile, dir_path),
                    fileTimeStamp, 
                    fileInfo.st_size]


def main():
    #Set all command line arguments
    parser = argparse.ArgumentParser(description="This script will scan a specified directory and create a file that will serve as a snapshot of the directory for future use in copying only newer files to a delta directory")
    parser.add_argument("--override", action='store_true', help="Override output if exists.")
    parser.add_argument("repo_path", help="The Path of the directory you want to create a snapshot of")
    parser.add_argument("snapshot_path", help="Output file of the snapshot.")
    args = parser.parse_args()

    if not os.path.exists(args.repo_path):
        print("Path doesn't exist on this system")
        sys.exit()

    if not os.path.isdir(args.repo_path):
        print(args.path, 'is not a directory.')
        sys.exit()

    #Check to see if the path and file specified in argument -o exist.
    if os.path.exists(args.snapshot_path) and not args.override:
        print('Cowerdly refusing to override existing output file')
        sys.exit()

    lines = walk_directory(args.repo_path)

    con = sqlite3.Connection(args.snapshot_path)
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS "files"')
    cur.execute('CREATE TABLE "files" ("filename" text, "mdate" text, "size" numeric);')
    cur.executemany('INSERT INTO files (filename, mdate, size) VALUES (?, ?, ?)', lines)
    cur.execute('CREATE INDEX IF NOT EXISTS idx_filename on files(filename);')
    cur.close()
    con.commit()
    
if __name__ == '__main__':
    main()
