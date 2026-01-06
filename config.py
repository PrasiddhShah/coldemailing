import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for Apollo API tool."""

    APOLLO_API_KEY = os.getenv('APOLLO_API_KEY', '')
    API_BASE_URL = "https://api.apollo.io"
    DEFAULT_PER_PAGE = int(os.getenv('DEFAULT_PER_PAGE', '100'))
    DEFAULT_PER_PAGE = int(os.getenv('DEFAULT_PER_PAGE', '100'))
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', 'outputs')

    # AI Config
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini') # mock, openai, gemini
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')

    # Email Config
    EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'mock') # mock, smtp
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    RESUME_PATH = os.getenv('RESUME_PATH', 'docs/Prasiddh_Shah_resume.pdf')




    TITLE_MAPPINGS = {
        'recruiter': {
            'titles': [
                'Recruiter',
                'Technical Recruiter',
                'HR Manager',
                'Talent Acquisition',
                'Talent Acquisition Manager',
                'Recruiting Manager',
                'Head of Recruiting',
                'Hiring Manager'
            ],
            'seniorities': ['manager', 'head', 'senior']
        },
        'engineering_manager': {
            'titles': [
                'Engineering Manager',
                'Software Engineering Manager',
                'Team Lead',
                'Engineering Lead',
                'Development Manager',
                'Tech Lead'
            ],
            'seniorities': ['manager', 'head', 'director']
        },
        'cto': {
            'titles': [
                'CTO',
                'Chief Technology Officer',
                'VP Engineering',
                'VP of Engineering',
                'Vice President of Engineering',
                'Head of Engineering',
                'Chief Technical Officer'
            ],
            'seniorities': ['c_suite', 'vp', 'head']
        },
        'ceo': {
            'titles': ['CEO', 'Chief Executive Officer', 'Founder', 'Co-Founder'],
            'seniorities': ['c_suite', 'founder']
        },
        'founder': {
             'titles': ['Founder', 'Co-Founder', 'Owner'],
             'seniorities': ['founder', 'c_suite']
        },
        'sales': {
            'titles': ['Sales Manager', 'Account Executive', 'VP of Sales', 'Head of Sales', 'Business Development'],
            'seniorities': ['manager', 'head', 'vp', 'director']
        },
        'marketing': {
            'titles': ['Marketing Manager', 'CMO', 'VP of Marketing', 'Head of Marketing', 'Product Marketing Manager'],
            'seniorities': ['manager', 'head', 'vp', 'c_suite']
        }
    }


def load_config():
    """Load and return configuration."""
    return Config()


def validate_api_key(api_key):
    """Validate that API key is present and not empty."""
    if not api_key or api_key == 'your_apollo_api_key_here':
        raise ValueError(
            "Apollo API key not found or invalid. "
            "Please set APOLLO_API_KEY in your .env file. "
            "You can create one by copying .env.example to .env and adding your API key."
        )
    return True


def mask_api_key(api_key):
    """Mask API key for logging (show only last 4 characters)."""
    if len(api_key) <= 4:
        return "****"
    return "*" * (len(api_key) - 4) + api_key[-4:]
