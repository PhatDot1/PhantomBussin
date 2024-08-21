import os
import requests
import gspread
from google.oauth2.service_account import Credentials

# Airtable API setup using environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID2')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID2')
AIRTABLE_URL = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}'

# Google Sheets setup
GOOGLE_SHEET_ID = '18b3FEQ6MwUXdD1FykypSkRgwRxmxE6qINPmK9-NKtSA'
SHEET_NAME = 'CloudInt'

# Define the scope for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate with Google Sheets using your credentials file
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)

# Fetch the data from Google Sheets
data = sheet.get_all_records()

# Prepare the data for Airtable
records_to_update = []
for row in data:
    if row['Done'] != 'Yes':
        # Clean the skills from 'allSkills' column
        all_skills = row['allSkills'].split(', ')[:6]
        skills_columns = {f'skill{i+1}': all_skills[i] if i < len(all_skills) else '' for i in range(6)}

        # Create a record dictionary to push to Airtable
        record = {
            'fields': {
                'LinkedIn URL': row['baseUrl'],
                'Headline': row['headline'],
                'Location': row['location'],
                'ImgUrl': row['imgUrl'],
                'Company': row['company'],
                'Company URL': row['companyUrl'],
                'Job Title': row['jobTitle'],
                'Job Location': row['jobLocation'],
                'Job Date Range': row['jobDateRange'],
                'Job Duration': row['jobDuration'],
                'Company 2': row['company2'],
                'Company 2 URL': row['companyUrl2'],
                'Job Title 2': row['jobTitle2'],
                'Job Date Range 2': row['jobDateRange2'],
                'Job Duration 2': row['jobDuration2'],
                'School': row['school'],
                'School Degree': row['schoolDegree'],
                'School Date Range': row['schoolDateRange'],
                'All Skills': row['allSkills'],
                'Skill 1': skills_columns['skill1'],
                'Skill 2': skills_columns['skill2'],
                'Skill 3': skills_columns['skill3'],
                'Skill 4': skills_columns['skill4'],
                'Skill 5': skills_columns['skill5'],
                'Skill 6': skills_columns['skill6'],
                'Job Location 2': row['jobLocation2'],
                'School 2': row['school2'],
                'School Degree 2': row['schoolDegree2'],
                'School 2 Date Range': row['schoolDateRange2'],
                'Description': row['description'],
                'Job Description': row['jobDescription'],
                'Job Description 2': row['jobDescription2'],
                'Matching': 'Match'
            }
        }
        records_to_update.append((row, record))

# Push the updated records to Airtable and mark as 'Done'
headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

for row, record in records_to_update:
    response = requests.post(AIRTABLE_URL, headers=headers, json=record)
    if response.status_code == 200:
        # Mark the corresponding row in Google Sheets as 'Done'
        row_index = data.index(row) + 2  # Adding 2 to account for header row and 1-based index in Sheets
        sheet.update_cell(row_index, sheet.find('Done').col, 'Yes')
        print(f"Record {record['fields']['LinkedIn URL']} updated successfully.")
    else:
        print(f"Error updating record {record['fields']['LinkedIn URL']}: {response.content}")
