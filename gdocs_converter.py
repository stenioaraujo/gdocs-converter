# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import pickle
import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
MIME_BASE = 'application/vnd.openxmlformats-officedocument'
EXTENSIONS = {
    'gdoc': {
        "mime": MIME_BASE + '.wordprocessingml.document',
        "out_ext": "docx"
    },
    'gsheet': {
        "mime": MIME_BASE + '.spreadsheetml.sheet',
        "out_ext": "xlsx"
    },
    'gslides': {
        "mime": MIME_BASE + '.presentationml.presentation',
        "out_ext": "pptx"
    }
}


def create_service():
    # Copyright 2018 Google LLC
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def all_files(start_dir):
    for root, _, files in os.walk(start_dir):
        rootpath = os.path.abspath(root)
        for filename in files:
            filename_parts = filename.split(".")
            ext, file_no_ext = None, None
            if len(filename_parts) > 1:
                ext = filename_parts[-1].lower()
                file_no_ext = '.'.join(filename_parts[:-1])

            result = {
                "relative": os.path.join(root, filename),
                "fqn": os.path.join(rootpath, filename),
                "rootpath": rootpath,
                "filename": filename,
                "file_without_ext": file_no_ext,
                "ext": ext
            }

            yield result


def path_to_download(file):
    """Verify if the file should be downloaded and return where

    If a file should be downloaded, the path where it should be downloaded is
    returned

    :param file: A dictionary with the keys:
        ("rootpath", "file_without_ext", "ext")
    :returns:
        -1 if extension doesn't match EXTENSIONS
        0 if file exists,
        FQN string otherwise
    """
    ext = file['ext']
    if ext not in EXTENSIONS:
        return -1

    out_filename = os.path.join(
        file['rootpath'],
        file['file_without_ext'] + '.' + EXTENSIONS[ext]['out_ext'])
    if os.path.exists(out_filename):
        return 0

    return out_filename


def download(drive_service, dst_download, file):
    """Download the file for the desired extension

    :param drive_service: An instance of the client for Google Drive Service
    :param dst_download: Destination path of the downloaded file
    :param file: A dictionary with the keys:
        ("fqn", "ext")
    """
    extension = EXTENSIONS[file['ext']]

    fileid = file_id(file['fqn'])
    request = drive_service.files().export_media(fileId=fileid, mimeType=extension['mime'])
    delete_file_if_error = not os.path.exists(dst_download)
    try:
        with open(dst_download, 'wb') as dst_file:
            downloader = MediaIoBaseDownload(dst_file, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
        return "OK"
    except Exception as e:
        if delete_file_if_error:
            delete_file(dst_download)

        err_msg = str(e).replace("\r", "")
        err_msg = err_msg.replace("\n", " ")
        return f"ERROR ({err_msg})"


def file_id(fqn):
    """Get the Google FileID

    :param fqn: path to a json-like file which contains the key: "doc_id"
    """
    with open(fqn) as json_file:
        result = json.load(json_file)
        return result['doc_id']


def delete_file(dst_download):
    if os.path.exists(dst_download):
        os.remove(dst_download)


def main(root_dir_path):
    drive_service = create_service()
    files = all_files(root_dir_path)
    for file in files:
        dst_download = path_to_download(file)
        if dst_download != -1:
            if dst_download == 0:
                status = "SKIPPED"
            else:
                status = download(drive_service, dst_download, file)
            print((file['relative'] + ' - ' + status).encode('utf-8'), flush=True)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        help = f"""The correct way of using it is:
    {args[0]} ROOT_DIR_PATH
Where ROOT_DIR_PATH is the start of your Google Drive directory
"""
        print(help)
    
    main(args[1])