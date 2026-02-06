from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from llm.llm import llm, embeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic import hub



class RulesRAGInput(BaseModel):
    query: str = Field(..., description="The specific trading rule or strategy to look up")
    context: Optional[str] = Field(None, description="Additional context like 'Bank Nifty' or 'Expiry day'")

# 1. Initialize DB ONCE outside the function to prevent file locking
vectorstore = Chroma(
    persist_directory="./DB/chroma_db", 
    embedding_function=embeddings  # Assumes 'embeddings' is defined globally
)

@tool(args_schema=RulesRAGInput)
def query_investment_rules(query: str, context: Optional[str] = None) -> str:
    """
    Query the trading handbook for rules, risk management, and strategy setups.
    Use this to get specific guidance on Nifty/BankNifty principles.
    """
    
    # Combine query and context for a better semantic search
    search_query = f"{query} {context}" if context else query
    
    # 2. Execute the search
    docs = vectorstore.similarity_search(search_query, k=3)
    
    # 3. Format output as a string (LLMs prefer text over raw Dicts for tools)
    results = []
    for doc in docs:
        results.append(f"SOURCE: {doc.metadata.get('source', 'Handbook')}\nCONTENT: {doc.page_content}")
    
    return "\n\n---\n\n".join(results)
    
    