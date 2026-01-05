import os
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Scopes required for reading emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and return Gmail service object."""
    creds = None
    
    # Check if token.pickle exists (stored credentials)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_sent_emails(service, max_results=50, query=None):
    """Fetch sent emails with optional query filter."""
    
    # Build search query
    search_query = 'in:sent'
    if query:
        search_query += f' {query}'
    
    # Get list of messages
    results = service.users().messages().list(
        userId='me',
        q=search_query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    
    for msg in messages:
        # Fetch full message details
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        # Parse date
        date_str = headers.get('Date', '')
        
        # Get email body
        body = get_email_body(message['payload'])
        
        emails.append({
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': date_str,
            'snippet': message.get('snippet', ''),
            'body': body
        })
    
    return emails, results.get('nextPageToken')

def get_email_body(payload):
    """Extract email body from payload."""
    body = ''
    
    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
            elif 'parts' in part:
                # Handle nested parts
                body = get_email_body(part)
                if body:
                    break
    
    return body

def get_sent_emails_by_date(service, start_date, end_date, max_results=100):
    """Fetch sent emails within a date range."""
    query = f'after:{start_date} before:{end_date}'
    return get_sent_emails(service, max_results, query)


# Main execution
if __name__ == '__main__':
    # Authenticate
    service = authenticate_gmail()
    
    # Example 1: Get recent sent emails
    print("=== Recent Sent Emails ===\n")
    emails, next_page = get_sent_emails(service, max_results=10)
    
    for email in emails:
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print(f"Preview: {email['snippet'][:100]}...")
        print("-" * 50)
    
    # Example 2: Get sent emails for December 2025
    print("\n=== December 2025 Sent Emails ===\n")
    dec_emails, _ = get_sent_emails_by_date(
        service,
        start_date='2025/12/01',
        end_date='2025/12/31',
        max_results=20
    )
    
    for email in dec_emails:
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print("-" * 50)
    
    # Example 3: Search sent emails by keyword
    print("\n=== Sent Emails Mentioning 'Software Engineer' ===\n")
    filtered_emails, _ = get_sent_emails(
        service,
        max_results=10,
        query='subject:Software Engineer'
    )
    
    for email in filtered_emails:
        print(f"To: {email['to']}")
        print(f"Subject: {email['subject']}")
        print("-" * 50)