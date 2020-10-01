from __future__ import print_function

import base64
import os
import os.path
import pandas as pd
import pickle
import re
import sys
import time

from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from working_dir.working_dir import working_dir as wd

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

def get_folers(drive_service):
    folder_id = '0B90NxPhuoYQ-UTFFTXA4X0JJVk0'
    query = f'parents = "{folder_id}"'
    q = ["mimeType = 'application/vnd.google-apps.folder'", query]

    response = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folders = response.get('folder', [])
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        folders.extend(response.get('folder', []))
        nextPageToken = response.get('nextPageToken')

    df = pd.DataFrame(folders)
    print(df)

drive_service = build_drive_service()
get_folers(drive_service)