import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, date
import boto3
import boto3.session


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


# Create a directory function
def create_dir(directory):
    if not directory.exists():
        directory.mkdir(parents=True)

# Create backup directories if non-existent
backup_directories = [backup_dir, raw_backup, daily_backup, weekly_backup, monthly_backup]
for dir in backup_directories:
    create_dir(dir)

# Check for latest backups. Delete unrelated files and directories
today = date.today()
raw_backup_list = os.listdir(raw_backup)
for directory in raw_backup_list:
    directory_path = (raw_backup / directory)
    creation_time = os.path.getctime(directory_path)
    creation_date = date.fromtimestamp(creation_time)
    if creation_date != today and os.path.isdir(directory_path) and 'appdir' in directory or 'logs' in directory or 'etc' in directory:     # Delete raw directories in raw backups if != today.
        shutil.rmtree(directory_path)
    else:
        if os.path.isfile(directory_path):          
            os.remove(directory_path)
        elif os.path.isdir(directory_path):
            shutil.rmtree(directory_path)

# Copy function
def copy(dir_path, dir_name):
    shutil.copytree(dir_path, os.path.join(raw_backup, f'{dir_name}-{date_and_time}'), dirs_exist_ok=True)

# Copying raw files to s3 backup directory
copy(etc_dir, 'etc')
copy(app_dir, 'appdir')
copy(etc_dir, 'logs')

# Storing the directories to archive in a variable
raw_backup_dirs = [item for item in raw_backup.glob("**/*")]

# Function for archiving directories:
def archive_dir(destination_dir, dir_name):
    with zipfile.ZipFile(destination_dir / f'{dir_name}-{today}.zip', "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for files in raw_backup_dirs:
            zipf.write(files, arcname=files.relative_to(raw_backup))
            
# Daily Archive
archive_dir(daily_backup, 'daily-backup')

# Weekly Archive
weekly_date = date.today().strftime('%d')
for day in range(0, 32, 7):
    if str(day) == weekly_date:
        archive_dir(weekly_backup, 'weekly-backup')

# Monthly Archive
monthly_date = date.today().strftime('%d')
for day in range(0, 32, 30):
    if str(day) == monthly_date:
        archive_dir(monthly_backup, 'monthly-backup')

# Function for removing unnecessary files in zip directories
def delete_irrelevant_zip_files(schedule_dir):
    backup_list = os.listdir(schedule_dir)
    for zip_files in backup_list:
        zip_files_path = (schedule_dir / zip_files)               
        if 'backup' not in zip_files:
            if os.path.isdir(zip_files_path):
                shutil.rmtree(zip_files_path)
            elif os.path.isfile(zip_files_path):
                os.remove(zip_files_path)

# Remove unrelated files (specially not zip files)
zipfile_backup_dirs = [daily_backup, weekly_backup, monthly_backup]
for backups in zipfile_backup_dirs:
    delete_irrelevant_zip_files(backups)


# Truncating the archived directories (daily, weekly, monthly)
daily_backup_list = list(os.listdir(daily_backup))
weekly_backup_list = list(os.listdir(weekly_backup))
monthly_backup_list = list(os.listdir(monthly_backup))

# Retain only 7 days of daily backups
if len(daily_backup_list) > 7:
    daily_backup_list_copy = sorted(daily_backup_list.copy())
    # daily_backup_list_copy = sorted(daily_backup_list_copy)
    for daily_zip_files in daily_backup_list_copy[:-7]:
        os.remove(daily_zip_files)


# Retain only 5 zipfiles of weekly backups
if len(weekly_backup_list) > 5:
    weekly_backup_list_copy = sorted(weekly_backup_list.copy())
    # weekly_backup_list_copy = sorted(weekly_backup_list_copy)
    for weekly_zip_files in weekly_backup_list_copy[:-5]:
        os.remove(weekly_zip_files)

# Retain only 12 zipfiles of monthly backups
if len(monthly_backup_list) > 12:
    monthly_backup_list_copy = sorted(monthly_backup_list.copy())
    # monthly_backup_list_copy = sorted(monthly_backup_list_copy)
    for monthly_zip_files in monthly_backup_list_copy[:-12]:
        os.remove(monthly_zip_files)


#### Uploading of local backups to s3 ####

# # Initialize connection to s3 console
# aws_console = boto3.session.Session(profile_name= 'iamadmin', region_name= 'ap-southeast-1')
# s3_client = boto3.client('s3')

# # Upload zip file from daily backups (only the latest)
# daily_backup_to_s3 = os.listdir(daily_backup)
# print(daily_backup_to_s3)
# # s3_client.upload_file(daily_backup / zip_files, 'linuxfs-automated-backup-bucket', f'daily/{daily_backup_to_s3[-1]}')
