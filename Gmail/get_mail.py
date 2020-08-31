
from __future__ import print_function

import base64
import os
import pickle
import time
import sys

from apiclient import errors
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from working_dir.working_dir import working_dir as wd

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]


def build_service(gmail):
    '''
    build_service Makes connection to Gmail API

    Builds the service that allows the connection to Gmail API

    :param gmail: File Folder
    :type gmail: string
    :return: object to connect ot Gmail
    :rtype: string
    '''
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
                gmail+'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service


def get_message(service):
    '''
    get_message gets messages form Gmail as a list

    Gets email form Gmail that meet requirements and retruns a list
    of messages

    :param service: makes the connection to Gmail for specific account
    :type service: http cal
    :return: list of messages
    :rtype: list
    '''
    q=['label:UNREAD', 'from:papercut@pcssd.org']
    results = service.users().messages().list(
        userId='me', q=q).execute()  # q='from:papercut@pcssd.org'
    messages = results.get('messages', [])

    message_count = int(input('How many messages do you want to see?'))
    if not messages:
        print('No messages found.')
    else:
        print('messages:')
        for message in messages[:message_count]:
            msg = service.users().messages().get(
                userId='me', id=message['id']).execute()
            print(msg['snippet'])
            print(msg['payload']['partId'])
            print('\n')
            time.sleep(2)
        return messages


def get_attachments(service, messages, temp):
    '''
    get_attachments gets attachment form email

    Gets emails from Gmail and downloads the attachments

    :param service: makes the connection to Gmail for specific account
    :type service: http cal
    :param messages: Gmail messages returned
    :type messages: list of dict
    :param temp: temporary working folder
    :type temp: string
    '''
    print('Getting attachments.')
    try:
        for message in messages:
            msg = service.users().messages().get(
                userId='me', id=message['id']).execute()
            messagePayload = msg['payload']
            messagePart = messagePayload['parts']
            for temp_dict in messagePart:
                if temp_dict['filename'] != '':
                    print(temp_dict['filename'])
                    if 'data' in temp_dict['body']:
                        file_data = base64.urlsafe_b64encode(
                            temp_dict['body']['data'].encode('UTF-8'))
                    elif 'attachmentId' in temp_dict['body']:
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=message['id'], id=temp_dict['body']['attachmentId']
                        ).execute()
                        file_data = base64.urlsafe_b64decode(
                            attachment['data'].encode('UTF-8'))
                    else:
                        file_data = None
                    if file_data != None:
                        path = ''.join([temp, temp_dict['filename']])
                        with open(path, 'wb') as f:
                            f.write(file_data)
                    print('File has been written to temp')
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def main():
    googleProject, gmail, drive, temp = wd()
    service = build_service(gmail)
    messages = get_message(service)
    get_attachments(service, messages, temp)


if __name__ == '__main__':
    print('This file has to be called from the Main.py file')
    print('in the GoogleProjects Folder')
else:
    main()
