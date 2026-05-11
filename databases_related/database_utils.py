import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import chromadb

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


def save_to_database_news(ticker: str, news : list):

    assert news

    try:
        chroma_client = chromadb.HttpClient(host='localhost', port=8000)
        colecao = chroma_client.get_or_create_collection(name="market_news")

        documentos = []
        metadados = []
        ids = []

        for index, artigo in enumerate(news):
            titulo = artigo.get('title', '')
            resumo = artigo.get('summary', '')
            texto_para_vetor = f"Título: {titulo}\nResumo: {resumo}"
            
            meta = {
                "ticker": ticker,
                "data_publicacao": artigo.get('time_published', ''),
                "sentimento": artigo.get('overall_sentiment_label', ''),
                "fonte": artigo.get('source', ''),
                "url": artigo.get('url', '')
            }
            doc_id = f"Idx{index}_{ticker}_{artigo.get('time_published', f'idx_{index}')}"
            
            documentos.append(texto_para_vetor)
            metadados.append(meta)
            ids.append(doc_id)
            
        colecao.upsert(documents=documentos, metadatas=metadados, ids=ids)
        print(f"✅ [ChromaDB] {len(documentos)} vetores injetados para {ticker}.")

    except Exception as e:
        print(f'Erro: {e}')