import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "tu_api_key_aqui")