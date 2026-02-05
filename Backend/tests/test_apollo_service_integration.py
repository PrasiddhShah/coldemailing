import pytest
from app.clients.apollo_client import ApolloClient
from app.services.apollo_service import ApolloService
from app.models.apollo_model import CompaniesAPIResponse, PeopleAPIResponse, EnrichAPIResponse


@pytest.fixture(autouse=True)
def reset_singleton():
    ApolloClient._instance = None
    yield
    ApolloClient._instance = None


@pytest.fixture
def service():
    client = ApolloClient()
    return ApolloService(client)


class TestApolloServiceChained:
    @pytest.mark.asyncio
    async def test_search_company_microsoft(self, service):
        result = await service.search_company("microsoft", per_page=3)

        print("\n--- Company Search ---")
        for org in result.organizations:
            print(f"  {org.name} | id: {org.id} | web: {org.website_url}")

        assert isinstance(result, CompaniesAPIResponse)
        assert len(result.organizations) > 0

        # store org_id for next step
        pytest.org_id = result.organizations[0].id

    @pytest.mark.asyncio
    async def test_search_people_in_microsoft(self, service):
        org_id = getattr(pytest, "org_id", None)
        assert org_id is not None, "Run test_search_company_microsoft first"

        result = await service.search_people(org_id, per_page=3)

        print("\n--- People Search ---")
        for p in result.people:
            print(f"  {p.first_name} {p.last_name_obfuscated} | title: {p.title} | id: {p.id}")

        assert isinstance(result, PeopleAPIResponse)
        assert len(result.people) > 0

        # store person_id for next step
        pytest.person_id = result.people[0].id

    @pytest.mark.asyncio
    async def test_enrich_person(self, service):
        person_id = getattr(pytest, "person_id", None)
        assert person_id is not None, "Run test_search_people_in_microsoft first"

        result = await service.enrich_people(person_id)

        print("\n--- Enriched Person ---")
        p = result.person
        print(f"  {p.first_name} {p.last_name}")
        print(f"  title: {p.title}")
        print(f"  email: {p.email} ({p.email_status})")
        print(f"  linkedin: {p.linkedin_url}")
        print(f"  location: {p.city}, {p.state}, {p.country}")

        assert isinstance(result, EnrichAPIResponse)
        assert result.person.first_name is not None
