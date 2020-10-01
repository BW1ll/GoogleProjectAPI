
from __future__ import print_function

import base64
import os
import pickle
import re
import sys
import time

from apiclient import errors
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow3
from googleapiclient.discovery import build

from working_dir.working_dir import working_dir as wd

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]


def build_gmail_service(gmail):
    '''
    build_gmail_service Makes connection to Gmail API

    Builds the gmail_service that allows the connection to Gmail API

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

    gmail_service = build('gmail', 'v1', credentials=creds)

    return gmail_service


def get_message(gmail_service):
    '''
    get_message gets messages form Gmail as a list

    Gets email form Gmail that meet requirements and retruns a list
    of messages

    :param gmail_service: makes the connection to Gmail for specific account
    :type gmail_service: http call
    :return: list of messages
    :rtype: list
    '''
    # q contains required Gmail labels to get correct files
    q='label:UNREAD from:papercut@pcssd.org has:attachment'
    # gets request messages and retruns a list
    results = gmail_service.users().messages().list(
        userId='me', q=q).execute()
    messages = results.get('messages', [])

    # gets the number of messages to be displayed
    message_count = int(input('How many messages do you want to see?'))
    if not messages:
        print('No messages found.')
        exit()
    else:
        print('messages:')
        for message in messages[:message_count]:
            msg = gmail_service.users().messages().get(
                userId='me', id=message['id']).execute()
            print(msg['snippet'])
            print(msg['payload']['partId'])
            print('\n')
            time.sleep(1)
        # returns the list of messages    
        return messages


def get_attachments(gmail_service, messages, temp):
    '''
    get_attachments gets attachment form email

    Gets emails from Gmail and downloads the attachments

    :param gmail_service: makes the connection to Gmail for specific account
    :type gmail_service: http cal
    :param messages: Gmail messages returned
    :type messages: list of dict
    :param temp: temporary working folder
    :type temp: string
    '''
    # search patterns for subject line in mail
    executive_summary = r'(:\s(.+)\sE)'
    printer_groups = r'(P[a-z].+- (s[a-z]{6}[A-Z]{3}?|s[a-z]{6}))'
    date_of_report = r'(([A-Z][a-z]{2})\s\d,\s(\d{4}))'
    print('Getting attachments.')
    try:
        for message in messages:
            msg = gmail_service.users().messages().get(
                userId='me', id=message['id']).execute()
            messagePayload = msg['payload']
            subject_list = messagePayload['headers'][21:22] 
            subject_dict = subject_list.pop() # gets the dict that contains the subject
            # breaks down the dict to get the subject as a string
            # then pulls the name to name the file
            for name, value in subject_dict.items():
                subject_full = value
                es = re.search(executive_summary, value)
                pg = re.search(printer_groups, value)
                if es != None:
                    sch_name = es.group(2)
                elif pg != None:
                    pg_name = pg.group(1)
            messagePart = messagePayload['parts']
            # pulls the attachment data out of the message
            for temp_dict in messagePart:
                if temp_dict['filename'] != '':
                    if 'data' in temp_dict['body']:
                        file_data = base64.urlsafe_b64encode(
                            temp_dict['body']['data'].encode('UTF-8'))
                    elif 'attachmentId' in temp_dict['body']:
                        attachment = gmail_service.users().messages().attachments().get(
                            userId='me', messageId=message['id'], id=temp_dict['body']['attachmentId']
                        ).execute()
                        file_data = base64.urlsafe_b64decode(
                            attachment['data'].encode('UTF-8'))
                    else:
                        file_data = None
                    # combines the filename and the name form the subject and writes
                    # the file to a temp directory
                    if file_data != None:
                        if sch_name != None:
                            new_filename = sch_name +' '+ temp_dict['filename']
                            path = ''.join([temp, new_filename])
                        elif pg_name != None:
                            new_filename = pg_name +' '+ temp_dict['filename']
                            path = ''.join([temp, new_filename])
                        with open(path, 'wb') as f:
                            f.write(file_data)
                            print(f'{new_filename} as been created')
                            # these variables need to be set to none for next pass in for loop
                            pg_name = None
                            sch_name = None
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def main():
    googleProject, gmail, drive, temp = wd()
    gmail_service = build_gmail_service(gmail)
    messages = get_message(gmail_service)
    get_attachments(gmail_service, messages, temp)
    return print(' All files have been downloaded')

main()
#if __name__ == '__main__':
#    print('This file has to be called from the Main.py file')
#    print('in the GoogleProjects Folder')
#else:
#    main()
