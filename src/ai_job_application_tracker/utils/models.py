"""
Data models for Job Application Tracker.

This module defines Pydantic models for email data and job application information.
These models provide validation and type safety throughout the application.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class EmailProvider(str, Enum):
    """
    Email service providers supported by the application.

    Used to identify which provider an email came from.
    """
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    IMAP = "imap"


class EmailData(BaseModel):
    """
    Raw email data fetched from email providers.

    This represents a single email with all its metadata and content.
    Used as the input to the LLM analyzer.

    Attributes:
        email_id: Unique identifier from the email provider
        subject: Email subject line
        sender: Email address of sender
        sender_name: Display name of sender (if available)
        body: Full text content of email (plain text)
        date: When the email was received
        provider: Which service the email came from
        account_email: Which of your accounts received this email
    """

    email_id: str = Field(..., description="Unique email ID from provider")
    subject: str = Field(..., description="Email subject line")
    sender: str = Field(..., description="Sender email address")
    sender_name: Optional[str] = Field(None, description="Sender display name")
    body: str = Field(..., description="Email body content (plain text)")
    date: datetime = Field(..., description="Email received date")
    provider: EmailProvider = Field(..., description="Email provider source")
    account_email: EmailStr = Field(..., description="Account that received this email")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApplicationStatus(str, Enum):
    """
    Job application status categories.

    These are the categories the LLM will classify emails into.
    """
    NEW_APPLICATION = "new_application"  # Application submission confirmation
    UPDATE = "update"  # Status update (e.g., "under review")
    INTERVIEW = "interview"  # Interview invitation/scheduling
    REJECTION = "rejection"  # Application rejected
    OFFER = "offer"  # Job offer received
    NOT_JOB_RELATED = "not_job_related"  # Not a job application email


class JobApplicationData(BaseModel):
    """
    Structured job application data extracted from emails by LLM.

    This represents the analyzed result after the LLM processes an email.
    Contains all the job-related information extracted from the email.

    Attributes:
        email_id: Reference to original email
        email_date: When the email was received
        account_email: Which account received it
        company_name: Name of company (extracted by LLM)
        position_title: Job title (extracted by LLM)
        status: Classification (new_application/interview/rejection/etc.)
        details: Additional context (extracted by LLM)
        interview_date: If it's an interview, when is it scheduled
    """

    # Email reference
    email_id: str = Field(..., description="Reference to original email ID")
    email_date: datetime = Field(..., description="When email was received")
    account_email: EmailStr = Field(..., description="Account that received this")

    # LLM-extracted fields (will be populated in Phase 2)
    company_name: Optional[str] = Field(None, description="Company name")
    position_title: Optional[str] = Field(None, description="Job position title")
    status: ApplicationStatus = Field(
        ApplicationStatus.NOT_JOB_RELATED,
        description="Email classification"
    )
    details: Optional[str] = Field(None, description="Additional details/context")
    interview_date: Optional[datetime] = Field(None, description="Interview date if applicable")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Example usage (for documentation purposes):
if __name__ == "__main__":
    # Example: Creating an EmailData object
    email = EmailData(
        email_id="msg123456",
        subject="Interview Invitation - AI Engineer",
        sender="recruiter@company.com",
        sender_name="Jane Doe",
        body="We'd like to invite you for an interview...",
        date=datetime.now(),
        provider=EmailProvider.GMAIL,
        account_email="hajiyev.shamkhal@gmail.com"
    )

    print("Email created:", email.subject)
    print("From:", email.sender_name)

    # Example: Creating a JobApplicationData object
    job_app = JobApplicationData(
        email_id="msg123456",
        email_date=datetime.now(),
        account_email="hajiyev.shamkhal@gmail.com",
        company_name="Google",
        position_title="Software Engineer",
        status=ApplicationStatus.INTERVIEW,
        details="Phone screen scheduled for next Tuesday",
        interview_date=datetime.now()
    )

    print("\nJob application:", job_app.company_name)
    print("Status:", job_app.status.value)