import shutil
import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def process_input(source_type:str, tenant_id:str, value:str=None, file=None)-> List[Document]:
    docs=[]

    if source_type=="link":
        loader=WebBaseLoader(value)
        docs=loader.load()

    elif source_type=="pdf" and file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path=temp_file.name
        try:
            loader=PyPDFLoader(temp_path)
            docs=loader.load()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    elif source_type=="qa" and value:
        docs=[Document(page_content=value)]
    
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks=text_splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["tenant_id"]=tenant_id
        chunk.metadata["source_type"]=source_type
        if source_type=="link":
            chunk.metadata["source"]=value
        elif source_type=="pdf":
            chunk.metadata["source"] = getattr(file, "filename", "uploaded_pdf")
    print(f"Total chunks created: {len(chunks)}")
    return chunks
