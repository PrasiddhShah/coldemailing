from fastapi import APIRouter,HTTPException
from app.clients.apollo_client import ApolloClient
from typing import List
from app.models.apollo_model import CompaniesAPIResponse, PeopleAPIResponse, EnrichAPIResponse,CompanyCard

from app.services.apollo_service import ApolloService

apollo = APIRouter()
apollo_service = ApolloService(ApolloClient())

@apollo.get("/company/", response_model=CompaniesAPIResponse)
async def get_companies(company_name: str, db: bool = False):
    if len(company_name) ==0:
        raise HTTPException("No Company Passed for Company Search")
    if not db:
        companies = await apollo_service.search_company(company_name)
    else:
        pass
    return companies

@apollo.get("/people", response_model=PeopleAPIResponse)
async def get_people(company_id:str, db:bool = False):
    if len(company_id) == 0:
        raise HTTPException("No Company Passed for People Search")
    if not db:
        people = await apollo_service.search_people(company_id)
    else:
        pass
    return people

@apollo.get("/all_companies", response_model=List[CompanyCard])
async def get_all_companies():
    return 

@apollo.get("/enrich_people", response_model=EnrichAPIResponse)
async def get_people_info(id: str):
    if len(id) == 0:
        raise HTTPException("No Peoson ID Passed for Enrichment")