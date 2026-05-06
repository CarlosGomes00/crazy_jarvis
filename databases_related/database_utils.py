import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER')
db_password =os.getenv('DB_PASSWORD')



def save_to_database_daily(ticker_data):

    ticker = ticker_data['ticker']
    dados = ticker_data['dados']

    try:
        conn = psycopg2.connect(
            host="localhost",
            database="market_data",
            user=db_user,
            password=db_password,
            port="5432"
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                ticker VARCHAR(10),
                price_date DATE,
                close_price DECIMAL(12, 4),
                volume BIGINT,
                PRIMARY KEY (ticker, price_date)
            );
        """)

        valores = []
        for data_str, info in dados.items():
            valores.append((
                ticker,
                data_str,
                info['4. close'],
                info['5. volume']
            ))

        query = """
            INSERT INTO daily_prices (ticker, price_date, close_price, volume)
            VALUES %s
            ON CONFLICT (ticker, price_date) DO NOTHING;
        """

        execute_values(cur, query, valores)
        conn.commit()
        print(f"Postgres: {len(valores)} registos ({ticker}) guardados com sucesso!")

    except Exception as e:
        print(f"Erro no Postgres: {e}")
    
    finally:
        if conn:
            cur.close()
            conn.close()