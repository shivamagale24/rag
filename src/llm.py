
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Check your project .env file."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    def generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gemini-3.8-flash",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.2
        )

        return response.choices[0].message.content
