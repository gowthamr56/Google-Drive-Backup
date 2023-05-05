#!./env/bin/python

# how to run 👇
# python drive_backup.py "Folder Location"

import os
from sys import argv
import tempfile, zipfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from typing import Optional, Dict

def authorization() -> GoogleDrive:
    '''
        Authorizing the user by the `client_secrets.json` file.
        NOTE: Make sure that, after downloading the `credentials.json` file from `developers.google.com` rename it to `client_secrets.json`
    '''

    # Google authorization
    gl_auth = GoogleAuth()

    # Load previously stored credentials from a JSON file
    creds_file = 'creds.json'
    if os.path.exists(creds_file):
        gl_auth.LoadCredentialsFile(creds_file)

    # If the credentials don't exist or are invalid, authenticate the user
    if gl_auth.credentials is None or gl_auth.credentials.invalid:
        gl_auth.LocalWebserverAuth()

        # Save the credentials to a JSON file for future use
        gl_auth.SaveCredentialsFile(creds_file)

    # returning local instance for Google Drive
    return GoogleDrive(gl_auth)


def create_folder(instance: GoogleDrive, FOLDER_NAME: Optional[str]="Backups") -> None:
    '''This function create a `Backups` folder if that's not exists in the drive.'''

    FOLDER_MIMETYPE = "application/vnd.google-apps.folder"

    # creating a folder if `Backups` folder is not exists
    if not FOLDER_NAME in folder_details(instance):
        up_folder = instance.CreateFile(
            {
                "title": FOLDER_NAME,
                "mimeType": FOLDER_MIMETYPE
            }
        )
        up_folder.Upload()


def folder_details(instance: GoogleDrive) -> Dict[str, str]:
    '''Returns all the `folder names` with their `folder ID` that is in the drive.'''
    
    FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
    folders = dict()
    folder_list = instance.ListFile({"q": f"mimeType='{FOLDER_MIMETYPE}' and trashed=false"}).GetList()
    
    for folder in folder_list:
        folders.update(
            {
                folder.get("title"): folder.get("id")
            }
        )
    return folders


def upload_file(instance: GoogleDrive, filename: str, content_filename: str, folder_id: Optional[str]=None) -> None:
    f'''
    Uploads file to the google drive.
    :param folder_id: expects `Backups` folder's ID. If nothing specifed, then it will upload to the `root(My Drive)` folder
    '''

    if folder_id:
        file_metadata = {
            "title": filename,
            "parents": [
                {
                    "id": folder_id
                }
            ]
        }
    else:
        file_metadata = {"title": filename}
        
    up_file = instance.CreateFile(metadata=file_metadata)
    up_file.SetContentFile(content_filename)

    print(f"Uploading {filename}...")
    up_file.Upload()
    print("File Uploaded.\n")


if __name__ == "__main__":
    
    drive = authorization()
    path = argv[1]

    # getting id of `Backups` folder
    fol_details = folder_details(drive)
    folder_id = fol_details.get("Backups") if "Backups" in fol_details else None

    # checking `Backups` exists or not
    if folder_id is None:
        print("Backups folder is not found.\nCreating Backups folder...")
        create_folder(drive)
        print("Backups folder created.\n")
        folder_id = folder_details(drive).get("Backups")

    # creating temporary buffer to store zip file 
    # NOTE: created temporary file will be deleted after this context manager
    with tempfile.NamedTemporaryFile(suffix=".zip") as temp_zip:

        # archiving the files that is in the given path
        with zipfile.ZipFile(temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:

            # iterating over each and every file in the given path
            for cur_path, dirs, files in list(os.walk(path)):
                for file in files:
                    zip_file.write(
                        filename=os.path.join(cur_path, file),
                        arcname=os.path.relpath(os.path.join(cur_path, file), os.path.join(path, ".."))
                    )

        # Uploading a file
        upload_file(
            instance=drive, 
            filename=f"{os.path.split(path)[-1]}.zip", 
            content_filename=temp_zip.name,
            folder_id=folder_id
        )