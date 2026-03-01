from fastapi import APIRouter, HTTPException,Query
from app.services.supabase_service import supabase_client

router=APIRouter()

@router.get("/list")
async def list_user_sessions(tenant_id:str, user_id:str):
    response=supabase_client.from_("chat_history")\
        .select("session_id,content,created_at")\
        .eq("tenant_id",tenant_id)\
        .eq("user_id",user_id)\
        .eq("role","user")\
        .order("created_at",desc=True)\
        .execute()
    
    seen=set()
    unique_sessions=[]
    for row in response.data:
        if row['session_id'] not in seen:
            seen.add(row['session_id'])
            unique_sessions.append({
                "id": row['session_id'],
                "title": row['content'][:30] + "...",
                "date": row['created_at'].split("T")[0]
            })
    return {"sessions": unique_sessions}


@router.get("/{session_id}")
async def get_session_history(session_id: str, tenant_id: str, user_id: str):
    response = supabase_client.from_("chat_history") \
        .select("role, content") \
        .eq("session_id", session_id) \
        .eq("tenant_id", tenant_id) \
        .eq("user_id", user_id) \
        .order("created_at", desc=False) \
        .execute()
    
    # Ensure we ALWAYS return a dictionary with a 'messages' key
    return {"messages": response.data if response.data else []}