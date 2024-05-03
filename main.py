import os
import shutil
import zipfile
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



# List of directories
raw_random_files = sorted((list(os.listdir(s3_backup_dir))))
dir_count = len(raw_random_files)

# Checks the directory if s3 backup folder has directories and/or files not related to backup will be deleted
os.chdir(s3_backup_dir)
for directory in raw_random_files:
    if 'appdir' not in directory and 'etc' not in directory and 'logs' not in directory and os.path.isdir(directory) == True:
        shutil.rmtree(directory)
    elif os.path.isdir(directory) == False:
        os.remove(directory)
    # elif zipfile.is_zipfile(directory) == True

# Checks if there are more than 1 copies of appdir/etc/logs, delete the oldest ones
raw_relevant_files = sorted((list(os.listdir(s3_backup_dir))))
if dir_count > 3:
    os.chdir(s3_backup_dir)
    for directory2 in raw_relevant_files[:-3]:
        shutil.rmtree(directory2)

