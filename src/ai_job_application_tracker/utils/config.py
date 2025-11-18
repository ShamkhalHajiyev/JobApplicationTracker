"""
Configuration management for Job Application Tracker.

This module loads settings from config/config.yaml and provides easy access
to all configuration throughout the application.

The configuration includes:
- Email accounts (Gmail, Outlook, iCloud)
- LLM provider settings (Claude, ChatGPT, Gemini)
- Google Sheets integration
- General application settings
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, EmailStr, Field


class EmailAccountConfig(BaseModel):
    """
    Configuration for a single email account.

    This represents one email account from your config.yaml file.
    For example, your Gmail account or Outlook account.
    """

    name: str = Field(..., description="Account display name (e.g., 'Personal Gmail')")
    provider: str = Field(..., description="Provider type: gmail, outlook, or imap")
    email: EmailStr = Field(..., description="Email address")
    enabled: bool = Field(True, description="Whether this account is enabled")

    # OAuth token file path (for gmail and outlook)
    token_file: Optional[str] = Field(None, description="Path to OAuth token file")

    # IMAP-specific settings (for iCloud)
    imap_server: Optional[str] = Field(None, description="IMAP server address")
    imap_port: Optional[int] = Field(None, description="IMAP port")
    app_password: Optional[str] = Field(None, description="App-specific password")

    # Outlook-specific settings
    client_id: Optional[str] = Field(None, description="Azure Application ID")
    client_secret: Optional[str] = Field(None, description="Azure Client Secret")
    tenant_id: Optional[str] = Field(None, description="Azure Tenant ID")


class LLMConfig(BaseModel):
    """
    LLM provider configuration.

    This holds settings for your AI provider (Claude, ChatGPT, or Gemini).
    """

    provider: str = Field(..., description="Which LLM to use: anthropic, openai, google, ollama")
    anthropic: Optional[Dict[str, Any]] = None
    openai: Optional[Dict[str, Any]] = None
    google: Optional[Dict[str, Any]] = None
    ollama: Optional[Dict[str, Any]] = None


class GoogleSheetsConfig(BaseModel):
    """Google Sheets configuration for exporting job applications."""

    enabled: bool = Field(True, description="Whether Sheets integration is enabled")
    spreadsheet_id: str = Field(..., description="Google Sheets ID")
    credentials_file: str = Field(..., description="Path to service account JSON")
    sheet_name: str = Field("JobApplications", description="Sheet tab name")


class GeneralSettings(BaseModel):
    """General application settings."""

    fetch_hours: int = Field(24, description="Hours to fetch on subsequent runs")
    log_level: str = Field("INFO", description="Logging level")
    sync_schedule: List[str] = Field(
        default_factory=lambda: ["08:00", "13:00", "18:00"],
        description="Daily sync times"
    )


class Config:
    """
    Main configuration class.

    This class loads your config.yaml and provides easy access to all settings.

    Example usage:
        config = get_config()

        # Get all enabled accounts
        accounts = config.get_enabled_accounts()

        # Check if Gmail token exists
        has_token = config.token_exists("hajiyev.shamkhal@gmail.com")

        # Get Claude API key
        api_key = config.llm.anthropic['api_key']
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to config.yaml file (default: config/config.yaml)
        """
        self.config_path = Path(config_path)

        # Check if config file exists
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Please create it from config/config.yaml.example\n"
                f"Or make sure you're running from the project root directory."
            )

        # Load YAML file
        print(f"📂 Loading configuration from: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self._raw_config = yaml.safe_load(f)

        # Parse email accounts into Pydantic models
        self.accounts = [
            EmailAccountConfig(**account)
            for account in self._raw_config.get('accounts', [])
        ]
        print(f"   ✓ Loaded {len(self.accounts)} email account(s)")

        # Parse LLM configuration
        llm_data = self._raw_config.get('llm', {})
        if llm_data:
            self.llm = LLMConfig(**llm_data)
            print(f"   ✓ LLM provider: {self.llm.provider}")
        else:
            self.llm = None
            print(f"   ⚠️ No LLM configured")

        # Parse Google Sheets configuration
        sheets_data = self._raw_config.get('google_sheets', {})
        if sheets_data and sheets_data.get('enabled'):
            self.google_sheets = GoogleSheetsConfig(**sheets_data)
            print(f"   ✓ Google Sheets: enabled")
        else:
            self.google_sheets = None
            print(f"   ✓ Google Sheets: disabled")

        # Parse general settings
        self.settings = GeneralSettings(**self._raw_config.get('settings', {}))
        print(f"   ✓ Settings loaded\n")

    def save(self):
        """
        Save current configuration back to YAML file.

        Useful when the Streamlit UI modifies settings.
        """
        config_dict = {
            'accounts': [acc.dict() for acc in self.accounts],
            'settings': self.settings.dict()
        }

        if self.llm:
            config_dict['llm'] = self.llm.dict()

        if self.google_sheets:
            config_dict['google_sheets'] = self.google_sheets.dict()

        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        print(f"💾 Configuration saved to: {self.config_path}")

    def add_account(self, account: EmailAccountConfig):
        """
        Add a new email account to configuration.

        If an account with the same email already exists, it will be updated.

        Args:
            account: EmailAccountConfig object to add
        """
        # Check if account already exists
        for i, existing in enumerate(self.accounts):
            if existing.email == account.email:
                # Update existing account
                self.accounts[i] = account
                print(f"📧 Updated account: {account.email}")
                self.save()
                return

        # Add new account
        self.accounts.append(account)
        print(f"📧 Added new account: {account.email}")
        self.save()

    def remove_account(self, email: str):
        """
        Remove an email account from configuration.

        Args:
            email: Email address of account to remove
        """
        original_count = len(self.accounts)
        self.accounts = [acc for acc in self.accounts if acc.email != email]

        if len(self.accounts) < original_count:
            print(f"🗑️ Removed account: {email}")
            self.save()
        else:
            print(f"⚠️ Account not found: {email}")

    def get_enabled_accounts(self) -> List[EmailAccountConfig]:
        """
        Get list of enabled email accounts.

        Returns:
            List of EmailAccountConfig objects where enabled=True
        """
        return [acc for acc in self.accounts if acc.enabled]

    def get_account_by_email(self, email: str) -> Optional[EmailAccountConfig]:
        """
        Get account configuration by email address.

        Args:
            email: Email address to search for

        Returns:
            EmailAccountConfig object if found, None otherwise
        """
        for account in self.accounts:
            if account.email == email:
                return account
        return None

    def get_token_path(self, account_email: str) -> Optional[Path]:
        """
        Get the full path to the OAuth token file for an account.

        This is where the OAuth token will be saved after authentication.

        Args:
            account_email: Email address of the account

        Returns:
            Path to token file, or None if not configured
        """
        account = self.get_account_by_email(account_email)
        if account and account.token_file:
            token_path = Path(account.token_file)
            # Ensure parent directory exists
            token_path.parent.mkdir(parents=True, exist_ok=True)
            return token_path
        return None

    def token_exists(self, account_email: str) -> bool:
        """
        Check if OAuth token file exists for an account.

        Used to determine if we need to run OAuth flow or can use existing token.

        Args:
            account_email: Email address of the account

        Returns:
            True if token file exists, False otherwise
        """
        token_path = self.get_token_path(account_email)
        return token_path is not None and token_path.exists()

    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the active LLM provider configuration.

        Returns:
            Dictionary with API key, model, etc. for active provider
        """
        if not self.llm:
            return None

        provider = self.llm.provider

        if provider == "anthropic" and self.llm.anthropic:
            return self.llm.anthropic
        elif provider == "openai" and self.llm.openai:
            return self.llm.openai
        elif provider == "google" and self.llm.google:
            return self.llm.google
        elif provider == "ollama" and self.llm.ollama:
            return self.llm.ollama

        return None


