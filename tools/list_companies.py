import pandas as pd
from langchain_core.documents import Document
from llm.llm import embeddings
from llm.llm import llm
from langchain_classic import hub
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.tools import tool
import yfinance as yf

@tool
def companies_list(question:str):
    """
    data containing the companies to search with their listed names.
    listed name : offical name
    important: Dont look any other column other than these two
    """
    CSV_PATH = r"Companies.csv"
    data = pd.read_csv(CSV_PATH)

    documents = []

    tickers_with_news = []
    tickers_less_than=[]
    for symbol in data['SYMBOL'][:100]:  # Test first 50
        ticker = yf.Ticker(f"{symbol}.NS")
        if ticker.news:
            tickers_with_news.append(symbol)
    for i in tickers_with_news:
        ticker = yf.Ticker(f"{i}.NS")
        if ticker.info.get('currentPrice')<300:
            tickers_less_than.append(i)
    print(tickers_less_than)

    return tickers_less_than

tools=[companies_list]

