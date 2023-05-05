#!./env/bin/python

# how to run 👇
# python drive_backup.py "Folder Location"

import os
from sys import argv
import tempfile, zipfile
from tabulate import tabulate
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
    '''
        This function creates `Backups` folder by default if that's not exists in the drive.
        You can also create other folders that you want.
    '''

    FOLDER_MIMETYPE = "application/vnd.google-apps.folder"

    # creating a folder if `Backups` folder is not exists
    if not FOLDER_NAME in folder_details(instance):
        print(f"Creating {FOLDER_NAME} folder...")
        up_folder = instance.CreateFile(
            {
                "title": FOLDER_NAME,
                "mimeType": FOLDER_MIMETYPE
            }
        )
        up_folder.Upload()
        print(f"{FOLDER_NAME} folder created.")
        print()
    else:
        print(f"{FOLDER_NAME} folder already exists.")
        print()


def folder_details(instance: GoogleDrive) -> Dict[str, str]:
    '''Returns all the `folder names` with their `folder ID` that is in the drive.'''
    
    FOLDER_MIMETYPE = "application/vnd.google-apps.folder"
    folders = dict()
    folder_list = instance.ListFile({
        "q": f"mimeType='{FOLDER_MIMETYPE}' and trashed=false"
    }).GetList()
    
    for folder in folder_list:
        folders.update(
            {
                folder.get("title"): folder.get("id")
            }
        )
    return folders


def get_backups_fol_id(instance: GoogleDrive) -> str:
    '''
        Returns `id` of `Backups` folder.
    '''

    fol_details = folder_details(instance)

    if "Backups" in fol_details:
        return fol_details.get("Backups")
    else:
        print("Backups folder is not found.")
        create_folder(drive)

        return folder_details(drive).get("Backups")


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


def upload_zip(instance: GoogleDrive, path: str, folder_id: Optional[str]=None) -> None:
    '''
        creating temporary buffer to store zip file 
        NOTE: created temporary file will be deleted after this context manager

        :param path: expected path should be `folder path` not `file path`
    '''

    with tempfile.NamedTemporaryFile(suffix=".zip") as temp_zip:

        # archiving the files that is in the given path
        with zipfile.ZipFile(temp_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:

            # iterating over each and every file in the given path
            for cur_path, _, files in list(os.walk(path)):
                for file in files:
                    zip_file.write(
                        filename=os.path.join(cur_path, file),
                        arcname=os.path.relpath(os.path.join(cur_path, file), os.path.join(path, ".."))
                    )

        # Uploading a file
        upload_file(
            instance=instance, 
            filename=f"{os.path.split(path)[-1]}.zip", 
            content_filename=temp_zip.name,
            folder_id=folder_id
        )


def save_to_local(instance: GoogleDrive) -> None:
    '''Saves the files to local directory from the `Backups` (from My Drive) folder.'''

    fol_details = folder_details(instance)

    if "Backups" in fol_details:
        folder_id = fol_details.get("Backups")

        files = instance.ListFile({
            "q": f"'{folder_id}' in parents and trashed=false"
        }).GetList()

        files_list = list()
        files_dict = dict()
        for index, file in enumerate(files, start=1):
            files_list.append([index, file.get("title")])
            files_dict.update({index: file.get("title")})

        print(tabulate(files_list, headers=["SI.NO", "FILE NAME"], tablefmt="simple_grid"))
        print()
        file_no = int(input("Enter the number corresponding to the filename which you want to save: "))
        print()
        print(f"Writing {files_dict.get(file_no)}...")
    else:
        raise Exception("Backups folder not found.")
    

if __name__ == "__main__":
    
    drive = authorization()
    path = argv[1]
    
    folder_id = get_backups_fol_id(drive)

    '''# uploading a zip file
    upload_zip(
        instance=drive,
        path=path,
        folder_id=folder_id
    )'''

    # downloading
    save_to_local(drive)