# Singleton pattern - ensures only one Config instance exists
_config_instance: Optional[Config] = None


def get_config(config_path: str = "config/config.yaml") -> Config:
    """
    Get configuration singleton instance.

    This ensures we only load the config file once and reuse the same instance.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Config instance

    Example:
        config = get_config()
        accounts = config.get_enabled_accounts()
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def reload_config(config_path: str = "config/config.yaml") -> Config:
    """
    Force reload configuration from file.

    Useful when the config file has been modified externally.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Fresh Config instance
    """
    global _config_instance
    _config_instance = None
    return get_config(config_path)


# Example usage (for testing)
if __name__ == "__main__":
    # Load configuration
    config = get_config()

    # Display loaded accounts
    print("=" * 60)
    print("LOADED CONFIGURATION:")
    print("=" * 60)

    print(f"\n📧 Email Accounts ({len(config.accounts)} total):")
    for acc in config.accounts:
        status = "✓ enabled" if acc.enabled else "✗ disabled"
        token_status = "🔐 has token" if config.token_exists(acc.email) else "⚠️ no token"
        print(f"   • {acc.name} ({acc.email}) [{acc.provider}] - {status} - {token_status}")

    print(f"\n🤖 LLM Configuration:")
    if config.llm:
        print(f"   Provider: {config.llm.provider}")
        llm_config = config.get_llm_config()
        if llm_config:
            print(f"   Model: {llm_config.get('model', 'N/A')}")
            print(f"   API Key: {'*' * 20}...{llm_config.get('api_key', '')[-8:]}")
    else:
        print(f"   No LLM configured")

    print(f"\n⚙️ General Settings:")
    print(f"   Fetch hours: {config.settings.fetch_hours}")
    print(f"   Log level: {config.settings.log_level}")
    print(f"   Sync schedule: {', '.join(config.settings.sync_schedule)}")

    print("\n" + "=" * 60)