import os
import requests
import gspread
from google.oauth2.service_account import Credentials

# Airtable API setup using environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
AIRTABLE_URL = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'

# Google Sheets setup
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
QUEUE_ID_UPDATE = '21/08/2024 CLOUDTIME'

# Define the scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate with Google Sheets using your credentials file
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# Fetch records from Airtable
headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}'
}

params = {
    'filterByFormula': 'AND({Queue ID}="", FIND("/in/", {Proper LinkedIn}), {Scraped}="")'
}

response = requests.get(AIRTABLE_URL, headers=headers, params=params)
records = response.json().get('records', [])

# Process each record
for record in records:
    linkedin_url = record['fields'].get('Proper LinkedIn', '')
    
    # Add LinkedIn URL to Google Sheets
    sheet.append_row([linkedin_url])

    # Update Queue ID in Airtable
    record_id = record['id']
    update_data = {
        'fields': {
            'Queue ID': QUEUE_ID_UPDATE
        }
    }
    update_response = requests.patch(f'{AIRTABLE_URL}/{record_id}', headers=headers, json=update_data)

    if update_response.status_code == 200:
        print(f'Record {record_id} updated successfully.')
    else:
        print(f'Error updating record {record_id}: {update_response.content}')
