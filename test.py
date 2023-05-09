from __future__ import print_function

from googleapiclient.discovery import build
import oauth2client
import google_auth_oauthlib.flow
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify']
REDIRECT_URI = 'https://developers.google.com/oauthplayground/'
EMAIL = '2000shivam659@gmail.com'


def exchange_code(authorization_code):
    # exchange code to get the tokens and credentials
    flow = flow_from_clientsecrets('credentials.json', SCOPES)
    flow.redirect_uri = REDIRECT_URI
    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except HttpError as error:
        print(F'An error occurred: {error}')


def get_authorization_url(email_address, state=None):
    # to get the authorization url from OAuth 2.0 Playground
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    try:
        return authorization_url
    except FlowExchangeError as error:
        print('An error occurred: %s', error)


def load_or_get_credentials():
    try:
        with open('credentials.json') as cred_json:
            return oauth2client.client.Credentials.new_from_json(cred_json.read())
    except Exception as e:
        print(e)
        print(get_authorization_url(EMAIL))
        auth_code = input("Authorization Code: ")
        tokens = exchange_code(auth_code)
        # Save the credentials
        with open("tokens.json", "w") as cred_json:
            cred_json.write(tokens.to_json())
        return tokens


def send_replies_labels():
    creds = load_or_get_credentials()
    # Create a Gmail API client
    service = build('gmail', 'v1', credentials=creds)
    # Retrieve the user's Gmail messages
    results = service.users().messages().list(userId=EMAIL, q='is:unread', maxResults=10).execute()
    emails = results.get('messages', [])

    # Loop through the emails and reply to ones that have no prior replies
    for email in emails:
        msg = service.users().messages().get(userId=EMAIL, id=email['id']).execute()
        thread_id = msg['threadId']

        # Check if the email has any previous replies
        thread = service.users().threads().get(userId=EMAIL, id=thread_id).execute()
        if len(thread['messages']) != 1: continue

        i = next(i for i, header in enumerate(msg['payload']['headers']) if header['name'] == 'From')

        # The email has no previous replies, so compose a reply
        reply = MIMEText('Ok, I will look forward to your response.')
        reply['to'] = msg['payload']['headers'][i]['value']
        reply['subject'] = 'Re: ' + msg['payload']['headers'][17]['value']
        reply['In-Reply-To'] = msg['threadId']
        reply['References'] = msg['threadId']
        message = {'raw': base64.urlsafe_b64encode(reply.as_bytes()).decode(), 'threadId': thread_id}

        # Send the reply
        try:
            send_message = (service.users().messages().send(userId=EMAIL, body=message).execute())
            print(F'sent message to {msg["payload"]["headers"][i]["value"]} Message Id: {send_message["id"]}')

            # Send the label
            label_name = 'Replied'
            results = service.users().labels().list(userId='me').execute()
            label_id = next((label['id'] for label in results['labels'] if label['name'] == label_name), None)
            label = {"addLabelIds": [label_id]}
            response = service.users().messages().modify(userId=EMAIL, id=thread_id, body=label).execute()
            print(f'Moved email to label: {label_name}')
        except HttpError as error:
            print(F'An error occurred: {error}')


send_replies_labels()
