from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain,create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from app.core.config import settings
from app.services.supabase_service import get_vector_store
from app.utils.memory import get_chat_history, add_message_to_history


llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=settings.GEMINI_API_KEY,temperature=0)

# def run_rag_chain(tenant_id:str,question:str):
#  vector_store=get_vector_store()

#  retriever=vector_store.as_retriever(
#     search_kwargs={'filter':{'tenant_id':tenant_id},'k':4}
# )


#  prompt=ChatPromptTemplate.from_template(
#     """Answer the question based only on the context below.
#     Context:{context}
#     Question:{input}
#     """
# )
#  doc_chain=create_stuff_documents_chain(llm,prompt)
#  chain=create_retrieval_chain(
#   retriever,doc_chain
#  )

#  return chain.invoke({"input":question})

from app.services.supabase_service import supabase_client, embeddings
from app.utils.memory import get_chat_history, add_message_to_history

def run_rag_chain(query: str, session_id: str, tenant_id: str):
    # 1. Retrieve Past Memory (using the RPC logic we fixed)
    history = get_chat_history(session_id, tenant_id)
    
    # 2. RAG Retrieval - DIRECT RPC CALL
    # This bypasses the LangChain wrapper to avoid 'params' errors
    query_vec = embeddings.embed_query(query)
    
    # We call the Supabase client directly to execute our SQL function
    rpc_response = supabase_client.rpc(
        "match_documents",
        {
            "query_embedding": query_vec,
            "match_count": 3,
            "p_tenant_id": tenant_id
        }
    ).execute()

    # Extract the text content from the returned rows
    context_text = "\n".join([row["content"] for row in rpc_response.data])

    # 3. Construct the Prompt with Memory
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
    system_prompt = f"""
    You are a helpful assistant for Tenant: {tenant_id}.
    Use the context below to answer the question. 
    
    Context:
    {context_text}
    
    Chat History:
    {history_str}
    
    User Question: {query}
    """
    
    print(f"DEBUG PROMPT: {system_prompt}")

    # 4. Generate Response using Gemini (LangChain .invoke)
    response = llm.invoke(system_prompt)
    answer = response.content

    # 5. Save Interaction to Memory
    add_message_to_history(session_id, tenant_id, "user", query)
    add_message_to_history(session_id, tenant_id, "assistant", answer)

    return answer