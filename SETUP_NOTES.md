# Setup Guide - Apollo Cold Emailer

Complete setup instructions for the Apollo Cold Emailer web application.

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
# Navigate to project root
cd path/to/apollo-cold-emailer

# Create virtual environment
python -m venv env

# Activate virtual environment (Windows)
env\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

**Frontend:**
```bash
# Navigate to web directory
cd web

# Install Node packages
npm install

# Return to root
cd ..
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# REQUIRED - Apollo API Key
APOLLO_API_KEY=your_apollo_api_key_here

# OPTIONAL - AI Email Generation
LLM_PROVIDER=mock  # Options: mock, gemini, openai
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gemini-2.5-flash

# OPTIONAL - Email Sending
EMAIL_PROVIDER=mock  # Options: mock, smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
RESUME_DIR=docs

# OPTIONAL - Other Settings
DEFAULT_OUTPUT_DIR=outputs
DEFAULT_PER_PAGE=100
```

### 3. Get API Keys

#### Apollo.io API Key (Required)

1. Go to https://app.apollo.io/
2. Navigate to **Settings → Integrations → API**
3. Copy your API key
4. Paste into `.env` as `APOLLO_API_KEY`

**Important:** You need a **paid Apollo plan** ($49-149/month) for API access. Free plans do NOT include API functionality.

#### Gemini API Key (Optional - for AI email generation)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste into `.env` as `GEMINI_API_KEY`
5. Set `LLM_PROVIDER=gemini`

**Free tier available** - 15 requests/minute, 1500 requests/day

#### OpenAI API Key (Optional - alternative to Gemini)

1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Paste into `.env` as `OPENAI_API_KEY`
4. Set `LLM_PROVIDER=openai`

**Costs money** - Charges per token used

#### Gmail SMTP (Optional - for sending emails)

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password for "Mail"
4. Copy the 16-character password
5. Paste into `.env` as `SMTP_PASSWORD`
6. Set your Gmail address as `SMTP_EMAIL`
7. Set `EMAIL_PROVIDER=smtp`

### 4. Add Your Resume (Optional)

```bash
# Create docs directory
mkdir docs

# Copy any PDF resume to the docs/ folder
# The app will automatically find and use the first PDF
# Example: copy MyResume.pdf docs/
```

The application automatically finds the first PDF file in the `docs/` directory (or whatever directory you set in `RESUME_DIR`). No need to specify the exact filename.

### 5. Run the Application

**Terminal 1 - Backend Server:**
```bash
# From project root
python server.py
```
Server starts at http://localhost:8000

**Terminal 2 - Frontend Dev Server:**
```bash
# From project root
cd web
npm run dev
```
Frontend starts at http://localhost:5173

**Open browser to:** http://localhost:5173

## Configuration Modes

### Mode 1: Minimal Setup (Apollo Only)

Use this for basic contact search and manual email sending:

```env
APOLLO_API_KEY=your_key_here
LLM_PROVIDER=mock
EMAIL_PROVIDER=mock
```

**Features:**
✅ Search for contacts by company/role
✅ Enrich contacts with emails (costs Apollo credits)
✅ Export to JSON
❌ AI email generation (manual editing only)
❌ Automated email sending (copy-paste to email client)

### Mode 2: With AI Email Generation

Add AI-powered email drafts:

```env
APOLLO_API_KEY=your_key_here
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
EMAIL_PROVIDER=mock
```

**Features:**
✅ Everything from Mode 1
✅ AI-generated personalized emails
❌ Automated email sending

### Mode 3: Full Automation

Complete workflow with email sending:

```env
APOLLO_API_KEY=your_key_here
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
EMAIL_PROVIDER=smtp
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RESUME_DIR=docs
```

**Features:**
✅ Everything from Mode 2
✅ Automated email sending via SMTP
✅ Resume attachment

## Troubleshooting

### "ModuleNotFoundError" when running server

**Problem:** Python packages not installed
**Solution:**
```bash
env\Scripts\activate
pip install -r requirements.txt
```

### "npm: command not found"

**Problem:** Node.js not installed
**Solution:** Download and install from https://nodejs.org/

### Backend starts but frontend won't load

**Problem:** Frontend not running or wrong port
**Solution:**
```bash
cd web
npm run dev
# Check that it says "Local: http://localhost:5173"
```

### "APOLLO_API_KEY not found"

**Problem:** Missing or incorrectly named .env file
**Solution:**
- Ensure `.env` is in project root (NOT in web/ folder)
- Check file is named exactly `.env` (not `.env.txt`)
- Verify `APOLLO_API_KEY=` line exists

### "401 Unauthorized" from Apollo API

