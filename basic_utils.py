#!./env/bin/python

##########################################
############# BASIC UTILITY ##############
##########################################

# this script will helpful to upload/download files from Drive's `Backups` folder only.

import GBackupPy as bkup
from typing import Optional

def upload(instance: bkup.authorization, is_file: bool, path: str) -> None:
    try:
        # get folder ID
        folder_id = bkup.get_fol_id(instance)

        if is_file:
            bkup.upload_file(instance, path, folder_id=folder_id)
        else:
            bkup.upload_folder(instance, path, folder_id)
    except ValueError as ve:
        print(f"{ve} Just go to 'drive.google.com' and create a folder named 'Backups'.")


def download(instance: bkup.authorization, path: Optional[str]=".") -> None:
    bkup.save_to_local(instance, path)


if __name__ == "__main__":
    
    # google authorization
    drive = bkup.authorization()

    # uploading...
    # upload(instance=drive, is_file=False, path="/path/to/folder")
    # upload(instance=drive, is_file=True, path="/path/to/file")

    # downloading...
    # download(instance=drive)  # saves in current directory
    # download(instance=drive, path="/path/to/save")
    
