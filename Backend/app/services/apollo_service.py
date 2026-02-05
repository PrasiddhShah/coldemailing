
from app.clients.apollo_client import ApolloClient
from app.models.apollo_model import (
     CompaniesAPIResponse,
     PeopleAPIResponse,
     EnrichAPIResponse
)

class ApolloService():
    def __init__(self, client: ApolloClient):
            self.client = client

    async def search_company(self,company_name: str, page: int = 1, per_page: int = 10) -> CompaniesAPIResponse:
        data = await self.client.post("mixed_companies/search", data={
            "q_organization_name": company_name,
            "page": page,
            "per_page": per_page
        })
        return CompaniesAPIResponse(**data)
    
    async def search_people(self, org_id: str, page: int = 1, per_page: int = 10) -> PeopleAPIResponse:
        data = await self.client.post("mixed_people/api_search", data={
            "organization_ids[]": [org_id],  
            "page": page,
            "per_page": per_page
        })
        return PeopleAPIResponse(**data)
    
    async def enrich_people(self, person_id: str) -> EnrichAPIResponse:
        data = await self.client.post("people/match", data={
            "id": person_id,
            "reveal_personal_emails": True
        })
        return EnrichAPIResponse(**data)