from api_related_requests import extract_daily_prices, extract_market_info
from database_utils import save_to_database_daily, save_to_database_news
import time


if __name__ == '__main__':
    
    ticker = 'QQQ'

    dados_finais = extract_daily_prices(ticker)

    time.sleep(2)
    
    news = extract_market_info(ticker)

    if dados_finais:
      save_to_database_daily(dados_finais)

    if news:
        save_to_database_news(ticker=ticker, news=news)