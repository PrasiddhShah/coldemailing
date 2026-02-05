import pytest
from unittest.mock import patch, AsyncMock
from app.clients.apollo_client import ApolloClient


@pytest.fixture(autouse=True)
def reset_singleton():
    ApolloClient._instance = None
    yield
    ApolloClient._instance = None


@pytest.fixture
def env_vars():
    with patch.dict(
        "os.environ",
        {
            "APOLLO_BASE_URL": "https://api.apollo.test",
            "APOLLO_API": "test-api-key-123",
        },
    ):
        yield


class TestSingleton:
    def test_same_instance_returned(self, env_vars):
        a = ApolloClient()
        b = ApolloClient()
        assert a is b

    def test_same_id(self, env_vars):
        a = ApolloClient()
        b = ApolloClient()
        assert id(a) == id(b)

    def test_initialize_called_once(self, env_vars):
        with patch.object(ApolloClient, "_initialize") as mock_init:
            ApolloClient._instance = None
            ApolloClient()
            ApolloClient()
            mock_init.assert_called_once()

    def test_instance_stored_on_class(self, env_vars):
        obj = ApolloClient()
        assert ApolloClient._instance is obj

    def test_new_instance_after_reset(self, env_vars):
        first = ApolloClient()
        ApolloClient._instance = None
        second = ApolloClient()
        assert first is not second

    @pytest.mark.asyncio
    async def test_close_clears_singleton(self, env_vars):
        obj = ApolloClient()
        with patch.object(obj.client, "aclose", new=AsyncMock()):
            await obj.close()
        assert ApolloClient._instance is None

    @pytest.mark.asyncio
    async def test_new_instance_after_close(self, env_vars):
        first = ApolloClient()
        with patch.object(first.client, "aclose", new=AsyncMock()):
            await first.close()
        second = ApolloClient()
        assert first is not second
