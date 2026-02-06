from pydantic import BaseModel

class CompanyResponse(BaseModel):
    id: str
    name: str
    website_url: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    angellist_url: str | None = None
    logo_url: str | None = None

class PersonResponseRaw(BaseModel):
    id: str
    first_name: str
    last_name_obfuscated: str
    title: str | None = None
    has_email: bool = False
    has_state: bool = False
    has_country: bool = False

class PersonResponseEnriched(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    photo_url: str | None = None
    email_status: str | None = None
    organization_id: str | None = None
    headline: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None

class CompanyCard(BaseModel):
    company_id: str
    company_name: str
    company_logo_url: str | None = None


class CompaniesAPIResponse(BaseModel):
    organizations: list[CompanyResponse] = []

class PeopleAPIResponse(BaseModel):
    total_entries: int = 0
    people: list[PersonResponseRaw] = []  

class EnrichAPIResponse(BaseModel):
    person: PersonResponseEnriched
