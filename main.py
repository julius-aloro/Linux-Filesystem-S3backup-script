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
    if creation_date != today and os.path.isdir(directory_path) and 'appdir' in directory or 'logs' in directory or 'etc' in directory:
        shutil.rmtree(directory_path)
    else:
        if os.path.isfile(directory_path):
            os.remove(directory_path)
        elif os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
 

# Copying raw files to s3 backup directory
shutil.copytree(etc_dir, os.path.join(raw_backup, f'etc-{date_and_time}'), dirs_exist_ok=True)
shutil.copytree(app_dir, os.path.join(raw_backup, f'appdir-{date_and_time}'), dirs_exist_ok=True)
shutil.copytree(logs, os.path.join(raw_backup, f'logs-{date_and_time}'), dirs_exist_ok=True)


# Storing the directories to archive in a variable
raw_backup_dirs = [item for item in raw_backup.glob("**/*")]

# archiving the daily backup
with zipfile.ZipFile(daily_backup / f'daily-backup-{today}.zip', "w", compression=zipfile.ZIP_DEFLATED) as zipf:
    for item in raw_backup_dirs:
        zipf.write(item, arcname=item.relative_to(raw_backup))


# archiving the weekly backup
weekly_date = date.today().strftime('%d')
for day in range(0, 32, 7):
    if str(day) == weekly_date:
        with zipfile.ZipFile(weekly_backup / f'weekly-backup-{today}.zip', "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for item in raw_backup_dirs:
                zipf.write(item, arcname=item.relative_to(raw_backup))


# archiving the monthly backup
monthly_date = date.today().strftime('%d')
for day in range(0, 32, 30):
    if str(day) == monthly_date:
        with zipfile.ZipFile(monthly_backup / f'monthly-backup-{today}.zip', "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for item in raw_backup_dirs:
                zipf.write(item, arcname=item.relative_to(raw_backup))


# Truncating the archived directories (daily, weekly, monthly)
daily_backup_list = list(os.listdir(daily_backup))
weekly_backup_list = list(os.listdir(weekly_backup))
monthly_backup_list = list(os.listdir(monthly_backup))

# Retain only 7 days of daily backups
for daily_zip_files in daily_backup_list:               # Remove unrelated files (specially not zip files)
    if 'backup' not in daily_zip_files:
        if os.path.isdir(daily_zip_files):
            shutil.rmtree(daily_zip_files)
        elif os.path.isfile(daily_zip_files):
            os.remove(daily_zip_files)

if len(daily_backup_list) > 7:
    daily_backup_list_copy = daily_backup_list.copy()
    daily_backup_list_copy = sorted(daily_backup_list_copy)
    for daily_zip_files in daily_backup_list_copy[:-7]:
        os.remove(daily_zip_files)




# Retain only 5 zipfiles of weekly backups
if len(weekly_backup_list) > 5:
    weekly_backup_list_copy = weekly_backup_list.copy()
    weekly_backup_list_copy = sorted(weekly_backup_list_copy)
    for weekly_zip_files in weekly_backup_list_copy[:-5]:
        os.remove(weekly_zip_files)

# Retain only 12 zipfiles of monthly backups
if len(monthly_backup_list) > 12:
    monthly_backup_list_copy = monthly_backup_list.copy()
    monthly_backup_list_copy = sorted(monthly_backup_list_copy)
    for monthly_zip_files in monthly_backup_list_copy[:-12]:
        os.remove(monthly_zip_files)


#### Uploading of local backups to s3 ####

# Initialize connection to s3 console
aws_console = boto3.session.Session(profile_name= 'iamadmin', region_name= 'ap-southeast-1')
s3_client = boto3.client('s3')

# Upload zip file from daily backups (only the latest)
daily_backup_to_s3 = os.listdir(daily_backup)
print(daily_backup_to_s3)
# s3_client.upload_file(daily_backup / zip_files, 'linuxfs-automated-backup-bucket', f'daily/{daily_backup_to_s3[-1]}')
