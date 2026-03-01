from fastapi import APIRouter, HTTPException,Query
from app.services.supabase_service import supabase_client

router=APIRouter()



@router.get("/list")
@router.get("/api/docs/list")
async def list_user_documents(tenant_id: str, user_id: str):
    # 1. Fetch metadata from ALL chunks for this user/tenant
    # We set a high limit (e.g., 10,000) to ensure we see all chunks
    response = supabase_client.from_("documents") \
        .select("metadata") \
        .eq("metadata->>tenant_id", tenant_id) \
        .eq("metadata->>user_id", user_id) \
        .limit(10000) \
        .execute()

    if not response.data:
        return {"documents": []}

    # 2. Use a dictionary to keep only the UNIQUE source names
    # This also lets us store the latest date for each file
    unique_docs = {}
    
    for item in response.data:
        meta = item.get('metadata', {})
        name = meta.get('source_name')
        date = meta.get('upload_date', 'Recent')
        
        if name and name not in unique_docs:
            unique_docs[name] = {
                "name": name,
                "date": date
            }

    # Convert the dictionary back to a list for the frontend
    return {"documents": list(unique_docs.values())}    

@router.delete("/delete")
async def delete_user_document(filename: str, tenant_id: str, user_id: str):
    # Match the 'source_name' key used in your metadata
    response = supabase_client.from_("documents") \
        .delete() \
        .eq("metadata->>source_name", filename) \
        .eq("metadata->>tenant_id", tenant_id) \
        .eq("metadata->>user_id", user_id) \
        .execute()
        
    return {"status": "success", "message": f"Removed {filename} from memory."}