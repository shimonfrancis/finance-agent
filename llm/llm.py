from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
llm =ChatOpenAI(base_url='http://127.0.0.1:1234/v1',
               api_key='not-needed',model='ibm/granite-4-h-tiny')

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)