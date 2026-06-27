import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
cliente = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def embeber(textos: list[str], tipo='RETRIEVAL_DOCUMENT') -> list[list[float]]:
    resp = cliente.models.embed_content(
        model='gemini-embedding-001',
        contents=textos,
        config=types.EmbedContentConfig(task_type=tipo),
    )
    return [e.values for e in resp.embeddings]