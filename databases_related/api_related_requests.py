import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

chave_alpha_vantage = os.getenv('ALPHA_VANTAGE_API_KEY') 



def check_ticker(ticker : str):

    url_ticker_search = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey={chave_alpha_vantage}'
    resp_search = requests.get(url_ticker_search).json()

    if "Information" in resp_search:
        print(f"Limite da API atingido: {resp_search['Information']}")
        return None

    if "bestMatches" not in resp_search or len(resp_search["bestMatches"]) == 0:
        print(f"Nenhum resultado para o ticker {ticker}")
        return None

    best_match = resp_search['bestMatches'][0]

    company_info = {
        "ticker": best_match["1. symbol"],
        "nome": best_match["2. name"]
    }

    return company_info



def extract_daily_prices(ticker : str):

    print(f'A procurar informação sobre o ticker: {ticker}')

    company_info = check_ticker(ticker)

    if not company_info:
        return None

    time.sleep(2)

    ticker = company_info['ticker']
    nome = company_info['nome']

    url_daily_prices = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={chave_alpha_vantage}"

    resp_prices = requests.get(url_daily_prices).json()

    if "Time Series (Daily)" not in resp_prices:
        print(resp_prices)
        return None
    
    serie_diaria = resp_prices["Time Series (Daily)"]
    
    return {
        "ticker": ticker,
        "nome": nome,
        "dados": serie_diaria
    }



def extract_market_info(ticker : str, limit : int = 3):

    print(f'A procurar top {limit} de noticias para o ticker: {ticker}')

    company_info = check_ticker(ticker)

    if not company_info:
        return None
    
    time.sleep(2)
    
    url_news = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&limit={limit}&apikey={chave_alpha_vantage}'

    news = requests.get(url_news).json()
    
    if 'feed' not in news:
        print('Erro, request sem a info esperada')
        return None

    news_filtradas = news['feed'][:limit] 

    return news_filtradas

    







    

