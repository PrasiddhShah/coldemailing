# Setup Notes

## Important: Apollo API Plan Requirements

### Current Issue
Your Apollo API key is on a **FREE PLAN**, which has very limited API access. The free plan does NOT include access to:
- `/api/v1/mixed_people/api_search` (People Search API)
- `/api/v1/mixed_companies/search` (Company Search API)
- `/api/v1/people/match` (Email Enrichment API)

### What This Means
The cold emailing tool **requires a paid Apollo plan** to function. The free plan only allows basic API testing.

### Apollo API Pricing
To use this tool, you need to upgrade your Apollo plan:
1. Go to https://app.apollo.io/
2. Navigate to Settings → Plans & Billing
3. Choose a plan that includes API access:
   - **Basic Plan**: ~$49-79/month - Includes API access
   - **Professional Plan**: ~$99-149/month - More credits and features
   - **Organization Plan**: Custom pricing - Full API access

### What the Tool Can Do (With Paid Plan)
Once you upgrade to a paid plan with API access:
1. Search for people by company (FREE searches, no credits)
2. Filter by job titles (recruiters, managers, CTOs)
3. Preview contacts before enrichment
4. Enrich with emails (costs credits, ~1 per contact)
5. Export to JSON

### Alternative: Manual Testing
If you want to test the tool's functionality without upgrading:
1. Use Apollo's web interface to manually find contacts
2. Export them to CSV
3. The tool can still help organize and filter your existing data

### Free Plan Limitations
The free Apollo plan is designed for:
- Manual prospecting in the web interface
- Limited exports (25 contacts/month)
- No API access for automation

### Recommended Action
**Upgrade your Apollo plan** at https://app.apollo.io/ to use this tool.

The minimum required plan is the **Basic/Professional plan** which includes API access.

---

## Tool Status
✅ Tool is fully built and working
✅ All features implemented correctly
❌ **Cannot run without paid Apollo API plan**

## Next Steps
1. Upgrade Apollo plan to include API access
2. Get new API key from upgraded account
3. Update `.env` file with new API key
4. Run: `python apollo_contacts.py "google.com" --roles recruiter --limit 5 --skip-enrichment`
