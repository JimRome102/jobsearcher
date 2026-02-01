"""Email service for sending job digests using Gmail OAuth2."""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class EmailService:
    """Handle email sending and digest generation using OAuth2."""

    def __init__(self, user_email: str):
        """Initialize email service with OAuth2."""
        self.user_email = user_email
        self.credentials_path = Path('config/gmail_credentials.json')
        self.token_path = Path('config/gmail_token.json')
        self.service = None

        # Initialize Gmail API service
        self._init_gmail_service()

    def _init_gmail_service(self):
        """Initialize Gmail API service with OAuth2 credentials."""
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                print("Refreshing OAuth2 token...")
                creds.refresh(Request())
            else:
                # Run OAuth2 flow
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"\n❌ Gmail OAuth2 credentials not found!\n"
                        f"Expected location: {self.credentials_path}\n\n"
                        f"Please run: python setup_gmail_oauth.py\n"
                        f"Or see README.md for setup instructions."
                    )

                print("\n🔐 Starting OAuth2 authentication flow...")
                print("A browser window will open for you to authorize Gmail access.")

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

                print("✓ Authentication successful!")

            # Save credentials for next time
            self.token_path.parent.mkdir(exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            print(f"✓ Token saved to {self.token_path}")

        # Build Gmail API service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("✓ Gmail API service initialized")
        except HttpError as error:
            print(f'❌ An error occurred connecting to Gmail API: {error}')
            raise

    def send_digest(
        self,
        jobs: List[Dict],
        digest_type: str = 'morning',
        applications: List[Dict] = None,
        urgent_jobs: List[Dict] = None
    ):
        """Send job digest email via Gmail API."""
        subject = self._get_subject(digest_type, len(jobs))
        html_content = self._build_html_digest(
            jobs, digest_type, applications, urgent_jobs
        )

        self._send_email(subject, html_content)

    def _get_subject(self, digest_type: str, job_count: int) -> str:
        """Generate email subject line."""
        time_of_day = "Morning" if digest_type == 'morning' else "Evening"
        date_str = datetime.now().strftime("%b %d")

        if job_count == 0:
            return f"🔍 {time_of_day} Job Update ({date_str}) - No new matches"

        return f"🎯 {time_of_day} Job Update ({date_str}) - {job_count} new matches!"

    def _build_html_digest(
        self,
        jobs: List[Dict],
        digest_type: str,
        applications: List[Dict],
        urgent_jobs: List[Dict]
    ) -> str:
        """Build HTML email content."""
        # Sort jobs by match score
        jobs_sorted = sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)
        top_jobs = jobs_sorted[:10]  # Top 10 matches

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .job-card {{
                    background: #fff;
                    border: 1px solid #e1e4e8;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .job-card.urgent {{
                    border-left: 4px solid #f44336;
                }}
                .job-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #24292e;
                    margin: 0 0 8px 0;
                }}
                .job-company {{
                    font-size: 16px;
                    color: #586069;
                    margin: 0 0 12px 0;
                }}
                .job-meta {{
                    display: flex;
                    gap: 15px;
                    font-size: 14px;
                    color: #6a737d;
                    margin-bottom: 12px;
                }}
                .match-score {{
                    display: inline-block;
                    background: #28a745;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                .match-score.high {{
                    background: #28a745;
                }}
                .match-score.medium {{
                    background: #ffa726;
                }}
                .match-score.low {{
                    background: #9e9e9e;
                }}
                .reasoning {{
                    background: #f6f8fa;
                    border-left: 3px solid #667eea;
                    padding: 12px;
                    margin: 12px 0;
                    font-size: 14px;
                    color: #444;
                }}
                .btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: 600;
                    margin-top: 10px;
                }}
                .btn:hover {{
                    background: #5568d3;
                }}
                .section {{
                    margin: 30px 0;
                }}
                .section-title {{
                    font-size: 22px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #24292e;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: #f6f8fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .stat-number {{
                    font-size: 32px;
                    font-weight: 700;
                    color: #667eea;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #586069;
                    margin-top: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    color: #6a737d;
                    font-size: 14px;
                    border-top: 1px solid #e1e4e8;
                    margin-top: 40px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Your {"Morning" if digest_type == 'morning' else "Evening"} Job Update</h1>
                <p>{datetime.now().strftime("%A, %B %d, %Y")}</p>
            </div>
        """

        # Stats section
        html += f"""
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(jobs)}</div>
                    <div class="stat-label">New Matches</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([j for j in jobs if j.get('match_score', 0) >= 80])}</div>
                    <div class="stat-label">High Matches</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(urgent_jobs) if urgent_jobs else 0}</div>
                    <div class="stat-label">Urgent</div>
                </div>
            </div>
        """

        # Urgent jobs section
        if urgent_jobs and len(urgent_jobs) > 0:
            html += """
            <div class="section">
                <div class="section-title">🔥 Urgent Applications</div>
            """
            for job in urgent_jobs[:3]:
                html += self._build_job_card(job, urgent=True)
            html += "</div>"

        # Top matches section
        if len(top_jobs) > 0:
            html += """
            <div class="section">
                <div class="section-title">⭐ Top Matches</div>
            """
            for job in top_jobs[:5]:
                html += self._build_job_card(job)
            html += "</div>"

        # More opportunities section
        if len(top_jobs) > 5:
            html += """
            <div class="section">
                <div class="section-title">💼 More Opportunities</div>
            """
            for job in top_jobs[5:10]:
                html += self._build_job_card(job)
            html += "</div>"

        # Footer
        html += f"""
            <div class="footer">
                <p>You're receiving this because you signed up for automated job alerts.</p>
                <p>Next digest: {self._get_next_digest_time(digest_type)}</p>
                <p style="margin-top: 20px; font-size: 12px; color: #888;">
                    🔒 Secured with OAuth2 - No passwords stored
                </p>
            </div>
        </body>
        </html>
        """

        return html

    def _build_job_card(self, job: Dict, urgent: bool = False) -> str:
        """Build HTML for a single job card."""
        score = job.get('match_score', 0)
        score_class = 'high' if score >= 80 else 'medium' if score >= 60 else 'low'

        urgent_class = ' urgent' if urgent else ''

        return f"""
        <div class="job-card{urgent_class}">
            <div class="job-title">{job.get('title', 'Unknown Title')}</div>
            <div class="job-company">{job.get('company', 'Unknown Company')}</div>
            <div class="job-meta">
                <span>📍 {job.get('location', 'Location not specified')}</span>
                <span>💼 {job.get('source', '').title()}</span>
            </div>
            <span class="match-score {score_class}">{int(score)}% Match</span>
            <div class="reasoning">
                <strong>Why this matches:</strong> {job.get('match_reasoning', 'Good fit based on your profile')}
            </div>
            <a href="{job.get('url', '#')}" class="btn">View Job →</a>
        </div>
        """

    def _send_email(self, subject: str, html_content: str):
        """Send email via Gmail API."""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = self.user_email
            message['From'] = self.user_email
            message['Subject'] = subject

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send via Gmail API
            send_message = {'raw': encoded_message}
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            print(f"✓ Email sent successfully to {self.user_email}")
            print(f"  Message ID: {result['id']}")

        except HttpError as error:
            print(f"❌ Error sending email: {error}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error sending email: {e}")
            raise

    def _get_next_digest_time(self, current_digest_type: str) -> str:
        """Get next digest time."""
        if current_digest_type == 'morning':
            return "6:00 PM today"
        else:
            return "8:00 AM tomorrow"


def test_email_service():
    """Test email service with a sample email."""
    print("Testing Gmail OAuth2 email service...")

    email_service = EmailService('romejim@gmail.com')

    # Send test email
    test_jobs = [{
        'title': 'Test Job - Principal Product Manager',
        'company': 'Test Company',
        'location': 'New York, NY',
        'source': 'test',
        'match_score': 95,
        'match_reasoning': 'This is a test email to verify OAuth2 is working correctly.',
        'url': 'https://example.com/job',
    }]

    email_service.send_digest(test_jobs, 'morning')
    print("\n✓ Test email sent! Check your inbox at romejim@gmail.com")


if __name__ == '__main__':
    test_email_service()
