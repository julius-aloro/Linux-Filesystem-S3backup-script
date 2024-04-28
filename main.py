import os
import shutil
import sys
from datetime import datetime

# Date variable
date_and_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Directories to be used
backup_dir = '/backup/'
s3_backup_dir = '/backup/s3_backup/'

# Directories to backup
etc_dir = '/etc/'
app_dir = '/appdir/'
logs = '/var/log/'

#Checking of the directories -- create if non-existent
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

if not os.path.exists(s3_backup_dir):
    os.makedirs(s3_backup_dir)

# Copying raw files to s3 backup directory
shutil.copytree(etc_dir, os.path.join(s3_backup_dir, f'{date_and_time}-etc'))
shutil.copytree(app_dir, os.path.join(s3_backup_dir, f'{date_and_time}-appdir'))
shutil.copytree(logs, os.path.join(s3_backup_dir, f'{date_and_time}-logs'))

# Checker for raw directories. If more than 3, delete the oldest
raw_backup_count = list(sorted(os.listdir(s3_backup_dir)))
os.chdir(s3_backup_dir)
if len(raw_backup_count) > 3:
    for dir in raw_backup_count[0:3]:
        shutil.rmtree(dir)

