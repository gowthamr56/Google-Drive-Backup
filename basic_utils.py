#!./env/bin/python

##########################################
############# BASIC UTILITY ##############
##########################################

# this script will helpful to upload/download files from Drive's `Backups` folder only.

import GBackupPy as bkup

def upload(instance: bkup.authorization, is_file: bool, path: str) -> None:
    try:
        # get folder ID
        folder_id = bkup.get_fol_id(instance)

        if is_file:
            # checking the file (that is going to upload) is already exist or not 
            fl_details = bkup.file_details(instance)
            
            if path in fl_details:
                bkup.trash_file(instance, file_name=path)
                bkup.upload_file(instance, path, folder_id=folder_id)
            else: 
                bkup.upload_file(instance, path, folder_id=folder_id)

        else:
            bkup.upload_folder(instance, path, folder_id)

    except ValueError as ve:
        print(f"{ve} Just go to 'drive.google.com' and create a folder named 'Backups'.")


if __name__ == "__main__":
    
    # google authorization
    drive = bkup.authorization()

    # uploading...
    # upload(instance=drive, is_file=False, path="test")
    # upload(instance=drive, is_file=True, path="test.txt")

    # listing files
    # details = bkup.file_details(instance=drive)

    # downloading...
    # bkup.save_to_local(instance=drive, filename="enter filename")  # saves in current directory
    # bkup.save_to_local(instance=drive, filename="enter filename", path="/path/to/save")
    
    # trashing...
    # bkup.trash_file(drive, "test.txt")