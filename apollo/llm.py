import os
from typing import Dict, Any, Optional
import json

class EmailGenerator:
    def __init__(self, provider: str = "mock", api_key: Optional[str] = None, model: str = "gpt-4"):
        self.provider = provider
        self.api_key = api_key
        self.model = model

    def generate_draft(self, contact: Dict[str, Any], user_context: str = "", job_link: str = "") -> Dict[str, str]:
        """
        Generate an email draft based on contact info.
        """
        if self.provider == "mock":
            return self._generate_mock(contact, user_context)
        elif self.provider == "openai":
            return self._generate_openai(contact, user_context, job_link)
        elif self.provider == "gemini":
            return self._generate_gemini(contact, user_context, job_link)
        else:
            print(f"Warning: Unknown provider {self.provider}, falling back to mock.")
            return self._generate_mock(contact, user_context)

    def _generate_mock(self, contact: Dict[str, Any], user_context: str) -> Dict[str, str]:
        first_name = contact.get('first_name') or "there"
        company = contact.get('company') or "your company"
        title = contact.get('title') or "Role"
        
        subject = f"Quick question for {first_name} about {company}"
        body = f"""Hi {first_name},

I noticed you're leading the team as {title} at {company}.

I'm working on a project that might help with your hiring process.
{user_context or "[User Context would go here]"}

Would you be open to a quick chat?

Best,
[Your Name]"""
        return {"subject": subject, "body": body}

    def _generate_openai(self, contact: Dict[str, Any], user_context: str, job_link: str = "") -> Dict[str, str]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            prompt = self._build_prompt(contact, user_context, job_link)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful SDR assistant generating cold emails. Return JSON with 'subject' and 'body'."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return self._generate_mock(contact, user_context + f"\n(Fallback due to error: {str(e)})")

    def _generate_gemini(self, contact: Dict[str, Any], user_context: str, job_link: str = "") -> Dict[str, str]:
        try:
            from google import genai

            # Initialize client with API key
            client = genai.Client(api_key=self.api_key)

            # Map robust model names if needed, or rely on pass-through
            model_name = self.model or "gemini-2.5-flash"
            if "gpt" in model_name: model_name = "gemini-2.5-flash" # Fallback if user switched provider but kept model name

            prompt = self._build_prompt(contact, user_context, job_link)

            # Use new client.models.generate_content API
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return self._generate_mock(contact, user_context + f"\n(Fallback due to error: {str(e)})")

    def _build_prompt(self, contact: Dict[str, Any], user_context: str, job_link: str = "") -> str:
        # Import here to allow "hot reloading" if the user changes the file without restart
        import sys
        if 'scripts.prompt' in sys.modules:
            import importlib
            import scripts.prompt
            importlib.reload(scripts.prompt)
            from scripts.prompt import EMAIL_PROMPT_TEMPLATE
        else:
            from scripts.prompt import EMAIL_PROMPT_TEMPLATE

        # Prepare data for safe formatting
        data = {
            'name': contact.get('name', ''),
            'first_name': contact.get('first_name', ''),
            'title': contact.get('title', ''),
            'company': contact.get('company', ''),
            'location': contact.get('location', ''),
            'headline': contact.get('headline', ''),
            'job_description': user_context or "",
            'job_link': job_link or "[Job Link]"
        }

        try:
            return EMAIL_PROMPT_TEMPLATE.format(**data)
        except KeyError as e:
            raise ValueError(f"Error in scripts/prompt.py: Missing variable {e}. Please check your template.")
