# Apollo Cold Emailer - Web Application

A professional web application for finding and contacting professionals at target companies using the Apollo.io API. Features AI-powered email generation and automated sending.

## Features

### Contact Discovery
- **Company Search**: Search by company name, URL, or domain
- **Role Filtering**: Target recruiters, engineering managers, CTOs, CEOs, sales, marketing, or founders
- **Smart Caching**: Automatically saves and merges contacts across searches
- **Credit-Conscious**: Preview contacts before spending credits on email enrichment

### Email Automation
- **AI-Powered Drafts**: Generate personalized emails using Gemini or OpenAI
- **Job Context**: Save job descriptions per company for consistent outreach
- **Resume Attachment**: Automatically attach your resume
- **Email Sending**: Send directly via SMTP (Gmail, Outlook, etc.)

### Web Interface
- **Minimal Design**: Clean, distraction-free interface
- **Contact Management**: View, enrich, and organize contacts in a grid
- **Email Composer**: Full-featured composer with context panel
- **Real-time Updates**: Live search results and notifications

## Architecture

```
┌─────────────────┐
│  React Frontend │  (Port 5173)
│   (Vite + JSX)  │
└────────┬────────┘
         │ HTTP API
         ▼
┌─────────────────┐
│  FastAPI Server │  (Port 8000)
│   (Python)      │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬────────┐
    ▼         ▼         ▼        ▼
┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Apollo │ │Gemini│ │ SMTP │ │ JSON │
│  API   │ │ LLM  │ │Email │ │Cache │
└────────┘ └──────┘ └──────┘ └──────┘
```

## Installation

### Prerequisites

