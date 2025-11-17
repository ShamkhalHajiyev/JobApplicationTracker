# 🤖 AI Job Application Tracker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> AI-powered email analyzer that automatically tracks job applications across multiple email accounts using LLM analysis and Google Sheets integration.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Setup Guide](#-setup-guide)
- [Configuration](#-configuration)
- [Deployment Strategy](#-deployment-strategy)
- [Development Roadmap](#-development-roadmap)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This project automatically monitors multiple email accounts (Gmail, Outlook, iCloud) and uses AI to identify job application-related emails. It categorizes them (new application, interview invite, rejection, etc.) and logs all information to Google Sheets for easy tracking.

**Key Problem Solved:** Manually tracking job applications across multiple email accounts is time-consuming and error-prone. This tool automates the entire process.

### 🎬 How It Works

1. **Scheduled Execution**: Runs 3 times daily (8 AM, 1 PM, 6 PM)
2. **Initial Backfill**: On first run, analyzes last 15 days of emails
3. **Email Fetching**: Connects to all configured email accounts
4. **AI Analysis**: Uses LLM (Claude/GPT/Gemini) to classify emails
5. **Data Storage**: Writes job application data to Google Sheets
6. **Deduplication**: Prevents duplicate entries using email IDs

---

## ✨ Features

### Current Features (In Development)

- ✅ Multi-account email support (Gmail, Outlook, iCloud)
- ✅ Multiple LLM providers (Claude, ChatGPT, Gemini, Ollama)
- ✅ Configurable YAML-based settings
- ✅ Secure credential management
- ✅ Automated scheduling (3x daily)
- ✅ Google Sheets integration
- ✅ Intelligent email categorization:
  - New Application Confirmation
  - Application Updates
  - Interview Invitations
  - Rejection Notifications
  - Job Offers
- ✅ 15-day historical email analysis on first run

### Planned Features (Future)

- [ ] Streamlit web dashboard
- [ ] Real-time email notifications
- [ ] Application status statistics
- [ ] Email sentiment analysis
- [ ] Resume/cover letter attachment detection
- [ ] Salary information extraction
- [ ] Interview date calendar integration
- [ ] Multi-language support
- [ ] Custom email filtering rules
- [ ] Export to CSV/PDF reports

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Environment                    │
│           (AWS Lambda / Railway / Local Docker)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler (APScheduler)                   │
│                  Triggers: 8AM, 1PM, 6PM                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Email Fetcher (Core)                       │
│              Orchestrates multi-account sync                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Gmail Client │      │Outlook Client│      │ IMAP Client  │
│  (OAuth 2.0) │      │   (MSAL)     │      │  (iCloud)    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │  Email Objects  │
                    │  (Pydantic)     │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Analyzer (Core)                       │
│           Classifies & extracts job info                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Claude     │      │   ChatGPT    │      │   Gemini     │
│ (Anthropic)  │      │   (OpenAI)   │      │  (Google)    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                ┌──────────────────────────┐
                │ Job Application Data     │
                │ (Structured JSON)        │
                └──────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   Google Sheets API      │
                │  (Deduplication Check)   │
                └──────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   Job Tracker Sheet      │
                │  (Persistent Storage)    │
                └──────────────────────────┘
```

### Component Breakdown

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Authentication** | OAuth 2.0 token management | `google-auth`, `msal` |
| **Email Providers** | Fetch emails from various sources | Gmail API, Graph API, IMAP |
| **LLM Providers** | AI-powered email classification | Anthropic, OpenAI, Google AI |
| **Storage** | Persistent data storage | Google Sheets API |
| **Scheduler** | Automated execution | APScheduler |
| **Core Logic** | Business logic orchestration | Python |

---

## 📁 Project Structure

```
ai-job-application-tracker/
├── config/
│   ├── config.yaml              # Main config (gitignored)
│   ├── config.yaml.example      # Config template
│   ├── credentials/             # API credentials (gitignored)
│   │   └── sheets_service.json
│   └── tokens/                  # OAuth tokens (gitignored)
│       ├── gmail_personal.json
│       └── outlook_main.json
├── data/
│   └── cache/                   # Temporary data cache
├── docs/                        # Additional documentation
├── logs/                        # Application logs (gitignored)
├── src/
│   └── ai_job_application_tracker/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── auth/                # Authentication modules
│       │   ├── gmail_auth.py
│       │   └── outlook_auth.py
│       ├── core/                # Business logic
│       │   ├── email_fetcher.py
│       │   ├── analyzer.py
│       │   └── scheduler.py
│       ├── providers/           # Email & LLM providers
│       │   ├── email/
│       │   │   ├── base.py
│       │   │   ├── gmail.py
│       │   │   ├── outlook.py
│       │   │   └── imap.py
│       │   └── llm/
│       │       ├── base.py
│       │       ├── anthropic_llm.py
│       │       ├── openai_llm.py
│       │       └── google_llm.py
│       ├── storage/
│       │   └── sheets.py
│       └── utils/
│           ├── config.py
│           ├── logger.py
│           └── models.py
├── tests/                       # Unit tests
├── Dockerfile                   # Container config
├── docker-compose.yml
├── pyproject.toml              # UV dependencies
├── uv.lock
└── README.md
```

---

## 🛠️ Technology Stack

### Core Technologies

- **Language**: Python 3.10+
- **Package Manager**: UV (ultra-fast Python package installer)
- **Config Management**: YAML
- **Data Validation**: Pydantic

### APIs & Services

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| Gmail API | Fetch Gmail emails | OAuth 2.0 |
| Microsoft Graph API | Fetch Outlook emails | MSAL (OAuth 2.0) |
| IMAP | Fetch iCloud emails | App-specific password |
| Anthropic API | Claude LLM analysis | API Key |
| OpenAI API | ChatGPT analysis | API Key |
| Google AI API | Gemini analysis | API Key |
| Google Sheets API | Data storage | Service Account |

### Dependencies

```toml
# Core
pydantic, pyyaml, python-dotenv

# Email
google-auth, google-api-python-client, msal

# Storage
gspread

# Scheduling
APScheduler

# LLM (optional)
anthropic, openai, google-generativeai, ollama
```

---

## 🚀 Setup Guide

### Prerequisites

- Python 3.10 or higher
- UV package manager ([install guide](https://github.com/astral-sh/uv))
- Google Cloud Project (for Gmail & Sheets APIs)
- Azure App Registration (for Outlook)
- API keys for chosen LLM provider(s)

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/ShamkhalHajiyev/JobApplicationTracker.git
cd JobApplicationTracker
```

#### 2. Install Dependencies

```bash
# Install core dependencies
uv sync

# Install LLM providers (choose one or all)
uv sync --extra anthropic-support   # Claude
uv sync --extra openai-support      # ChatGPT
uv sync --extra all-llms            # All providers
```

#### 3. Configure Settings

```bash
# Copy example config
cp config/config.yaml.example config/config.yaml

# Edit with your settings
nano config/config.yaml
```

#### 4. Setup API Credentials

**Gmail API:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `config/credentials/gmail_credentials.json`
5. Run auth script: `uv run python scripts/setup_gmail_oauth.py`

**Outlook API:**
1. Go to [Azure Portal](https://portal.azure.com/)
2. Register app → Add `Mail.Read` permission
3. Copy Application ID, Tenant ID, Client Secret
4. Update `config/config.yaml`

**Google Sheets API:**
1. In Google Cloud Console → Enable Google Sheets API
2. Create Service Account
3. Download JSON key → Save as `config/credentials/sheets_service.json`
4. Create Google Sheet → Share with service account email

**LLM API Keys:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/
- Google AI: https://makersuite.google.com/

#### 5. Run Initial Sync

```bash
# Test configuration
uv run python src/ai_job_application_tracker/main.py --test

# Run first sync (analyzes last 15 days)
uv run python src/ai_job_application_tracker/main.py --initial
```

---

## ⚙️ Configuration

### config.yaml Structure

```yaml
# Email accounts
accounts:
  - name: "Personal Gmail"
    provider: gmail
    email: "your@gmail.com"
    token_file: "config/tokens/gmail_personal.json"
    enabled: true

# LLM settings
llm:
  provider: "anthropic"  # anthropic | openai | google
  anthropic:
    api_key: "sk-ant-..."
    model: "claude-sonnet-4-20250514"

# Google Sheets
google_sheets:
  spreadsheet_id: "your-sheet-id"
  credentials_file: "config/credentials/sheets_service.json"

# Scheduling
settings:
  initial_fetch_days: 15  # First run analyzes last 15 days
  fetch_hours: 24         # Subsequent runs check last 24 hours
  sync_schedule:
    - "08:00"  # 8 AM
    - "13:00"  # 1 PM
    - "18:00"  # 6 PM
```

---

## 🌐 Deployment Strategy

### Option 1: AWS Lambda (Recommended for Production)

**Pros:** Serverless, cost-effective, auto-scaling
**Cost:** ~$0.50/month (based on 3 executions/day)

```bash
# Deploy with AWS SAM or Serverless Framework
# Triggered by EventBridge (CloudWatch Events)
```

**Setup Steps:**
1. Package application with dependencies
2. Create Lambda function
3. Configure EventBridge rules (cron: 0 8,13,18 * * ?)
4. Store secrets in AWS Secrets Manager
5. Set timeout to 5 minutes

### Option 2: Railway.app (Easiest)

**Pros:** Simple deployment, GitHub integration
**Cost:** Free tier available

```bash
# Deploy from GitHub
railway up
```

### Option 3: Docker + Cron (Self-Hosted)

**Pros:** Full control, no vendor lock-in
**Cost:** Server costs only

```dockerfile
# Dockerfile provided
docker build -t job-tracker .
docker run -d job-tracker
```

**Cron Setup:**
```cron
0 8,13,18 * * * docker exec job-tracker python src/ai_job_application_tracker/main.py
```

### Option 4: Google Cloud Run

**Pros:** Serverless, integrates with Google Sheets
**Cost:** ~$1/month

```bash
gcloud run deploy job-tracker --source .
```

---

## 🗺️ Development Roadmap

### Phase 1: Core Functionality ✅ (Weeks 1-2)
- [x] Project setup with UV
- [x] Configuration management
- [x] Pydantic models
- [ ] Gmail client implementation
- [ ] Outlook client implementation
- [ ] IMAP client implementation
- [ ] LLM analyzer (Claude)
- [ ] Google Sheets integration
- [ ] Basic scheduler

### Phase 2: Multi-Provider Support (Weeks 3-4)
- [ ] OpenAI integration
- [ ] Google Gemini integration
- [ ] Ollama (local) support
- [ ] Provider switching logic
- [ ] Error handling & retries
- [ ] Logging system

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] Deduplication logic
- [ ] 15-day historical analysis
- [ ] Email caching
- [ ] Rate limiting
- [ ] Batch processing
- [ ] Unit tests (>80% coverage)

### Phase 4: Deployment (Week 7)
- [ ] Dockerization
- [ ] AWS Lambda setup
- [ ] CI/CD with GitHub Actions
- [ ] Monitoring & alerts
- [ ] Documentation completion

### Phase 5: UI & Analytics (Week 8+)
- [ ] Streamlit dashboard
- [ ] Application statistics
- [ ] Timeline visualization
- [ ] Export functionality
- [ ] Mobile notifications

---

## 📊 Usage

### Manual Execution

```bash
# Run once (last 24 hours)
uv run python src/ai_job_application_tracker/main.py

# Initial run (last 15 days)
uv run python src/ai_job_application_tracker/main.py --initial

# Test configuration
uv run python src/ai_job_application_tracker/main.py --test

# Dry run (no writes)
uv run python src/ai_job_application_tracker/main.py --dry-run
```

### Scheduled Execution

```bash
# Start scheduler (runs 3x daily)
uv run python src/ai_job_application_tracker/main.py --daemon
```

### View Logs

```bash
tail -f logs/job_tracker.log
```

---

## 📈 Expected Output

### Google Sheets Format

| Date | Account | Company | Position | Type | Status | Details | Email ID |
|------|---------|---------|----------|------|--------|---------|----------|
| 2025-11-17 | Gmail | Google | SWE | Interview | Scheduled | Phone screen on 11/20 | msg123 |
| 2025-11-16 | Outlook | Meta | DS | Update | Under review | Moved to 2nd round | msg124 |
| 2025-11-15 | Gmail | Amazon | PM | Rejection | Declined | Position filled | msg125 |

### Email Categories

- **NEW_APPLICATION**: Confirmation of application submission
- **UPDATE**: Status updates (e.g., "under review")
- **INTERVIEW**: Interview invitations
- **REJECTION**: Rejection notices
- **OFFER**: Job offers
- **NOT_JOB_RELATED**: Filtered out

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ai_job_application_tracker

# Run specific test
uv run pytest tests/test_email_clients.py
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
uv sync --extra dev

# Format code
uv run black src/

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Anthropic for Claude API
- OpenAI for GPT API
- Google for Gemini and Workspace APIs
- UV team for amazing Python package manager

---

## 📧 Contact

**Shamkhal Hajiyev**
- GitHub: [@ShamkhalHajiyev](https://github.com/ShamkhalHajiyev)
- Project: [JobApplicationTracker](https://github.com/ShamkhalHajiyev/JobApplicationTracker)

---

## 🎯 Project Status

**Current Version:** 0.1.0 (In Development)

**Next Milestone:** Complete Phase 1 (Core Functionality)

**Last Updated:** November 17, 2025

---

### ⭐ If this project helps you, please give it a star!