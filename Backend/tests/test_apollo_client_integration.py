import pytest
from app.clients.apollo_client import ApolloClient


@pytest.fixture(autouse=True)
def reset_singleton():
    ApolloClient._instance = None
    yield
    ApolloClient._instance = None


class TestCompanySearch:
    @pytest.mark.asyncio
    async def test_search_microsoft(self):
        client = ApolloClient()
        try:
            result = await client.post(
                "mixed_companies/search",
                data={
                    "q_organization_name": "microsoft",
                    "page": 1,
                    "per_page": 5,
                },
            )
            print("\n--- Apollo API Response ---")
            print(result)
            assert result is not None
        finally:
            await client.close()
