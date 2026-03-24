from supabase.client import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from app.core.config import settings
import google.generativeai as genai
from typing import Optional

supabase_client=create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)
genai.configure(api_key=settings.GEMINI_API_KEY)

print("--- AVAILABLE EMBEDDING MODELS ---")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Model Name: {m.name}")

embeddings=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.GEMINI_API_KEY,

)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_vector_store():
    return SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents_secure"
    )

async def verify_external_api_key(api_key:str)->Optional[str]:
    try:
        print(f"\n--- AUTH DEBUG ---")
        print(f"Incoming Key: {api_key}")


        response=supabase_client.table("user_api_keys")\
             .select("user_id")\
             .eq("api_key",api_key)\
             .execute()
        
        print(f"Supabase Response: {response.data}")
        print(f"------------------\n")

        if response.data and len(response.data)>0:
            return response.data[0]["user_id"]
        
        return None
    
    except Exception as e:
        print(f"API Key Verification Error:{e}")
        return None