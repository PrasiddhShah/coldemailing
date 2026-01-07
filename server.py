"""
FastAPI server with PostgreSQL database support.
This replaces JSON file storage with database operations.
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from config import load_config, find_resume_path
from database import (
    get_db, init_db, test_connection,
    upsert_company, upsert_contact, create_search, get_company_by_domain,
    get_contacts_by_company, create_email_history, export_contacts_to_dict
)
from apollo.api_client import ApolloClient
from apollo.company_resolver import resolve_company_input
from apollo.contact_search import search_contacts
from apollo.enrichment import enrich_contacts
from apollo.llm import EmailGenerator
from apollo.mailer import EmailSender

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    config = load_config()
    client = ApolloClient(config.APOLLO_API_KEY, config.API_BASE_URL)

    llm_api_key = config.GEMINI_API_KEY if config.LLM_PROVIDER == 'gemini' else config.OPENAI_API_KEY
    llm_service = EmailGenerator(
        provider=config.LLM_PROVIDER,
        api_key=llm_api_key,
        model=config.LLM_MODEL
    )

    email_service = EmailSender(
        provider=config.EMAIL_PROVIDER,
        smtp_config={
            'server': config.SMTP_SERVER,
            'port': config.SMTP_PORT,
            'email': config.SMTP_EMAIL,
            'password': config.SMTP_PASSWORD
        }
    )

    # Test database connection on startup
    if not test_connection():
        print("WARNING: Database connection failed! Check DATABASE_URL in .env")
except Exception as e:
    print(f"Warning: Failed to initialize services: {e}")
    client = None
    llm_service = EmailGenerator(provider="mock")
    email_service = EmailSender(provider="mock")


# --- Data Models ---

class SearchRequest(BaseModel):
    company: str
    roles: List[str]
    limit: Optional[int] = 10


class EnrichRequest(BaseModel):
    contacts: List[Dict[str, Any]]


class EmailDraftRequest(BaseModel):
    contact: Dict[str, Any]
    user_context: Optional[str] = ""
    job_link: Optional[str] = ""


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    attach_resume: Optional[bool] = True


# --- Startup Event ---

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")


# --- Endpoints ---

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except:
        db_status = "disconnected"

    return {
        "status": "ok",
        "api_key_configured": client is not None,
        "database": db_status
    }


@app.post("/api/search")
def search_api(req: SearchRequest, db: Session = Depends(get_db)):
    """
    Search for contacts at a company.
    Stores results in database.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")

    try:
        # Resolve company
        company_info = resolve_company_input(req.company, client)

        # Upsert company to database
        company = upsert_company(db, {
            'domain': company_info['domain'],
            'name': company_info['name'],
            'organization_id': company_info.get('organization_id')
        })

        # Check if we have existing contacts in database
        existing_contacts = get_contacts_by_company(db, company.id)
        existing_count = len(existing_contacts)

        print(f"Found {existing_count} existing contacts in database for {company.name}")

        # Fetch fresh contacts from Apollo
        fresh_contacts = search_contacts(
            company_domain=company_info['domain'],
            target_roles=req.roles,
            client=client,
            max_results=req.limit,
            config=config,
            company_info=company_info
        )

        # Upsert contacts to database (smart merge)
        for contact_data in fresh_contacts:
            # Ensure company_domain is set
            if not contact_data.get('company_domain'):
                contact_data['company_domain'] = company_info['domain']

            upsert_contact(db, contact_data, company.id)

        # Record this search
        create_search(
            db,
            company_id=company.id,
            roles=req.roles,
            limit=req.limit,
            total_found=len(fresh_contacts)
        )

        # Get all contacts for this company from database
        all_contacts = get_contacts_by_company(db, company.id)

        # Convert to dictionaries for JSON response
        contacts_dict = export_contacts_to_dict(all_contacts)

        return {
            "company": {
                "name": company.name,
                "domain": company.domain
            },
            "contacts": contacts_dict,
            "total_count": len(all_contacts),
            "new_contacts": len(fresh_contacts),
            "cached": existing_count > 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enrich")
def enrich_api(req: EnrichRequest, db: Session = Depends(get_db)):
    """
    Enrich contacts with emails.
    Updates database with enriched data.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")

    try:
        # Enrich via Apollo API
        enriched_contacts = enrich_contacts(req.contacts, client, show_progress=False)

        # Update database with enriched data
        updated_contacts = []
        for contact_data in enriched_contacts:
            # Find company
            company_domain = contact_data.get('company_domain')
            if not company_domain:
                continue

            company = get_company_by_domain(db, company_domain)
            if not company:
                # Create company if doesn't exist
                company = upsert_company(db, {
                    'domain': company_domain,
                    'name': contact_data.get('company', 'Unknown')
                })

            # Upsert enriched contact
            contact = upsert_contact(db, contact_data, company.id)
            updated_contacts.append(contact)

        # Convert to dictionaries
        contacts_dict = export_contacts_to_dict(updated_contacts)

        return {
            "contacts": contacts_dict,
            "total_enriched": len(updated_contacts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-email")
def generate_email_api(req: EmailDraftRequest):
    """Generate AI email draft."""
    try:
        draft = llm_service.generate_draft(req.contact, req.user_context, req.job_link)
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send-email")
def send_email_api(req: SendEmailRequest, db: Session = Depends(get_db)):
    """
    Send email and record in database.
    """
    try:
        # Find resume if needed
        attachment_path = None
        if req.attach_resume:
            attachment_path = find_resume_path(config.RESUME_DIR)
            if attachment_path:
                print(f"Using resume: {attachment_path}")
            else:
                print(f"Warning: No PDF resume found in {config.RESUME_DIR}/")

        # Send email
        success = email_service.send_email(req.to_email, req.subject, req.body, attachment_path)

        # Record in database
        # Note: We need contact_id, but we may not have it from the frontend
        # For now, we'll create email history without contact_id
        # TODO: Update frontend to send contact_id

        if success:
            return {
                "status": "sent",
                "mock": (email_service.provider == "mock")
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
