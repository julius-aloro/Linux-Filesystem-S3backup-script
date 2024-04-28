import os
import shutil
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
# try:
shutil.copytree(etc_dir, os.path.join(s3_backup_dir, f'etc-{date_and_time}'))
shutil.copytree(app_dir, os.path.join(s3_backup_dir, f'appdir-{date_and_time}'))
shutil.copytree(logs, os.path.join(s3_backup_dir, f'logs-{date_and_time}'))
# # except:
#     print('Error is found, please manually check files..')
# else:
#     print('Backup is completed successfully!')

