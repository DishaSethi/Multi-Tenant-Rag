from supabase import create_client
import os
from app.core.config import settings 

# supabase=create_client(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# def get_chat_history(session_id: str, tenant_id: str, limit: int = 5):
#     try:
#         # We use the direct .select() and then provide filters in a single chain
#         # before the final .execute(). This is the most stable pattern.

#         filters={
#             "session_id":session_id,
#             "tenant_id":tenant_id
#         }
#         response = (
#             supabase.table("chat_history")
#             .select("message")
#             .match({
#                 "session_id": session_id, 
#                 "tenant_id": tenant_id
#             })
#             .order("created_at", desc=True)
#             .limit(limit)
#             .execute()
#         )
        
#         history = [row['message'] for row in response.data][::-1]
#         return history
#     except Exception as e:
#         # Detailed logging to see exactly where it fails
#         print(f"Database Query Error: {e}")
#         return []

def get_chat_history(session_id: str, tenant_id: str, limit: int = 5):
    print(f"--- DEBUG: Fetching history for {session_id} ---")
    try:
        # Step 1: Check if supabase client is alive
        if not supabase:
            print("DEBUG ERROR: Supabase client is None!")
            return []

        # Step 2: Call RPC
        print(f"DEBUG: Calling RPC with session: {session_id}, tenant: {tenant_id}")
        response = supabase.rpc(
            "get_session_history", 
            {"p_session_id": session_id, "p_tenant_id": tenant_id, "p_limit": limit}
        ).execute()
        
        # Step 3: Check raw response
        print(f"DEBUG: Raw DB Response Data: {response.data}")
        
        if not response.data:
            print("DEBUG: No history found in DB.")
            return []

        history = [row['message'] for row in response.data][::-1]
        print(f"DEBUG: Formatted History for LangChain: {history}")
        return history

    except Exception as e:
        print(f"DEBUG CRASH in memory.py: {str(e)}")
        return []

def add_message_to_history(session_id:str,tenant_id:str, role:str,content:str):
    """Saves a new message to the database."""

    message={"role":role,"content":content}
    supabase.table("chat_history").insert({
        "session_id":session_id,
        "tenant_id":tenant_id,
        "message":message
    }).execute()
    