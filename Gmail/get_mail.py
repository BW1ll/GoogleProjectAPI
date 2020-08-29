#!/usr/bin/env python3
from __future__ import print_function
import pickle
import os.path
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly', 
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
    ]

def build_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    service = build('gmail', 'v1', credentials=creds)

    return service
#
def find_mail(service):
    results = service.users().messages().list(userId='me', q='from:papercut@pcssd.org').execute()
    messages = results.get('messages', [])

    message_count = int(input('How many messages do you want to see?'))
    if not messages:
        print('No messages found.')
    else:
        print('messages:')
        for message in messages[:message_count]:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print(msg['snippet'])
            print('\n')
            time.sleep(2)
        return msg


service = build_service()
service_attachment = find_mail(service)
#find_mail_attachment(service_attachment)
#if __name__ == '__main__':
#    main()