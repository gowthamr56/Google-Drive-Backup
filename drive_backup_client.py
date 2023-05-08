#!./env/bin/python

import drive_backup as bkup
from sys import argv

# google authorization
drive = bkup.authorization()

# path = argv[1]

# downloading
bkup.save_to_local(drive)
