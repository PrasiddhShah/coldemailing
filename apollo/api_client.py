import requests
import time
from typing import Dict, List, Optional, Any


class ApolloAPIError(Exception):
    """Base exception for Apollo API errors."""
    pass


class AuthenticationError(ApolloAPIError):
    """Invalid or missing API key (HTTP 401)."""
    pass


class RateLimitError(ApolloAPIError):
    """Rate limit exceeded (HTTP 429)."""

    def __init__(self, message, retry_after_seconds=60):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class NotFoundError(ApolloAPIError):
    """Resource not found (HTTP 404)."""
    pass


class InsufficientCreditsError(ApolloAPIError):
    """Not enough credits for enrichment."""
    pass


class ApolloClient:
    """Low-level HTTP wrapper for Apollo API endpoints."""

    def __init__(self, api_key: str, base_url: str = "https://api.apollo.io"):
        """
        Initialize Apollo API client.

        Args:
            api_key: Apollo API key
            base_url: API base URL (default: https://api.apollo.io)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'x-api-key': api_key
        })

    def search_companies(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for companies by name.

        Args:
            query: Company name to search for
            per_page: Results per page (default: 10)
            page: Page number (default: 1)

        Returns:
            API response dictionary with company data
        """
        endpoint = f"{self.base_url}/api/v1/mixed_companies/search"
        params = {
            'q_organization_name': query,
            'per_page': per_page,
            'page': page
        }

        return self._make_request('POST', endpoint, params=params)

    def search_people(
        self,
        organization_domains: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        person_titles: Optional[List[str]] = None,
        person_seniorities: Optional[List[str]] = None,
        include_similar_titles: bool = True,
        per_page: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for people at companies (FREE - no credits consumed).

        Args:
            organization_domains: List of company domains (e.g., ['google.com'])
            organization_ids: List of Apollo organization IDs (e.g., ['57c4ace7a6da9867ee5599e7'])
            person_titles: List of job titles to search for
            person_seniorities: List of seniority levels
            include_similar_titles: Include similar job titles in search
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            API response dictionary with people data (without emails)
        """
        endpoint = f"{self.base_url}/api/v1/mixed_people/api_search"

        # Build request body as JSON instead of query params
        data = {
            'per_page': min(per_page, 100),
            'page': page,
            'include_similar_titles': include_similar_titles
        }

        if organization_ids:
            data['organization_ids'] = organization_ids
        elif organization_domains:
            data['q_organization_domains'] = organization_domains

        if person_titles:
            data['person_titles'] = person_titles

        if person_seniorities:
            data['person_seniorities'] = person_seniorities

        return self._make_request('POST', endpoint, json_data=data)

    def enrich_person(
        self,
        person_id: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None,
        domain: Optional[str] = None,
        reveal_personal_emails: bool = True,
        reveal_phone_number: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich person data with email and phone (COSTS CREDITS).

        Args:
            person_id: Apollo person ID
            email: Person's email address
            first_name: Person's first name
            last_name: Person's last name
            organization_name: Company name
            domain: Company domain
            reveal_personal_emails: Include personal email addresses
            reveal_phone_number: Include phone numbers

        Returns:
            API response dictionary with enriched data including emails
        """
        endpoint = f"{self.base_url}/api/v1/people/match"

        data = {
            'reveal_personal_emails': reveal_personal_emails,
            'reveal_phone_number': reveal_phone_number
        }

        if person_id:
            data['id'] = person_id
        if email:
            data['email'] = email
        if first_name:
            data['first_name'] = first_name
        if last_name:
            data['last_name'] = last_name
        if organization_name:
            data['organization_name'] = organization_name
        if domain:
            data['domain'] = domain

        return self._make_request('POST', endpoint, json_data=data)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Full endpoint URL
            params: Query parameters
            json_data: JSON body data
            max_retries: Maximum number of retry attempts

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            NotFoundError: Resource not found
            ApolloAPIError: Other API errors
        """
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(endpoint, params=params)
                elif method.upper() == 'POST':
                    if json_data:
                        response = self.session.post(endpoint, json=json_data)
                    else:
                        response = self.session.post(endpoint, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                return self._handle_response(response)

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = e.retry_after_seconds * (2 ** attempt)
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Network error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ApolloAPIError(f"Network error after {max_retries} attempts: {str(e)}")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: requests Response object

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: Invalid API key (401)
            RateLimitError: Rate limit exceeded (429)
            NotFoundError: Resource not found (404)
            InsufficientCreditsError: Not enough credits
            ApolloAPIError: Other API errors
        """
        if response.status_code == 200:
            return response.json()

        elif response.status_code == 401:
            raise AuthenticationError(
                "Invalid API key. Please check your APOLLO_API_KEY in .env file."
            )

        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            raise RateLimitError(
                "API rate limit exceeded. Please wait before making more requests.",
                retry_after_seconds=retry_after
            )

        elif response.status_code == 404:
            raise NotFoundError("Resource not found.")

        elif response.status_code == 402:
            raise InsufficientCreditsError(
                "Insufficient credits for this operation. Please check your Apollo account."
            )

        elif response.status_code == 403:
            try:
                error_data = response.json()
                error_message = error_data.get('error', '')
                if 'not accessible' in error_message and 'free plan' in error_message:
                    raise InsufficientCreditsError(
                        "This API endpoint is not available on the free plan. "
                        "Please upgrade your Apollo plan at https://app.apollo.io/"
                    )
            except InsufficientCreditsError:
                raise
            except:
                pass
            raise ApolloAPIError(f"Access forbidden (HTTP 403). Please check your API key permissions.")

        else:
            try:
                error_data = response.json()
                error_message = error_data.get('message', response.text)
            except:
                error_message = response.text

            raise ApolloAPIError(
                f"Apollo API error (HTTP {response.status_code}): {error_message}"
            )