**Problem:** Invalid API key or free plan
**Solution:**
- Verify key at https://app.apollo.io/#/settings/integrations/api
- Ensure you have a paid Apollo plan ($49+/month)
- Free plans do NOT have API access

### "Failed to generate email"

**Problem:** LLM API key missing or invalid
**Solution:**
- Check `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env`
- Verify key at https://aistudio.google.com/app/apikey
- Or set `LLM_PROVIDER=mock` to disable AI features

### "Failed to send email"

**Problem:** SMTP credentials incorrect
**Solution:**
- For Gmail, use App Password (not regular password)
- Enable 2FA first: https://myaccount.google.com/security
- Create App Password: https://myaccount.google.com/apppasswords
- Or set `EMAIL_PROVIDER=mock` to test without sending

### Port 8000 already in use

**Problem:** Another process using port 8000
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Port 5173 already in use

**Problem:** Another Vite dev server running
**Solution:**
```bash
# Kill other Vite instances
# Or edit web/vite.config.js to use different port
```

## Directory Structure After Setup

```
apollo-cold-emailer/
├── .env                         ← Your configuration
├── env/                         ← Python virtual environment
├── web/node_modules/            ← Node packages
├── outputs/                     ← Contact JSON files (auto-created)
├── logs/                        ← Server logs (auto-created)
└── docs/                        ← Your resume
```

## Testing Your Setup

### 1. Test Backend

```bash
python server.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

Open http://localhost:8000/api/health in browser
- Should return: `{"status":"ok","api_key_configured":true}`

### 2. Test Frontend

```bash
cd web
npm run dev
# Should see: "Local: http://localhost:5173"
```

Open http://localhost:5173 in browser
- Should see the search form

### 3. Test Full Workflow

1. Search for a company (e.g., "Google")
2. Select a role (e.g., "Recruiter")
3. Click "Search Contacts"
4. Results should appear in grid

If all tests pass, setup is complete!

## Common Workflows

### Workflow 1: Research Mode (Free)

Search and export without enrichment:
1. Start backend + frontend
2. Search for company/roles
3. Review contact names and titles (free)
4. Don't click "Reveal Email" (saves credits)
5. Export data saved to `outputs/`

### Workflow 2: Targeted Outreach

Search, enrich selectively, send:
1. Search for 20-50 contacts (free)
2. Review and identify top 5-10 candidates
3. Click "Reveal Email" only on best matches (costs credits)
4. Draft personalized emails
5. Send via SMTP or copy to email client

### Workflow 3: Bulk Outreach

Large-scale campaign:
1. Search for 100+ contacts (free)
2. Click "Reveal Email" on all (costs 100+ credits)
3. Generate AI emails for each
4. Review and customize
5. Send batch emails

## Production Deployment

For running in production (not recommended for beginners):

**Backend:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
cd web
npm run build
npm run preview
```

Consider using:
- **Gunicorn** or **Hypercorn** for backend
- **Nginx** for serving frontend static files
- **Docker** for containerization
- **Systemd** or **PM2** for process management

## API Credit Management

Apollo charges ~1 credit per email enrichment.

**Credit-Saving Tips:**
1. Search first (free) before enriching
2. Use cached contacts from `outputs/` folder
3. Enrich only high-priority targets
4. Review profiles before clicking "Reveal Email"

**Check Credits:**
```bash
python tests/check_account_status.py
```

## Security Checklist

- [ ] `.env` file created and NOT committed to Git
- [ ] `.gitignore` includes `.env`, `outputs/`, `logs/`
- [ ] Using App Password for Gmail (not regular password)
- [ ] API keys rotated every 3-6 months
- [ ] Resume file doesn't contain sensitive data

## Next Steps

Once setup is complete:
1. Read the main README.md for usage instructions
2. Test with a small search (5-10 contacts)
3. Verify email generation works
4. Test email sending in mock mode first
5. Enable SMTP only when ready to send

## Support

For issues:
1. Check this troubleshooting guide
2. Review main README.md
3. Check Apollo API status: https://status.apollo.io/
4. Verify API key permissions at https://app.apollo.io/

## Credits & Costs

**Apollo API:**
- Paid plan required: $49-149/month
- Includes API access + credits
- People search: FREE
- Email enrichment: ~1 credit each

**Gemini API:**
- Free tier: 15 req/min, 1500 req/day
- Paid tier: $0.10-0.30 per 1M tokens

**OpenAI API:**
- Pay per use: $0.50-2.00 per 1M tokens
- More expensive than Gemini

**SMTP (Gmail):**
- Free (500 emails/day limit)

## License

Personal use only for job searching and professional networking.
