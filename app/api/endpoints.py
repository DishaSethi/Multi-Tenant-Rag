# from http.client import HTTPException
from fastapi import APIRouter,UploadFile, File,Form,HTTPException
from app.utils.document_loaders import process_input
from app.services.supabase_service import get_vector_store, embeddings, supabase_client
from app.services.rag_service import run_rag_chain
from typing import Optional

router=APIRouter()


@router.post("/ingest")
async def ingest(tenant_id:str=Form(...),
                 source_type:str=Form(...),
                 link:str=Form(None),
                 file:Optional[UploadFile]=File(None)
                 ):
    try:
        if source_type=="pdf" and not file:
            raise HTTPException(status_code=400, detail="PDF file is required for source_type 'pdf'")
        if source_type=="link" and not link:
            raise HTTPException(status_code=400, detail="Link is required for source_type 'link'")
        
        chunks=process_input(source_type,tenant_id,link,file)
        for chunk in chunks:
            chunk.metadata = {"tenant_id": tenant_id}
        
        get_vector_store().from_documents(
            chunks,embeddings, client=supabase_client,
            table_name="documents",query_name="match_documents"
        )
        return{"status":"success","chunks":len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@router.post("/chat")
async def chat(
    tenant_id: str = Form(...),
    question: str = Form(...), 
    session_id: str = Form(...)
):
    try:
        # Call our manual logic
        answer = run_rag_chain(question, session_id, tenant_id)
        
        return {
            "answer": answer,
            "session_id": session_id
        }
    except Exception as e:
        # This will print the error to your console for easier debugging
        print(f"Chat Error Detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))
