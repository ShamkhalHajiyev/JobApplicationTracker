"""
Outlook OAuth 2.0 authentication using MSAL with persistent token storage.

This module handles Outlook/Microsoft Graph API authentication.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import msal


class OutlookAuthenticator:
    """Handles Outlook OAuth 2.0 authentication with token persistence."""

    # Microsoft Graph API scopes
    SCOPES = ["https://graph.microsoft.com/Mail.Read"]

    def __init__(self,
                 client_id: str,
                 client_secret: str = None,
                 tenant_id: str = "common"):
        """
        Initialize Outlook authenticator.

        Args:
            client_id: Azure Application (client) ID
            client_secret: Azure Client Secret (optional for public client)
            tenant_id: Azure Tenant ID (default: "common" for personal accounts)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"

    def _get_token_cache(self, cache_file: Path) -> msal.SerializableTokenCache:
        """Get token cache from file or create new one."""
        cache = msal.SerializableTokenCache()

        if cache_file.exists():
            print(f"📂 Loading existing Outlook token from {cache_file}")
            with open(cache_file, 'r') as f:
                cache.deserialize(f.read())

        return cache

    def _save_token_cache(self, cache: msal.SerializableTokenCache, cache_file: Path):
        """Save token cache to file."""
        if cache.has_state_changed:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w') as f:
                f.write(cache.serialize())
            print(f"💾 Token saved to {cache_file}")

    def authenticate(self, token_file: Path) -> Dict[str, str]:
        """
        Authenticate with Outlook and return access token.
        """
        cache = self._get_token_cache(token_file)

        app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=cache
        )

        # Try to get token from cache first
        accounts = app.get_accounts()
        result = None

        if accounts:
            print(f"✅ Found {len(accounts)} cached account(s)")
            result = app.acquire_token_silent(
                scopes=self.SCOPES,
                account=accounts[0]
            )

            if result:
                print("✅ Using cached token")

        # If no cached token, need interactive authentication
        if not result:
            print("\n" + "=" * 60)
            print("🔐 OUTLOOK AUTHENTICATION REQUIRED")
            print("=" * 60)
            print("A browser window will open for you to authorize access.")
            print("This only needs to be done once - token will be cached.")
            print("=" * 60 + "\n")

            # Use device code flow
            flow = app.initiate_device_flow(scopes=self.SCOPES)

            if "user_code" not in flow:
                raise Exception("Failed to create device flow.")

            print(flow["message"])
            print("\n⏳ Waiting for authentication...")

            result = app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                print("\n✅ Authentication successful!")
            else:
                error = result.get("error")
                error_description = result.get("error_description")
                raise Exception(f"Authentication failed: {error}\n{error_description}")

        self._save_token_cache(cache, token_file)

        if "error" in result:
            raise Exception(f"Authentication error: {result.get('error')}\n{result.get('error_description')}")

        return result

    def get_access_token(self, token_file: Path) -> str:
        """Get valid access token for Microsoft Graph API."""
        result = self.authenticate(token_file)
        return result["access_token"]


def authenticate_outlook(token_file: Path,
                         client_id: str,
                         client_secret: str = None,
                         tenant_id: str = "common") -> str:
    """
    Convenience function to authenticate with Outlook.
    """
    authenticator = OutlookAuthenticator(client_id, client_secret, tenant_id)
    return authenticator.get_access_token(token_file)