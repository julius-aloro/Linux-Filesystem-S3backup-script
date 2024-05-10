import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, date
import time

# Date variable
date_and_time = datetime.now().strftime("%Y-%m-%d")

# Directories to be used
root = Path('/')
backup_dir = Path(root) / 'backup'
raw_backup = Path(backup_dir) / 'raw_backup'
daily_backup = Path(backup_dir) / 'daily_backup'
weekly_backup = Path(backup_dir) / 'weekly_backup'
monthly_backup = Path(backup_dir) / 'monthly_backup'

# Directories to backup
etc_dir = Path(root) / 'etc'
app_dir = Path(root) / 'appdir'
logs = Path(root) / 'var' / 'log'

# Create backup directories if non-existent
if not raw_backup.exists():
    raw_backup.mkdir(parents=True)
if not daily_backup.exists():
    daily_backup.mkdir(parents=True)
if not weekly_backup.exists():
    weekly_backup.mkdir(parents=True)
if not monthly_backup.exists():
    monthly_backup.mkdir(parents=True)


# Check for latest backups. Delete unrelated files and directories
today = date.today()
raw_backup_list = os.listdir(raw_backup)

for directory in raw_backup_list:
    directory_path = (raw_backup / directory)
    creation_time = os.path.getctime(directory_path)
    creation_date = date.fromtimestamp(creation_time)
    if creation_date == today and os.path.isdir(directory_path) and 'appdir' in directory or 'logs' in directory or 'etc' in directory:
        print(directory)
    else:
        if os.path.isfile(directory_path):
            os.remove(directory_path)
        elif os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
