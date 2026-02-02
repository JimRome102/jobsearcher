"""Google Sheets service for job tracking."""

import os
from typing import List, Dict
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path


class SheetsService:
    """Service for managing jobs in Google Sheets."""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self):
        """Initialize Google Sheets service."""
        self.creds = None
        self.service = None
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        token_path = Path(__file__).parent.parent / 'config' / 'sheets_token.json'
        credentials_path = Path(__file__).parent.parent / 'config' / 'sheets_credentials.json'

        # Load existing token if available
        if token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

        # If no valid credentials, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing Google Sheets OAuth2 token...")
                self.creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        f"Google Sheets credentials not found at {credentials_path}\n"
                        "Please download OAuth2 credentials from Google Cloud Console"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for next run
            token_path.write_text(self.creds.to_json())
            print(f"✓ Token saved to {token_path}")

        self.service = build('sheets', 'v4', credentials=self.creds)
        print("✓ Google Sheets API service initialized")

    def create_job_tracker_spreadsheet(self, title: str = "Job Search Tracker") -> str:
        """Create a new job tracker spreadsheet with proper formatting."""
        try:
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Jobs',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Contacts',
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Stats',
                        }
                    }
                ]
            }

            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheetId']
            print(f"✓ Created spreadsheet: {spreadsheet_id}")
            print(f"✓ View at: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

            # Set up headers
            self._setup_headers(spreadsheet_id)
            self._setup_contacts_headers(spreadsheet_id)

            # Set up Stats sheet
            self._setup_stats_sheet(spreadsheet_id)

            return spreadsheet_id

        except HttpError as error:
            print(f"Error creating spreadsheet: {error}")
            return None

    def _setup_headers(self, spreadsheet_id: str):
        """Set up header row with formatting."""
        headers = [
            'Job Title', 'Company', 'Location', 'Match Score', 'Salary Min', 'Salary Max',
            'Posted Date', 'Status', 'Applied Date', 'Source', 'URL', 'Notes', 'Match Reasoning'
        ]

        # Write headers
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Jobs!A1:M1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()

        # Format headers (bold, frozen)
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.86},
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            },
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 13
                    }
                }
            }
        ]

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

    def _setup_contacts_headers(self, spreadsheet_id: str):
        """Set up Contacts sheet header row."""
        headers = [
            'Job', 'Contact Title', 'Reasoning', 'Confidence',
            'Primary Email (Guess)', 'Other Email Guesses', 'LinkedIn Search URL',
            'Connected', 'Response', 'Notes'
        ]

        # Write headers
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Contacts!A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()

        # Format headers
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 1,  # Contacts sheet ID
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.5, 'green': 0.7, 'blue': 0.4},
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            },
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 1,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 10
                    }
                }
            }
        ]

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()

    def _setup_stats_sheet(self, spreadsheet_id: str):
        """Set up Stats sheet with formulas."""
        stats_data = [
            ['Job Search Statistics', ''],
            ['', ''],
            ['Total Jobs', '=COUNTA(Jobs!A2:A)'],
            ['Applied', '=COUNTIF(Jobs!H2:H,"applied")'],
            ['Interviewing', '=COUNTIF(Jobs!H2:H,"interviewing")'],
            ['Rejected', '=COUNTIF(Jobs!H2:H,"rejected")'],
            ['Offer', '=COUNTIF(Jobs!H2:H,"offer")'],
            ['', ''],
            ['Average Match Score', '=AVERAGE(Jobs!D2:D)'],
            ['High Match Jobs (80%+)', '=COUNTIF(Jobs!D2:D,">=80")'],
            ['', ''],
            ['Midtown Manhattan Jobs', '=COUNTIF(Jobs!C2:C,"*Midtown*")'],
            ['Remote Jobs', '=COUNTIF(Jobs!C2:C,"*Remote*")'],
        ]

        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Stats!A1:B13',
            valueInputOption='USER_ENTERED',
            body={'values': stats_data}
        ).execute()

    def add_jobs_to_sheet(self, jobs: List[Dict], spreadsheet_id: str = None):
        """Add jobs to the spreadsheet."""
        if not spreadsheet_id:
            spreadsheet_id = self.spreadsheet_id

        if not spreadsheet_id:
            print("⚠ No spreadsheet ID configured. Set GOOGLE_SHEETS_ID in .env")
            return

        try:
            # Prepare job rows
            rows = []
            for job in jobs:
                row = [
                    job.get('title', ''),
                    job.get('company', ''),
                    job.get('location', ''),
                    job.get('match_score', 0),
                    job.get('salary_min', ''),
                    job.get('salary_max', ''),
                    self._format_date(job.get('posted_date')),
                    job.get('status', 'new'),
                    '',  # Applied date - empty initially
                    job.get('source', ''),
                    job.get('url', ''),
                    '',  # Notes - empty initially
                    job.get('match_reasoning', ''),
                ]
                rows.append(row)

            # Get existing data to find next row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Jobs!A:A'
            ).execute()

            existing_rows = len(result.get('values', []))
            next_row = existing_rows + 1

            # Append new jobs
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f'Jobs!A{next_row}',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

            print(f"✓ Added {len(jobs)} jobs to Google Sheets")
            print(f"✓ View at: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

        except HttpError as error:
            print(f"Error adding jobs to sheet: {error}")

    def update_job_status(self, job_title: str, company: str, status: str, spreadsheet_id: str = None):
        """Update the status of a specific job."""
        if not spreadsheet_id:
            spreadsheet_id = self.spreadsheet_id

        try:
            # Find the job row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Jobs!A:H'
            ).execute()

            rows = result.get('values', [])

            for i, row in enumerate(rows[1:], start=2):  # Skip header
                if len(row) >= 2 and row[0] == job_title and row[1] == company:
                    # Update status
                    self.service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Jobs!H{i}',
                        valueInputOption='RAW',
                        body={'values': [[status]]}
                    ).execute()

                    # If status is 'applied', set applied date
                    if status == 'applied':
                        self.service.spreadsheets().values().update(
                            spreadsheetId=spreadsheet_id,
                            range=f'Jobs!I{i}',
                            valueInputOption='USER_ENTERED',
                            body={'values': [[datetime.now().strftime('%Y-%m-%d')]]}
                        ).execute()

                    print(f"✓ Updated {job_title} at {company} to '{status}'")
                    return

            print(f"⚠ Job not found: {job_title} at {company}")

        except HttpError as error:
            print(f"Error updating job status: {error}")

    def add_contacts_to_sheet(self, contacts: List[Dict], spreadsheet_id: str = None):
        """Add contacts to the Contacts sheet."""
        if not spreadsheet_id:
            spreadsheet_id = self.spreadsheet_id

        if not spreadsheet_id:
            print("⚠ No spreadsheet ID configured")
            return

        try:
            # Prepare contact rows
            rows = []
            for contact in contacts:
                row = [
                    contact.get('job', ''),
                    contact.get('title', ''),
                    contact.get('reasoning', ''),
                    contact.get('confidence', ''),
                    contact.get('primary_email', ''),
                    contact.get('all_email_guesses', ''),
                    contact.get('linkedin_search', ''),
                    '',  # Connected - empty initially
                    '',  # Response - empty initially
                    '',  # Notes - empty initially
                ]
                rows.append(row)

            # Get existing data to find next row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Contacts!A:A'
            ).execute()

            existing_rows = len(result.get('values', []))
            next_row = existing_rows + 1

            # Append new contacts
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f'Contacts!A{next_row}',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

            print(f"✓ Added {len(contacts)} contacts to Google Sheets")

        except HttpError as error:
            print(f"Error adding contacts to sheet: {error}")

    def _format_date(self, date_val) -> str:
        """Format date for sheets."""
        if not date_val:
            return ''

        if isinstance(date_val, str):
            return date_val

        if isinstance(date_val, datetime):
            return date_val.strftime('%Y-%m-%d')

        return str(date_val)


def setup_sheets_integration():
    """Interactive setup for Google Sheets integration."""
    print("\n" + "="*60)
    print("GOOGLE SHEETS INTEGRATION SETUP")
    print("="*60)
    print("\nThis will create a Google Sheets job tracker for you.")
    print("\nSteps:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select your project (or create one)")
    print("3. Enable Google Sheets API")
    print("4. Create OAuth 2.0 credentials (Desktop app)")
    print("5. Download credentials to config/sheets_credentials.json")
    print("\nPress Enter when ready...")
    input()

    try:
        sheets = SheetsService()
        spreadsheet_id = sheets.create_job_tracker_spreadsheet()

        print("\n" + "="*60)
        print("✓ SETUP COMPLETE")
        print("="*60)
        print(f"\nYour spreadsheet ID: {spreadsheet_id}")
        print(f"\nView at: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        print("\nAdd this to your .env file:")
        print(f"GOOGLE_SHEETS_ID={spreadsheet_id}")
        print("\nYour jobs will now be synced to this spreadsheet automatically!")

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nPlease ensure:")
        print("1. You've downloaded credentials to config/sheets_credentials.json")
        print("2. Google Sheets API is enabled in your project")


if __name__ == '__main__':
    setup_sheets_integration()
