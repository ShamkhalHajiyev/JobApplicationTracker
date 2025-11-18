"""
Gmail OAuth 2.0 authentication with persistent token storage.

This module handles Gmail authentication using OAuth 2.0.
It manages tokens to avoid re-authentication every time.

How it works:
1. First time: Opens browser for OAuth → Saves token
2. Next time: Loads token from file → Uses it
3. Token expired: Auto-refreshes → Saves new token
4. Never asks for authentication again!

Prerequisites:
- You need OAuth credentials from Google Cloud Console
- Save them as: config/credentials/gmail_credentials.json
- Get them from: https://console.cloud.google.com/
"""

import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes - read-only access to emails
# We only need to READ emails, not send or delete them
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailAuthenticator:
    """
    Handles Gmail OAuth 2.0 authentication with token persistence.

    This class manages the entire OAuth flow:
    - Checks for existing token
    - Loads token if available
    - Refreshes token if expired
    - Runs OAuth flow if needed
    - Saves token for future use

    Example:
        authenticator = GmailAuthenticator()
        service = authenticator.get_gmail_service(Path("config/tokens/gmail.json"))

        # Now you can use 'service' to fetch emails!
    """

    def __init__(self, credentials_file: str = "config/credentials/gmail_credentials.json"):
        """
        Initialize Gmail authenticator.

        Args:
            credentials_file: Path to OAuth credentials JSON from Google Cloud Console

        Raises:
            FileNotFoundError: If credentials file doesn't exist

        To get credentials file:
        1. Go to https://console.cloud.google.com/
        2. Enable Gmail API
        3. Create OAuth 2.0 credentials (Desktop app)
        4. Download JSON and save as config/credentials/gmail_credentials.json
        """
        self.credentials_file = Path(credentials_file)

        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"❌ Gmail credentials not found: {credentials_file}\n\n"
                f"📋 Please follow these steps:\n"
                f"1. Go to https://console.cloud.google.com/\n"
                f"2. Enable Gmail API\n"
                f"3. Create OAuth 2.0 credentials (Desktop app)\n"
                f"4. Download JSON and save as {credentials_file}\n\n"
                f"See documentation for detailed instructions."
            )

    def authenticate(self, token_file: Path) -> Credentials:
        """
        Authenticate with Gmail and return credentials.

        This is the main authentication method. It:
        1. Checks if token file exists and is valid
        2. If token expired, auto-refreshes it
        3. If no token exists, runs OAuth flow (opens browser)
        4. Saves token for future use

        Args:
            token_file: Path to save/load OAuth token

        Returns:
            Valid Gmail credentials object

        Example:
            token_path = Path("config/tokens/gmail_personal.json")
            creds = authenticator.authenticate(token_path)
        """
        creds = None

        # Ensure token directory exists
        token_file.parent.mkdir(parents=True, exist_ok=True)

        # ========================================
        # Step 1: Check if token file exists
        # ========================================
        if token_file.exists():
            print(f"📂 Loading existing Gmail token from {token_file}")
            try:
                creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
                print("✅ Token loaded successfully")
            except Exception as e:
                print(f"⚠️ Error loading token: {e}")
                print("   Will re-authenticate...")
                creds = None

        # ========================================
        # Step 2: Check if credentials are valid
        # ========================================
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Token expired but can be refreshed
                print("🔄 Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"⚠️ Error refreshing token: {e}")
                    print("   Will re-authenticate...")
                    creds = None

            # ========================================
            # Step 3: Run OAuth flow if needed
            # ========================================
            if not creds:
                print("\n" + "=" * 60)
                print("🔐 GMAIL AUTHENTICATION REQUIRED")
                print("=" * 60)
                print("A browser window will open for you to authorize access.")
                print("Please sign in and grant permission to read your emails.")
                print("")
                print("✅ This only needs to be done ONCE - token will be saved.")
                print("✅ Future runs will use the saved token automatically.")
                print("=" * 60 + "\n")

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file),
                        SCOPES
                    )
                    # Run local server on random port
                    creds = flow.run_local_server(port=0)
                    print("\n✅ Authentication successful!")
                except Exception as e:
                    print(f"\n❌ Authentication failed: {e}")
                    raise

            # ========================================
            # Step 4: Save the credentials
            # ========================================
            print(f"💾 Saving token to {token_file}")
            try:
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                print("✅ Token saved - you won't need to authenticate again!")
            except Exception as e:
                print(f"⚠️ Error saving token: {e}")
                print("   Authentication was successful, but token couldn't be saved.")
                print("   You may need to authenticate again next time.")

        return creds

    def get_gmail_service(self, token_file: Path):
        """
        Get authenticated Gmail service.

        This is the main method you'll call to get a Gmail service object
        that can be used to fetch emails.

        Args:
            token_file: Path to OAuth token file

        Returns:
            Authenticated Gmail service object (googleapiclient.discovery.Resource)

        Example:
            service = authenticator.get_gmail_service(Path("config/tokens/gmail.json"))

            # Now fetch emails:
            results = service.users().messages().list(userId='me').execute()
        """
        creds = self.authenticate(token_file)

        print("🔧 Building Gmail service...")
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail service ready!\n")

        return service


def authenticate_gmail(token_file: Path,
                       credentials_file: str = "config/credentials/gmail_credentials.json"):
    """
    Convenience function to authenticate with Gmail.

    This is a simpler wrapper around the GmailAuthenticator class.
    Use this for quick authentication.

    Args:
        token_file: Path to save/load OAuth token
        credentials_file: Path to OAuth credentials JSON

    Returns:
        Authenticated Gmail service

    Example:
        from pathlib import Path
        from auth.gmail_auth import authenticate_gmail

        service = authenticate_gmail(Path("config/tokens/gmail_personal.json"))

        # Fetch emails
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        print(f"Found {len(messages)} emails")
    """
    authenticator = GmailAuthenticator(credentials_file)
    return authenticator.get_gmail_service(token_file)


# Example usage and testing
if __name__ == "__main__":
    """
    Test Gmail authentication.

    Run this file directly to test authentication:
        python auth/gmail_auth.py
    """

    print("=" * 60)
    print("TESTING GMAIL AUTHENTICATION")
    print("=" * 60)
    print()

    # Test authentication
    try:
        print("Attempting to authenticate with Gmail...")
        print()

        token_path = Path("config/tokens/gmail_test.json")
        service = authenticate_gmail(token_path)

        print("=" * 60)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        print("=" * 60)
        print()

        # Test by fetching user profile
        print("Testing Gmail API by fetching your profile...")
        profile = service.users().getProfile(userId='me').execute()
        print(f"📧 Email address: {profile['emailAddress']}")
        print(f"📬 Total messages: {profile['messagesTotal']}")
        print(f"📊 Threads total: {profile['threadsTotal']}")

        print()
        print("=" * 60)
        print("✅ Gmail authentication is working perfectly!")
        print("=" * 60)

    except FileNotFoundError as e:
        print("❌ ERROR:")
        print(str(e))
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        print()
        print("Please check:")
        print("1. credentials file exists at config/credentials/gmail_credentials.json")
        print("2. You have internet connection")
        print("3. You granted permission in the browser")