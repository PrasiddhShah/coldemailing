import httpx
import os
from dotenv import load_dotenv, find_dotenv
from typing import Any

class ApolloClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv(find_dotenv(), override=False)
        self.client = httpx.AsyncClient(
            base_url=os.getenv("APOLLO_BASE_URL"),
            headers={"x-api-key": os.getenv("APOLLO_API")},
            timeout=30.0
        )

    async def get(self, endpoint: str, params: dict = None) -> dict[str, Any]:
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: dict = None) -> dict[str, Any]:
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
        ApolloClient._instance = None