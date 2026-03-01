from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain,create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from app.core.config import settings
from app.services.supabase_service import get_vector_store
from app.utils.memory import get_chat_history, add_message_to_history


llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=settings.GEMINI_API_KEY,temperature=0)

# # def run_rag_chain(tenant_id:str,question:str):
# #  vector_store=get_vector_store()

# #  retriever=vector_store.as_retriever(
# #     search_kwargs={'filter':{'tenant_id':tenant_id},'k':4}
# # )


# #  prompt=ChatPromptTemplate.from_template(
# #     """Answer the question based only on the context below.
# #     Context:{context}
# #     Question:{input}
# #     """
# # )
# #  doc_chain=create_stuff_documents_chain(llm,prompt)
# #  chain=create_retrieval_chain(
# #   retriever,doc_chain
# #  )

# #  return chain.invoke({"input":question})

# from app.services.supabase_service import supabase_client, embeddings
# from app.utils.memory import get_chat_history, add_message_to_history

# def run_rag_chain(query: str, session_id: str, tenant_id: str):
#     # 1. Retrieve Past Memory (using the RPC logic we fixed)
#     history = get_chat_history(session_id, tenant_id)
    
#     # 2. RAG Retrieval - DIRECT RPC CALL
#     # This bypasses the LangChain wrapper to avoid 'params' errors
#     query_vec = embeddings.embed_query(query)
    
#     # We call the Supabase client directly to execute our SQL function
#     rpc_response = supabase_client.rpc(
#         "match_documents",
#         {
#             "query_embedding": query_vec,
#             "match_count": 3,
#             "p_tenant_id": tenant_id
#         }
#     ).execute()

#     # Extract the text content from the returned rows
#     context_text = "\n".join([row["content"] for row in rpc_response.data])

#     # 3. Construct the Prompt with Memory
#     history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
#     system_prompt = f"""
#     You are a helpful assistant for Tenant: {tenant_id}.
#     Use the context below to answer the question. 
    
#     Context:
#     {context_text}
    
#     Chat History:
#     {history_str}
    
#     User Question: {query}
#     """
    
#     print(f"DEBUG PROMPT: {system_prompt}")

#     # 4. Generate Response using Gemini (LangChain .invoke)
#     response = llm.invoke(system_prompt)
#     answer = response.content

#     # 5. Save Interaction to Memory
#     add_message_to_history(session_id, tenant_id, "user", query)
#     add_message_to_history(session_id, tenant_id, "assistant", answer)

#     return answer

# from app.services.supabase_service import supabase_client, embeddings
# from app.utils.memory import get_chat_history, add_message_to_history

# def run_rag_chain(query: str, session_id: str,  user_id: str, tenant_id: str):
#     # 1. Retrieve Past Memory (Filtered by both Tenant and User for SaaS security)
#     # Ensure your get_chat_history function is updated to accept user_id
#     history = get_chat_history(session_id, tenant_id, user_id)
    
#     # 2. RAG Retrieval - SECURE DUAL-KEY RPC CALL
#     # This ensures User A never sees User B's documents within the same Tenant
#     query_vec = embeddings.embed_query(query)
    
#     # We call the 'match_documents_secure' function we created in Supabase
#     rpc_response = supabase_client.rpc(
#         "match_documents_secure", # Using the secure version we discussed
#         {
#             "query_embedding": query_vec,
            
#             "p_tenant_id": tenant_id,
#             "p_user_id": user_id,
#             "match_count": 3  # The second key for SaaS isolation
#         }
#     ).execute()

#     print(f"DEBUG: Found {len(rpc_response.data)} matching chunks for User: {user_id}")
#     if len(rpc_response.data) > 0:
#      print(f"DEBUG: First chunk preview: {rpc_response.data[0]['content'][:100]}")
#     # Extract the text content from the returned rows
#     context_text = "\n".join([row["content"] for row in rpc_response.data])

#     # 3. Construct the Prompt with specific User/Tenant identity
#     history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
    
#     system_prompt = f"""
#     You are a professional agent
#     Workspace (Tenant): {tenant_id}
#     Authorized User: {user_id}
    
#     Instructions:
#     Answer the question based ONLY on the provided Context and Chat History.
#     If the answer is not in the context, inform the user that no specific 
#     data was found in their private files.

#     Context:
#     {context_text}
    
#     Chat History:
#     {history_str}
    
#     User Question: {query}
#     """
    
#     print(f"--- SECURITY CHECK ---")
#     print(f"Tenant: {tenant_id} | User: {user_id} | Session: {session_id}")

#     # 4. Generate Response using Gemini
#     response = llm.invoke(system_prompt)
#     answer = response.content

#     # 5. Save Interaction to Memory (Tagged with user_id)
#     # This ensures session history is also isolated by user
#     add_message_to_history(session_id, tenant_id, user_id, "user", query)
#     add_message_to_history(session_id, tenant_id, user_id, "assistant", answer)

#     return answer

from app.services.supabase_service import supabase_client, embeddings
from app.utils.memory import get_chat_history, add_message_to_history

def run_rag_chain(query: str, session_id: str, user_id: str, tenant_id: str):
    # 1. LAYER 1: LOCAL MEMORY (The "Conversation Context")
    # This keeps follow-up questions working within THIS specific session.
    # It must use session_id, tenant_id, and user_id.
    history = get_chat_history(session_id, tenant_id, user_id)
    history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
    
    # 2. LAYER 2: GLOBAL KNOWLEDGE (The "Document Context")
    # This allows the AI to see any PDF uploaded by the user, regardless of session.
    # Note: We do NOT pass session_id here.
    query_vec = embeddings.embed_query(query)
    
    rpc_response = supabase_client.rpc(
        "match_documents_secure", # The SQL function we just recreated
        {
            "query_embedding": query_vec,
            "p_tenant_id": tenant_id,
            "p_user_id": user_id,
            "match_count": 5 # Fetching slightly more chunks for better accuracy
        }
    ).execute()
    print(f"\n--- TERMINAL CHUNK CHECK ---")
    print(f"User: {user_id} | Tenant: {tenant_id}")
    print(f"Chunks Found: {len(rpc_response.data)}")

    print(f"--- SECURITY TRACE ---")
    print(f"Session: {session_id} | User: {user_id} | Docs Found: {len(rpc_response.data)}")

    context_text = "\n".join([row["content"] for row in rpc_response.data])

    # 3. THE "BRAIN" MELD: Combine Knowledge + Memory
    system_prompt = f"""
    You are an AI Strategy Assistant for {tenant_id}.
    User Identity: {user_id}

    RULES:
    1. Use [GLOBAL KNOWLEDGE] for facts from uploaded PDFs.
    2. Use [SESSION HISTORY] to understand follow-up questions (like "it", "that", "earlier").
    3. If neither contains the answer, say you don't have that data in your files.

    [GLOBAL KNOWLEDGE]:
    {context_text}
    
    [SESSION HISTORY]:
    {history_str}
    
    USER QUESTION: {query}
    """
    
    # 4. Generate Response
    response = llm.invoke(system_prompt)
    answer = response.content

    # 5. Save Interaction (Ensures history builds up for the next follow-up)
    # This is where session_id is critical!
    add_message_to_history(session_id, tenant_id, user_id, "user", query)
    add_message_to_history(session_id, tenant_id, user_id, "assistant", answer)

    return answer