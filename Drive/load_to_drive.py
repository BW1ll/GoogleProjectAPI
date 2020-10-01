
from __future__ import print_function

import base64
import os
import os.path
import pickle
import re
import sys
import time

from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from working_dir.working_dir import working_dir as wd
from working_dir.working_dir import month_years as my

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/drive.activity',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.appdata',
    'https://www.googleapis.com/auth/drive.install',
    'https://www.googleapis.com/auth/drive.metadata'
]


def build_drive_service():

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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service


def create_drive_folder_es(drive_service, year, month_year, num_month):
    def create_drive_folder_level(filename, parents):
        dirs = drive_service.ListFile(
            {'q': "'{}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'".format(
                parents[-1]['id'])})
        try:
            # this will give me the parent folder, if it exists
            current = [x for x in list(dirs)[0] if x['title'] == filename][0]
        except HttpError:
            current = None
        except IndexError:
            current = None
        if not current:
            meta = {
                'title': filename,
                'parents': [x['id'] for x in [parents[-1]]],
                'mimeType': 'application/vnd.google-apps.folder'
                }
            current= drive_service.CreateFile(meta)
            current.Upload({'convert': True})
            return current
        return current

    path= path.split('/')
    p= [dict(id='root')]
    for i in range(len(path)):
        p.append(create_drive_folder_level(path[i], p))

def load_drive():
    pass


def main():
    googleProject, gmail, drive, temp, month, year= wd()
    year, month_year, num_month =my()
    drive_service= build_drive_service()
    create_drive_folder_es(drive_service, year, month_year, num_month)
    create_drive_folder_pg(folder_structure_pg)
    load_drive()
