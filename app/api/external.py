from fastapi import APIRouter, Body,Header,HTTPException
from app.services.rag_service import run_rag_chain
from app.services.supabase_service import verify_external_api_key

router=APIRouter()

@router.post("/chat")
async def universal_chat(
    message:str=Body(...,description="The user's question"),
    tenant_id: str = Body(..., description="The workspace to search in"),
    session_id:str=Body("universal_session",description="Chat history tracking ID"),
    x_api_key:str=Header(...,description="Secret key from the external platform")
):
    
    user_id=await verify_external_api_key(x_api_key)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    
    try:
        answer=run_rag_chain(query=message,
                             session_id=session_id,
                             user_id=user_id,
                             tenant_id=tenant_id
                             
                             )
        return{
            "reply":answer,
            "status":"success",
            "authenticated_user":user_id
        }
    
    except Exception as e:
        print(f"Universal Chat Error:{e}")
        raise HTTPException(status_code=500,detail=str(e))