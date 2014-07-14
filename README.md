RepoSync
========
RepoSync is a script that works with APT-MIRROR to create a delta file of updates. 

The primary usage is to update offline ubuntu repositories. The best way to use this software
is to create a daily or weekly cron job to create the delta directories automatically.

TODO:
- Integrate with apt-mirror mirror.list file.
- Add Option to compress delta directory to a single file
- Create single python script for both snap and delta functions.
- Create script to place files in the offline repo


USAGE:
run repoSnap.py on an existing directory, update that directory with apt-mirror, run repoDelta.py after apt-mirror is done. 
The directory created will contain only the changed files since the snapshot. Files are compared by filename, date, and size. if any field is changed the file is place in the delta.

$ sudo repoSnap.py -r -o delta.csv /repo/mirror
$ sudo apt-mirror 
$ sudo repoDelta -s delta.csv -b /repo/mirror -d delta

