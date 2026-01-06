# This is the prompt template used by the LLM to generate emails.
# You can edit this file to change the style, tone, or structure of the emails.
#
# AVAILABLE VARIABLES:
# {name}        - Full name of the contact
# {first_name}  - First name of the contact
# {title}       - Job title
# {company}     - Company name
# {location}    - Location (City, State)
# {headline}    - LinkedIn headline (if available)
# {user_context}- The custom context/offer you type in the UI

EMAIL_PROMPT_TEMPLATE = """

Requirements:
1. Return ONLY a valid JSON object with keys: "subject" and "body".
"""
