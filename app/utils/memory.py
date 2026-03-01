from urllib import response
from supabase import create_client
from app.core.config import settings 

# supabase=create_client(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_chat_history(session_id: str, tenant_id: str, user_id: str, limit: int = 10):
    """
    Retrieves the triple-key secured chat history.
    """
    print(f"--- SECURITY CHECK: Fetching history for {user_id} in {tenant_id} ---")
    try:
        # Use the secure RPC function we created in Supabase
        response = supabase.rpc(
            "get_session_history_secure", 
            {
                "p_session_id": session_id, 
                "p_tenant_id": tenant_id, 
                "p_user_id": user_id
            }
        ).execute()
        
        if not response.data:
            return []
        
        history_data = response.data or []
        print(f"📜 [HISTORY FOUND] {len(history_data)} previous messages retrieved.")
        
        for msg in history_data:
            # Short preview of each message in the terminal
            print(f"   - {msg['role'].upper()}: {msg['content'][:50]}...")

        # Assuming the RPC returns columns: role, content
        # We format them for your RAG prompt
        return response.data

    except Exception as e:
        print(f"DEBUG CRASH in memory.py (get_history): {str(e)}")
        return []

def add_message_to_history(session_id: str, tenant_id: str, user_id: str, role: str, content: str):
    """
    Saves a new message tagged with the specific User ID for SaaS isolation.
    """
    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "tenant_id": tenant_id,
            "user_id": user_id,  # CRITICAL: Identifying the specific uploader
            "role": role,
            "content": content
        }).execute()
        print(f"SUCCESS: Saved {role} message for {user_id}")
    except Exception as e:
        print(f"DEBUG CRASH in memory.py (add_message): {str(e)}")