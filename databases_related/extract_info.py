from api_related_requests import extract_daily_prices
from database_utils import save_to_database_daily



if __name__ == '__main__':
    dados_finais = extract_daily_prices('SPY')

    if dados_finais:
        save_to_database_daily(dados_finais)