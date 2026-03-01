# from http.client import HTTPException
from fastapi import APIRouter,UploadFile, File,Form,HTTPException
from app.utils.document_loaders import process_input
from app.services.supabase_service import get_vector_store, embeddings, supabase_client
from app.services.rag_service import run_rag_chain
from typing import Optional
from fastapi import APIRouter, Query
from app.services.supabase_service import supabase_client

router=APIRouter()


# @router.post("/ingest")
# async def ingest(tenant_id:str=Form(...),
#                  source_type:str=Form(...),
#                  user_id: str = Form(...),
#                  link:str=Form(None),
#                  file:Optional[UploadFile]=File(None)
#                  ):
#     try:
#         if source_type=="pdf" and not file:
#             raise HTTPException(status_code=400, detail="PDF file is required for source_type 'pdf'")
#         if source_type=="link" and not link:
#             raise HTTPException(status_code=400, detail="Link is required for source_type 'link'")
        
#         chunks=process_input(source_type,tenant_id,link,file)
#         for chunk in chunks:
#             chunk.metadata = {"tenant_id": tenant_id}
        
#         get_vector_store().from_documents(
#             chunks,embeddings, client=supabase_client,
#             table_name="documents",query_name="match_documents"
#         )
#         return{"status":"success","chunks":len(chunks)}
#     except Exception as e:
#         raise HTTPException(status_code=500,detail=str(e))

@router.post("/ingest")
async def ingest(
    tenant_id: str = Form(...),
    source_type: str = Form(...),
    user_id: str = Form(...),
    link: str = Form(None),
    file: Optional[UploadFile] = File(None)
):
    try:
        if source_type == "pdf" and not file:
            raise HTTPException(status_code=400, detail="PDF file is required for source_type 'pdf'")
        
        # 1. Process into chunks
        chunks = process_input(source_type, tenant_id, link, file)
        
        # 2. Tag EVERY chunk with metadata
        for chunk in chunks:
            chunk.metadata = {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "source_type": source_type,
                "source_name": file.filename if file else link
            }
        
        # 3. THE FIX: Use add_documents() instead of from_documents()
        # get_vector_store() returns the SupabaseVectorStore instance
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        
        return {
            "status": "success", 
            "chunks": len(chunks), 
            "workspace": tenant_id, 
            "source": file.filename if file else link
        }
        
    except Exception as e:
        print(f"Ingest Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/chat")
async def chat(
    tenant_id: str = Form(...),
    question: str = Form(...), 
    user_id: str = Form(...),
    session_id: str = Form(...)
):
    try:
        # Call our manual logic
        answer = run_rag_chain(question, session_id, user_id, tenant_id)

        return {
            "answer": answer,
            "session_id": session_id
        }
    except Exception as e:
        # This will print the error to your console for easier debugging
        print(f"Chat Error Detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check")
async def check_docs(
    tenant_id: str = Query(...), 
    user_id: str = Query(...)
):
    """
    Checks if a workspace has any documents uploaded by a specific user.
    Used for the frontend onboarding workflow.
    """
    try:
        # We perform a count-only query for maximum performance
        response = supabase_client.table("documents").select(
            "id", count="exact"
        ).match({
            "metadata->>tenant_id": tenant_id,
            "metadata->>user_id": user_id
        }).execute()
        
        count = response.count if response.count is not None else 0
        
        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "count": count,
            "has_docs": count > 0
        }
    except Exception as e:
        print(f"Error checking documents: {e}")
        return {"error": str(e), "count": 0, "has_docs": False}
    



