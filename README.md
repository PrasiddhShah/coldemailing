# Apollo Cold Emailing Tool

A professional CLI tool for finding recruiter, engineering manager, and executive contacts at target companies using the Apollo.io API.

## Features

- **Company Search**: Search by company name, URL, or domain
- **Role Filtering**: Target recruiters, engineering managers, CTOs, or all decision-makers
- **Smart Preview**: See contacts before spending credits on email enrichment
- **Credit Saving**: Two-phase workflow (free search → paid enrichment with confirmation)
- **JSON Export**: Export contacts with structured metadata
- **Error Handling**: Robust retry logic and helpful error messages
- **Secure**: API key stored in environment variables, never committed

## Installation

### 1. Prerequisites

- Python 3.7 or higher
- Apollo.io API key ([Get one here](https://app.apollo.io/#/settings/integrations/api))

### 2. Install Dependencies

```bash
cd "C:\Users\prasi\Documents\Learn\JOB SEARCh"
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your Apollo API key
# APOLLO_API_KEY=your_actual_key_here
```

**IMPORTANT**: Never commit your `.env` file to version control!

## Usage

### Basic Usage

```bash
# Find recruiters at Google
python apollo_contacts.py "Google" --roles recruiter

# Find engineering managers at Stripe
python apollo_contacts.py "https://www.stripe.com" --roles engineering_manager

# Find CTOs at Shopify
python apollo_contacts.py "shopify.com" --roles cto
```

### Advanced Usage

```bash
# Search for multiple role types
python apollo_contacts.py "Meta" --roles recruiter engineering_manager cto

# Limit results
python apollo_contacts.py "Apple" --roles recruiter --limit 50

# Specify output file
python apollo_contacts.py "Netflix" --roles cto --output netflix_executives.json

# Skip email enrichment (free search only)
python apollo_contacts.py "Adobe" --roles engineering_manager --skip-enrichment

# Auto-confirm enrichment (no prompt)
python apollo_contacts.py "Tesla" --roles recruiter --auto-confirm
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--roles` | `-r` | Target roles: `recruiter`, `engineering_manager`, `cto`, or `all` |
| `--output` | `-o` | Output JSON filename (default: auto-generated with timestamp) |
| `--output-dir` | | Output directory (default: `outputs/`) |
| `--limit` | `-l` | Maximum number of contacts to find |
| `--skip-enrichment` | | Skip email enrichment (export without emails - free) |
| `--auto-confirm` | `-y` | Skip confirmation prompt for enrichment |
| `--verbose` | `-v` | Verbose output with debug information |

## How It Works

### Workflow

```
1. Company Resolution
   User Input → Company Domain

2. Contact Search (FREE - No Credits)
   Apollo People API → Find contacts by role

3. Preview & Confirmation
   Display contacts → Ask to proceed

4. Email Enrichment (COSTS CREDITS)
   Apollo Enrichment API → Get emails

5. JSON Export
   Save contacts with metadata
```

### API Operations

1. **Company Search** (if needed)
   - Endpoint: `/api/v1/mixed_companies/search`
   - Converts company name → domain

2. **People Search** (FREE)
   - Endpoint: `/api/v1/mixed_people/api_search`
   - Finds people by company domain and job titles
   - **Does NOT consume credits**

3. **Email Enrichment** (COSTS CREDITS)
   - Endpoint: `/api/v1/people/match`
   - Adds email addresses and phone numbers
   - **Consumes 1 credit per contact**

## Output Format

The tool exports contacts to JSON with the following structure:

```json
{
  "metadata": {
    "export_date": "2026-01-05T14:30:45Z",
    "company": "Google Inc",
    "company_domain": "google.com",
    "total_contacts": 45,
    "target_roles": ["recruiter", "engineering_manager"],
    "enriched": true
  },
  "contacts": [
    {
      "name": "John Doe",
      "first_name": "John",
      "last_name": "Doe",
      "title": "Engineering Manager",
      "company": "Google",
      "location": "San Francisco, CA",
      "email": "john.doe@google.com",
      "phone": "+1-555-0100",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "seniority": "manager",
      "departments": ["engineering"],
      "apollo_id": "abc123"
    }
  ]
}
```

## Role Types

The tool supports three predefined role types:

### 1. Recruiter
- Job Titles: Recruiter, Technical Recruiter, HR Manager, Talent Acquisition, etc.
- Seniorities: Manager, Head, Senior

### 2. Engineering Manager
- Job Titles: Engineering Manager, Software Engineering Manager, Team Lead, etc.
- Seniorities: Manager, Head, Director

### 3. CTO
- Job Titles: CTO, Chief Technology Officer, VP Engineering, etc.
- Seniorities: C-Suite, VP, Head

Use `--roles all` to search for all three types at once.

## Examples

### Example 1: Find Recruiters at Google

```bash
python apollo_contacts.py "Google" --roles recruiter
```

**Output:**
```
Resolving company: Google
✓ Found: Google Inc (google.com)

Searching for recruiter contacts...
  Found 45 contacts so far...

+---+----------------------+---------------------------+--------------+
| # | Name                 | Title                     | Location     |
+---+----------------------+---------------------------+--------------+
| 1 | Jane Smith           | Technical Recruiter       | San Francisco|
| 2 | John Doe             | Recruiting Manager        | New York     |
...

EMAIL ENRICHMENT CONFIRMATION
Contacts to enrich: 45
Estimated credit cost: ~45 credits

Proceed with email enrichment? (y/n): y

Enriching emails: |████████████████████████████████████████| 45/45 (100.0%)

✓ Successfully exported 45 contacts to: outputs/google_contacts_2026-01-05_14-30-45.json
  - Contacts with emails: 42/45
```

### Example 2: Preview Without Enrichment

```bash
python apollo_contacts.py "Stripe" --roles engineering_manager --skip-enrichment
```

Searches for contacts but skips email enrichment (no credits used).

### Example 3: Multiple Roles

```bash
python apollo_contacts.py "https://www.shopify.com" --roles recruiter engineering_manager cto --limit 100
```

Finds up to 100 recruiters, engineering managers, and CTOs at Shopify.

## Project Structure

```
C:\Users\prasi\Documents\Learn\JOB SEARCh\
├── apollo_contacts.py          # Main CLI entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── .env                         # API key (DO NOT COMMIT!)
├── .env.example                 # Template for API key
├── README.md                    # This file
├── apollo/                      # Package directory
│   ├── __init__.py
│   ├── api_client.py           # Apollo API wrapper
│   ├── company_resolver.py     # Company name/URL → domain
│   ├── contact_search.py       # People search logic
│   ├── enrichment.py           # Email enrichment
│   ├── export.py               # JSON export
│   └── display.py              # Console formatting
└── outputs/                     # JSON export directory
```

## Error Handling

The tool handles common errors gracefully:

- **Invalid API Key**: Prompts to check `.env` file
- **Company Not Found**: Suggests providing domain directly
- **Zero Results**: Offers suggestions for broader search
- **Rate Limits**: Automatically retries with exponential backoff
- **Insufficient Credits**: Shows current balance and aborts
- **Network Errors**: Retries up to 3 times

## Security Best Practices

1. **Never commit `.env` file** - It contains your API key
2. **Use `.gitignore`** - Ensure `.env` is excluded from version control
3. **Rotate API keys** - Periodically regenerate your Apollo API key
4. **Limit permissions** - Use API keys with minimum required permissions

## Troubleshooting

### Issue: "Invalid API key"
**Solution**: Check that `APOLLO_API_KEY` is set correctly in your `.env` file

### Issue: "No contacts found"
**Solutions**:
- Try different roles: `--roles recruiter engineering_manager cto`
- Remove the `--limit` flag
- Verify the company domain is correct

### Issue: "Rate limit exceeded"
**Solution**: Wait a few minutes before making more requests. The tool will automatically retry.

### Issue: "Insufficient credits"
**Solution**: Check your Apollo account and upgrade your plan if needed

## API Credit Usage

- **People Search**: FREE (no credits consumed)
- **Email Enrichment**: ~1 credit per contact
- **Best Practice**: Always preview contacts before enriching to avoid wasting credits

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest

# Run tests
pytest
```

### Code Structure

- **Modular Design**: Each module has a single responsibility
- **Error Handling**: Custom exceptions for different error types
- **Type Hints**: Full type annotations for better IDE support
- **Documentation**: Comprehensive docstrings

## License

This tool is for personal use in job searching and professional networking.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Apollo API documentation: https://docs.apollo.io/
3. Ensure your API key has the necessary permissions

## Changelog

### Version 1.0.0 (2026-01-05)
- Initial release
- Company search by name, URL, or domain
- Role filtering (recruiter, engineering_manager, cto)
- Two-phase workflow (search → enrich)
- JSON export with metadata
- Comprehensive error handling

## Credits

Built with:
- [Apollo.io API](https://www.apollo.io/) - Contact data provider
- [Python Requests](https://requests.readthedocs.io/) - HTTP library
- [Tabulate](https://github.com/astanin/python-tabulate) - Table formatting
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management
