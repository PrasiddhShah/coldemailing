from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import os

from config import load_config
from apollo.api_client import ApolloClient
from apollo.company_resolver import resolve_company_input
from apollo.contact_search import search_contacts
from apollo.enrichment import enrich_contacts

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Apollo Client
try:
    config = load_config()
    client = ApolloClient(config.APOLLO_API_KEY, config.API_BASE_URL)
except Exception as e:
    print(f"Warning: Failed to initialize Apollo Client: {e}")
    client = None

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

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "api_key_configured": client is not None}

@app.post("/api/search")
def search_api(req: SearchRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")
    
    try:
        # Resolve company
        company_info = resolve_company_input(req.company, client)
        
        # Search contacts
        contacts = search_contacts(
            company_domain=company_info['domain'],
            target_roles=req.roles,
            client=client,
            max_results=req.limit,
            config=config,
            company_info=company_info
        )
        return {"company": company_info, "contacts": contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enrich")
def enrich_api(req: EnrichRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")
    
    try:
        # Note: enrich_contacts expects a list of dicts. 
        # We might need to adjust show_progress=False to avoid stdout noise
        enriched_contacts = enrich_contacts(req.contacts, client, show_progress=False)
        return {"contacts": enriched_contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-email")
def generate_email_api(req: EmailDraftRequest):
    # Mock LLM generation for now
    name = req.contact.get('first_name') or "there"
    title = req.contact.get('title') or "Role"
    company = req.contact.get('company') or "Company"
    
    subject = f"Question about {company}"
    body = f"""Hi {name},

I noticed you are working as a {title} at {company}.

I'd love to connect and discuss...

Best,
[Your Name]"""
    
    return {"subject": subject, "body": body}

@app.post("/api/send-email")
def send_email_api(req: SendEmailRequest):
    # Mock Email Sending for now
    print("="*50)
    print(f"MOCK SEND EMAIL to: {req.to_email}")
    print(f"Subject: {req.subject}")
    print(f"Body: {req.body}")
    print("="*50)
    
    return {"status": "sent", "mock": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
