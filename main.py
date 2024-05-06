
import os
import shutil
import zipfile
from datetime import datetime

# Date variable
date_and_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Directories to be used
backup_dir = os.path.join('/', 'backup')
s3_backup_dir = os.path.join('/', 'backup', 's3_backup')

# Directories to backup
etc_dir = os.path.join('/', 'etc')
app_dir = os.path.join('/', 'appdir')
logs = os.path.join('/', 'var', 'log')

#Checking of the directories -- create if non-existent
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

if not os.path.exists(s3_backup_dir):
    os.makedirs(s3_backup_dir)

# Creation of daily, weekly, and monthly directories
daily_dir = os.path.join(s3_backup_dir, 'daily')
weekly_dir = os.path.join(s3_backup_dir, 'weekly')
monthly_dir = os.path.join(s3_backup_dir, 'monthly')

if not os.path.exists(daily_dir):
    os.makedirs(os.path.join(s3_backup_dir, 'daily'))
if not os.path.exists(weekly_dir):
    os.makedirs(os.path.join(s3_backup_dir, 'weekly'))
if not os.path.exists(monthly_dir):
    os.makedirs(os.path.join(s3_backup_dir, 'monthly'))


# Copying raw files to s3 backup directory
shutil.copytree(etc_dir, os.path.join(s3_backup_dir, f'{date_and_time}-etc'))
shutil.copytree(app_dir, os.path.join(s3_backup_dir, f'{date_and_time}-appdir'))
shutil.copytree(logs, os.path.join(s3_backup_dir, f'{date_and_time}-logs'))

# List of directories
mixed_files = sorted((list(os.listdir(s3_backup_dir))))

# Checks and delete unrelated files in the s3 backup directory
raw_relevant_directories = sorted(list())
zipped_relevant_files = sorted(list())
schedule_directories = sorted(list())

# Check if file is a zip file or a directory
mixed_files_copy = mixed_files.copy()
for item in mixed_files_copy:
    if zipfile.is_zipfile(item) and 'backup' in item:
        zipped_relevant_files.append(item)
    elif os.path.isdir(os.path.join(s3_backup_dir, item)) and len(item) >= 23 and 'appdir' in item or 'etc' in item or 'logs' in item:
        raw_relevant_directories.append(item)
    elif os.path.isdir(os.path.join(s3_backup_dir, item)) and item == 'daily' or item == 'weekly' or item == 'monthly':
        schedule_directories.append(item)

# Check from the relevant list of zipfile and directories. If does not belong to the list, remove.
os.chdir(s3_backup_dir)
for item in os.listdir(s3_backup_dir):
    if item in raw_relevant_directories or item in zipped_relevant_files or item in schedule_directories:
        continue
    elif os.path.isdir(os.path.join(s3_backup_dir, item)):
        shutil.rmtree(os.path.join(s3_backup_dir, item))
    elif zipfile.is_zipfile(os.path.join(s3_backup_dir, item)):
        os.remove(os.path.join(s3_backup_dir, item))
    elif os.path.isfile(os.path.join(s3_backup_dir, item)):
        os.remove(os.path.join(s3_backup_dir, item))

# Remove the duplicate backups from the previous run, leaving only 3 folders that are updated daily (appdir, logs, etc)
if len(raw_relevant_directories) > 3:
    for directory in raw_relevant_directories[:-3]:
        shutil.rmtree(directory)

# Re-initialize relevant raw backups (update the list)
daily_raw_backups = list()
for directory in os.listdir(s3_backup_dir):
    if directory == 'daily' or directory == 'weekly' or directory == 'monthly':
        continue
    else:
        daily_raw_backups.append(directory)

# Create the archive
with zipfile.ZipFile(os.path.join(s3_backup_dir, 'daily', 'test.zip'), 'a', compression=zipfile.ZIP_DEFLATED) as zipf:
    for dirpath, dirnames, filenames in os.walk(s3_backup_dir):
        for dirname in dirnames:
            zipf.write(os.path.join(s3_backup_dir, 'daily', 'test.zip'))
        for filename in filenames:
            print('File:', os.path.join(dirpath, filename))
# # Archiving function
# def create_zip(): 
#     os.chdir(s3_backup_dir)
#     for directories in os.listdir(s3_backup_dir):
#         shutil.make_archive(f'backup_{date_and_time}', 'zip', directories)

# create_zip()



# # Checks if there are more than 1 copies of appdir/etc/logs, delete the oldest ones
# dir_count = 0 
# zip_file_count = 
# for dirs in os.listdir(s3_backup_dir):
#     if os.path.isdir(dirs) == True:
#         dir_count += 1
#         raw_relevant_files.append(dirs)

















# # # Archiving of directories
# # raw_relevant_files = sorted((list(os.listdir(s3_backup_dir))))
# # create_zip(s3_backup_dir, raw_relevant_files)





# # # daily tar
# # raw_relevant_files = sorted((list(os.listdir(s3_backup_dir))))
# # tar_file_name = f'{date_and_time}-backup.tar'
# # os.chdir(s3_backup_dir)
# # create_tar_gzip(tar_file_name, raw_relevant_files)


# # raw_relevant_files = sorted((list(os.listdir(s3_backup_dir))))
# # os.chdir(s3_backup_dir)
# # # output_filename = 'daily_backup.tar.gz'
# # for directory in raw_relevant_files:
# #     shutil.make_archive(f'{date_and_time}.daily_backup', 'gzip', directory)
    

# # for root, dirs, files in os.walk(s3_backup_dir):
# #     # for name in files:
# #     #     print(name)
# #     for name in dirs:
#         # print(name)
# # gzip file function
