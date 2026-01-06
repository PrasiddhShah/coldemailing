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
from apollo.export import export_to_json
from apollo.llm import EmailGenerator
from apollo.mailer import EmailSender

app = FastAPI()

# Helper for title matching
def is_title_match(title: str, roles: List[str], config) -> bool:
    if not roles: return True # "Any" matches everything
    if not title: return False
    
    title_lower = title.lower()
    for role in roles:
        # Check against mapped titles
        if role in config.TITLE_MAPPINGS:
            mappings = config.TITLE_MAPPINGS[role]
            # Check exact titles or seniority keywords?
            # Rough check: does any mapped title appear in the string?
            for t in mappings.get('titles', []):
                if t.lower() in title_lower: return True
        # Also check strict substring of the role itself (e.g. "sales")
        if role.lower() in title_lower: return True
    return False

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
    
    # Initialize Services
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
except Exception as e:
    print(f"Warning: Failed to initialize Services: {e}")
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
class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    attach_resume: Optional[bool] = True

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "api_key_configured": client is not None}

@app.post("/api/search")
def search_api(req: SearchRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")
    
    try:
        with open('server_debug.log', 'a') as f: f.write(f"DEBUG: Starting search for {req.company} with roles {req.roles}\n")
        # Resolve company
        company_info = resolve_company_input(req.company, client)
        with open('server_debug.log', 'a') as f: f.write(f"DEBUG: Resolved company: {company_info}\n")
        safe_company_name = company_info['domain'].lower().replace('.', '_') # Use domain for stability
        
        # Check for existing saved files
        output_dir = 'outputs'
        safe_filename = f"{safe_company_name}.json"
        cached_file_path = os.path.join(output_dir, safe_filename)
        
        if os.path.exists(cached_file_path):
            print(f"Loading cached results from: {cached_file_path}")
            import json
            with open(cached_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cached_contacts = data.get('contacts', [])
                
                # Check if cache satisfies the limit AND role query
                # Filter cached contacts to see how many match the requested roles
                relevant_cached = [c for c in cached_contacts if is_title_match(c.get('title'), req.roles, config)]
                
                if len(relevant_cached) >= req.limit:
                    print(f"Cache has {len(relevant_cached)} relevant contacts (from {len(cached_contacts)} total). Returning cache.")
                    # Return ALL contacts or just relevant? 
                    # User probably wants to see everyone they have saved, but maybe highlight relevant?
                    # For now return relevant to satisfy the "search" intent, but maybe we should return all?
                    # Let's return relevant to be precise, but sidebar might show total.
                    # actually user asked to "merge", so they want to build a db.
                    # But the UI shows the "Search Results".
                    # Let's return the RELEVANT ones for the table display, but existing file keeps all.
                    return {
                        "company": company_info, 
                        "contacts": relevant_cached[:req.limit], 
                        "cached": True,
                        "source_file": cached_file_path
                    }
                else:
                    print(f"Cache has {len(relevant_cached)} relevant (req {req.limit}). Fetching fresh data...")

        # Search contacts
        # We perform a specific search for the MISSING roles
        # Actually simplest to just search for the requested roles as usual
        with open('server_debug.log', 'a') as f: f.write(f"DEBUG: Fetching fresh contacts from Apollo...\n")
        fresh_contacts = search_contacts(
            company_domain=company_info['domain'],
            target_roles=req.roles,
            client=client,
            max_results=req.limit,
            config=config,
            company_info=company_info
        )
        with open('server_debug.log', 'a') as f: f.write(f"DEBUG: Fetched {len(fresh_contacts)} contacts.\n")

        # Backfill company_domain from authoritative source if missing
        for contact in fresh_contacts:
            if not contact.get('company_domain'):
                contact['company_domain'] = company_info['domain']

        # SMART MERGE & ENRICH
        # Goal: Use cached emails if available, enrich only new ones.
        
        # 1. Index cache
        cached_contacts = []
        if os.path.exists(cached_file_path):
             with open(cached_file_path, 'r', encoding='utf-8') as f:
                 cached_contacts = json.load(f).get('contacts', [])
        
        # Map: ID -> Contact (and Name check for fallback)
        cache_map = {}
        for c in cached_contacts:
             if c.get('id'): cache_map[c.get('id')] = c
             cache_map[(c.get('first_name'), c.get('last_name'))] = c
             
        # 2. Prepare list for auto-enrichment
        final_list = []
        to_enrich = []
        
        for fc in fresh_contacts:
             key_id = fc.get('id')
             key_name = (fc.get('first_name'), fc.get('last_name'))
             
             cached_version = cache_map.get(key_id) or cache_map.get(key_name)
             
             if cached_version and cached_version.get('email'):
                 # Use cached version (saves credit)
                 final_list.append(cached_version)
             else:
                 # New or unenriched - needs enrichment
                 # We use the fresh object 'fc'
                 final_list.append(fc)
                 to_enrich.append(fc)
        
        # 3. Enrich the new batch
        # DISABLE AUTO-ENRICHMENT to save credits
        # if to_enrich:
        #     print(f"Auto-enriching {len(to_enrich)} new contacts...")
        #     enriched_sublist = enrich_contacts(to_enrich, client, show_progress=False)
            
        #     # Map back enriched data
        #     enriched_map = {c.get('id') or (c.get('first_name'), c.get('last_name')): c for c in enriched_sublist}
            
        #     for i, c in enumerate(final_list):
        #          k_id = c.get('id')
        #          k_name = (c.get('first_name'), c.get('last_name'))
        #          if k_id in enriched_map:
        #              final_list[i] = enriched_map[k_id]
        #          elif k_name in enriched_map:
        #              final_list[i] = enriched_map[k_name]

        # 4. Global Merge: Add any cached contacts that weren't in this fresh search
        # This is where we ensure we keep the Recruiters when searching for Eng Managers
        fresh_ids = set(c.get('id') for c in final_list if c.get('id'))
        
        # Also track by name if ID missing
        fresh_names = set((c.get('first_name'), c.get('last_name')) for c in final_list)

        for cc in cached_contacts:
             c_id = cc.get('id')
             c_name = (cc.get('first_name'), cc.get('last_name'))
             
             if (c_id and c_id not in fresh_ids) or (not c_id and c_name not in fresh_names):
                 final_list.append(cc)

        # Save search results to disk (Enriched)
        # We enforce a specific filename: outputs/{domain}.json
        output_filename = f"{safe_company_name}.json"
        
        # Pass enriched=True since we are saving the master DB
        output_path = export_to_json(
            contacts=final_list,
            output_dir='outputs',
            output_path=os.path.join('outputs', output_filename),
            company_name=company_info['name'],
            company_domain=company_info['domain'],
            target_roles=req.roles,
            enriched=True
        )
        print(f"Saved enriched search results to: {output_path}")
        
        # Return ALL merged contacts so user sees their full DB growing?
        # Or just the ones matching the current filter?
        # User said "update the list", usually implying they want to see the result of their new work.
        # But if they want to email them, they might want to see only the new ones?
        # Let's filter the return to be "Relevant + Any Previously Viewed"? 
        # Actually, for "Project" view, seeing all is good. 
        # But for "Search", usually you expect to see what you searched for.
        # Compromise: Return relevant ones for the specific role at top, or just filter matching logic again.
        
        # Re-filter final list for return
        return_contacts = [c for c in final_list if is_title_match(c.get('title'), req.roles, config)]
        if len(return_contacts) < req.limit:
             # Fallback to showing more if we didn't find enough matches, just to show *something*
             return_contacts = final_list
        
        return {
            "company": company_info, 
            "contacts": return_contacts[:max(len(return_contacts), req.limit)], 
            "saved_to": output_path,
            "total_count": len(final_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enrich")
def enrich_api(req: EnrichRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Apollo API Client not initialized")
    
    try:
        enriched_contacts = enrich_contacts(req.contacts, client, show_progress=False)
        
        # Determine company info from first contact
        company_name = enriched_contacts[0].get('company', 'Unknown')
        company_domain = enriched_contacts[0].get('company_domain') or 'unknown_domain'
        safe_company_name = company_domain.lower().replace('.', '_')

        # Load existing cache to merge with
        output_dir = 'outputs'
        safe_filename = f"{safe_company_name}.json"
        cached_file_path = os.path.join(output_dir, safe_filename)
        
        all_contacts = enriched_contacts # Fallback if no cache
        
        if os.path.exists(cached_file_path):
            try:
                import json
                with open(cached_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_contacts = data.get('contacts', [])
                    
                    # Merge logic: Update existing contacts with enriched ones
                    # We use a Map keyed by name+title or ID for easier lookup
                    enriched_map = {c.get('id') or (c.get('first_name'), c.get('last_name')): c for c in enriched_contacts}
                    
                    updated_list = []
                    for c in existing_contacts:
                        key = c.get('apollo_id') or (c.get('first_name'), c.get('last_name'))
                        if key in enriched_map:
                            # Replace with enriched version
                            updated_list.append(enriched_map[key])
                            # Remove from map so we know what's left
                            del enriched_map[key]
                        else:
                            updated_list.append(c)
                    
                    # Add any new ones that weren't in the list
                    updated_list.extend(enriched_map.values())
                    all_contacts = updated_list
            except Exception as cache_err:
                print(f"Warning: Failed to merge with cache: {cache_err}")

        # Save merged list to disk
        output_path = export_to_json(
            contacts=all_contacts,
            output_dir='outputs',
            output_path=cached_file_path,
            company_name=company_name,
            enriched=True
        )
        print(f"Saved (merged) enriched contacts to: {output_path}")

        return {"contacts": enriched_contacts, "saved_to": output_path, "total_saved": len(all_contacts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-email")
def generate_email_api(req: EmailDraftRequest):
    try:
        # Pass the prompt (user_context) + contact info to the service
        draft = llm_service.generate_draft(req.contact, req.user_context, req.job_link)
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-email")
@app.post("/api/send-email")
def send_email_api(req: SendEmailRequest):
    try:
        attachment_path = None
        if req.attach_resume:
             attachment_path = config.RESUME_PATH
             if not os.path.exists(attachment_path):
                 print(f"Warning: Resume not found at {attachment_path}")

        success = email_service.send_email(req.to_email, req.subject, req.body, attachment_path)
        if success:
            return {"status": "sent", "mock": (email_service.provider == "mock")}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
