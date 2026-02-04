from pydantic import BaseModel

class CompanyResponse(BaseModel):
    id: str
    name: str
    website_url: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    angellist_url: str | None = None
    logo_url: str | None = None

class PersonResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    title: str | None = None
    has_email: bool = False
    has_state: bool = False
    has_country: bool = False

class CompaniesAPIResponse(BaseModel):
    organizations: list[CompanyResponse] = []

class PeopleAPIResponse(BaseModel):
    people: list[PersonResponse] = []  