- **Python 3.7+** - Backend server
- **Node.js 16+** - Frontend development
- **Apollo.io API Key** - [Get one here](https://app.apollo.io/#/settings/integrations/api)
- **Gemini API Key** (optional) - For AI email generation: [Get it here](https://aistudio.google.com/app/apikey)
- **SMTP Credentials** (optional) - For sending emails (Gmail, Outlook, etc.)

### 1. Clone and Navigate

```bash
cd "C:\Users\prasi\Documents\Learn\JOB SEARCh"
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd web
npm install
cd ..
```

### 4. Configuration

Create a `.env` file in the project root:

```env
# Required
APOLLO_API_KEY=your_apollo_api_key_here

# AI Email Generation (Optional - defaults to mock mode)
LLM_PROVIDER=gemini  # Options: mock, gemini, openai
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_key_here
LLM_MODEL=gemini-2.5-flash

# Email Sending (Optional - defaults to mock mode)
EMAIL_PROVIDER=smtp  # Options: mock, smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
RESUME_DIR=docs

# Optional Settings
DEFAULT_OUTPUT_DIR=outputs
DEFAULT_PER_PAGE=100
```

**Important Notes:**
- For Gmail SMTP, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
- The LLM_PROVIDER defaults to 'gemini' - set to 'mock' if you don't have an API key
- The EMAIL_PROVIDER defaults to 'mock' - set to 'smtp' to actually send emails

### 5. Add Your Resume (Optional)

Place any PDF resume in the `docs/` folder. The application will automatically find and attach the first PDF it finds. You can change the directory by setting `RESUME_DIR` in `.env`.

## Usage

### Starting the Application

You need to run both the backend server and frontend development server:

**Terminal 1 - Backend:**
```bash
python server.py
# Server starts at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
# Frontend starts at http://localhost:5173
```

Open your browser to **http://localhost:5173**

### Using the Web Interface

1. **Search for Contacts**
   - Enter company name (e.g., "Google", "stripe.com")
   - Select target roles (Recruiter, Eng Manager, CTO, etc.)
   - Set max results
   - Click "Search Contacts"

2. **Review Results**
   - Contacts appear in a grid with name, title, company, location
   - Contacts without emails show "Reveal Email" button
   - Contacts with emails show "Draft Email" button

3. **Reveal Emails** (Costs 1 Apollo Credit)
   - Click "Reveal Email" to enrich a contact
   - Email appears once enriched

4. **Draft & Send Emails**
   - Click "Draft Email" on an enriched contact
   - **Left Panel**: View contact details and add job context
   - **Right Panel**: Edit email subject and body
   - Click "Regenerate Draft" to use AI (requires LLM API key)
   - Click "Send Email" to send via SMTP

### Smart Caching System

The app automatically saves contacts to `outputs/{company_domain}.json`:
- **First search**: Fetches from Apollo and saves
- **Subsequent searches**: Loads cached contacts and merges new ones
- **Credit savings**: Uses cached emails when available, only enriches new contacts

Example: Search for "Google recruiters" → saves to `outputs/google_com.json` → next search for "Google engineers" merges with existing file.

## API Endpoints

The backend provides these REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Check server status |
| `/api/search` | POST | Search for contacts by company/role |
| `/api/enrich` | POST | Enrich contacts with emails (costs credits) |
| `/api/generate-email` | POST | Generate AI email draft |
| `/api/send-email` | POST | Send email via SMTP |

## Project Structure

```
C:\Users\prasi\Documents\Learn\JOB SEARCh\
├── server.py                    # FastAPI backend server
├── config.py                    # Configuration & role mappings
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (DO NOT COMMIT!)
├── README.md                    # This file
├── SETUP_NOTES.md               # Setup instructions
│
├── apollo/                      # Apollo.io integration
│   ├── __init__.py
│   ├── api_client.py           # Apollo API wrapper
│   ├── company_resolver.py     # Company name → domain resolution
│   ├── contact_search.py       # People search with role filtering
│   ├── enrichment.py           # Email enrichment (costs credits)
│   ├── export.py               # JSON export with metadata
│   ├── llm.py                  # AI email generation (Gemini/OpenAI)
│   └── mailer.py               # SMTP email sending
│
├── web/                         # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── App.css             # Minimal styling (unused)
│   │   ├── index.css           # Global styles & theme
│   │   ├── main.jsx            # React entry point
│   │   └── components/
│   │       ├── SearchForm.jsx  # Company/role search form
│   │       ├── ContactGrid.jsx # Contact card display
│   │       └── EmailComposer.jsx # Email drafting modal
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── outputs/                     # Contact export cache (JSON)
├── logs/                        # Server debug logs
├── docs/                        # Documents (resume, etc.)
└── tests/                       # Test scripts
```

## Configuration Details

### Role Mappings

The system supports 6 role types defined in `config.py`:

1. **Recruiter** - Recruiters, Talent Acquisition, HR Business Partners
2. **Engineering Manager** - Engineering Managers, Team Leads, Directors of Engineering
3. **CTO** - CTOs, VPs of Engineering, Heads of Engineering
4. **CEO** - CEOs, Founders, Presidents
5. **Sales** - Account Executives, Sales Directors, BDRs, SDRs
6. **Marketing** - Marketing Managers, CMOs, Growth leads

Each role has 50-100+ title variations and appropriate seniority filters.

### LLM Providers

- **mock**: Returns placeholder text (no API key needed)
- **gemini**: Uses Google Gemini (recommended, cheaper)
- **openai**: Uses OpenAI GPT models

### Email Providers

- **mock**: Logs email to console (testing)
- **smtp**: Sends via SMTP server (Gmail, Outlook, etc.)

## Apollo API Credit Usage

- **Company Resolution**: FREE
- **People Search**: FREE (no credits consumed)
- **Email Enrichment**: ~1 credit per contact
- **Phone Enrichment**: Included with email enrichment

**Best Practice**: Always search first (free) → review contacts → then enrich selectively to save credits.

## Troubleshooting

### Backend Issues

**"Invalid API key"**
- Check `APOLLO_API_KEY` in `.env`
- Verify key at https://app.apollo.io/#/settings/integrations/api

**"LLM generation failed"**
- Verify `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env`
- Set `LLM_PROVIDER=mock` to disable AI features

**"Email send failed"**
- Check SMTP credentials in `.env`
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Set `EMAIL_PROVIDER=mock` to test without sending

### Frontend Issues

**"Failed to connect to server"**
- Ensure backend is running on port 8000: `python server.py`
- Check for CORS errors in browser console

**Page won't load**
- Ensure frontend is running: `cd web && npm run dev`
- Check port 5173 is available

**Search returns no results**
- Try different roles or broader search
- Check company name is correct
- Verify Apollo account has remaining credits

## Security Best Practices

1. **Never commit `.env`** - Contains API keys and passwords
2. **Use App Passwords** - For Gmail/Outlook SMTP
3. **Rotate API Keys** - Periodically regenerate keys
4. **Review .gitignore** - Ensure `.env`, `outputs/`, `logs/` are excluded

## Development

### Running in Production

**Backend:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd web
npm run build
npm run preview
```

### Testing

Test individual components:
```bash
# Test Apollo API connection
python tests/test_api_key.py

# Test people search
python tests/test_people_search.py

# Test account status
python tests/check_account_status.py
```

## API Requirements

This tool requires a **paid Apollo.io plan** with API access:
- **Basic Plan**: ~$49-79/month - Includes API access
- **Professional Plan**: ~$99-149/month - More credits
- **Organization Plan**: Custom pricing - Full API access

The free Apollo plan does NOT include API access.

## License

This tool is for personal use in job searching and professional networking.

## Credits

Built with:
- [Apollo.io API](https://www.apollo.io/) - Contact data
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
- [Vite](https://vite.dev/) - Build tool
- [Google Gemini](https://ai.google.dev/) - AI email generation
- [Python Requests](https://requests.readthedocs.io/) - HTTP library

## Changelog

### Version 2.0.0 (2026-01-06)
- Added React web interface
- Added AI-powered email generation (Gemini/OpenAI)
- Added SMTP email sending
- Added smart contact caching and merging
- Minimal UI redesign
- Multi-role support (6 role types)

### Version 1.0.0 (2026-01-05)
- Initial CLI tool release
- Apollo API integration
- Basic contact search and enrichment
