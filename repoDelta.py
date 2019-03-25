#!/usr/bin/python3
import argparse
import os
import os.path
import time
import shutil
import sqlite3
import sys


def calculate_delta_listing(cursor, repo_path):
    for (path, dirs, files) in os.walk(repo_path, topdown=True):
        for f in files:
            abs_path = os.path.join(path, f)
            rel_path = os.path.relpath(abs_path, repo_path)

            file_info = os.stat(abs_path)
            timestamp = time.asctime(time.localtime(file_info.st_mtime))
            result = cursor.execute('select * from files where filename=?', (rel_path, ))

            # Copy the file if it new relative to the snapshot.
            row = result.fetchone()
            if not row:
                yield rel_path
            else:
                snapshot_timestamp, snapshot_size = str(row[1]), row[2]
                if snapshot_timestamp != timestamp or snapshot_size != file_info.st_size:
                    yield rel_path
        
    
def create_delta_directory(delta_path, repo_path, delta):
    absdelta_path = os.path.abspath(delta_path)
    absrepo_path =  os.path.abspath(repo_path)

    if not os.path.exists(absdelta_path):
        os.makedirs(absdelta_path)

    for i, f in enumerate(delta):
        print('#{}/{}'.format(i, len(delta)))
        src = os.path.join(absrepo_path, f)
        dst = os.path.join(absdelta_path, f)

        basedir = os.path.dirname(dst)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
            
        shutil.copy(os.path.join(absrepo_path, f), 
                    os.path.join(absdelta_path, f))
        

def main():
    #set all command line arguments
    parser = argparse.ArgumentParser(description="This script will take a snapshot file as input and produce a delta directory of all changed files, based on name, Size, and date modified.")
    parser.add_argument("repo_path", help="The Path of the directory you want to create a snapshot of")
    parser.add_argument("snapshot_path", help="Output file of the snapshot.")
    parser.add_argument("delta_path", help="Directory to place the difference files. (Must have write permissions)")
    args = parser.parse_args()

    #initialize SQL Database 
    con = sqlite3.Connection(args.snapshot_path)
    cur = con.cursor()

    if not os.path.exists(args.repo_path):
        print('Repository path does not exist')
        sys.exit()
    elif not os.path.exists(args.snapshot_path):
        print('Snapshot file does not exist')
        sys.exit()

    con = sqlite3.Connection(args.snapshot_path)
    cur = con.cursor()
    delta = list(calculate_delta_listing(cur, args.repo_path))
    create_delta_directory(args.delta_path, args.repo_path, delta)

        
if __name__ == '__main__':
    main()
