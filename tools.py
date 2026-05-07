import datetime
import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
import urllib.parse
import os
import subprocess
import json
from dotenv import load_dotenv, find_dotenv
from e2b import Sandbox
import docker
import psycopg2


#@tool('clock', description='Tool para obter dia e hora atual. Usa isto quando te perguntarem o dia ou a hora atual')
#def get_current_time(*args, **kwargs):
#    """Retorna a data e a hora atual. Útil para quando o utilizador perguntar que dia é hoje, ou que horas são."""
#    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


load_dotenv(find_dotenv())
chave_tavily = os.getenv('TAVILY_API_KEY')
chave_e2b = os.getenv('E2B_API_KEY')
chave_db_user = os.getenv('DB_USER')
chave_db_pass = os.getenv('DB_PASSWORD')


@tool('calculator', description='Tool para fazer calculos. Usa isto para qualquer problema matemático')
def calculator(expression : str):
    """Avalia expressões matemáticas"""
    return str(eval(expression))


#web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="Usa isto para pesquisar na internet por informações atuais, notícias ou factos que desconheces. Sê explicito na pesquisa para obter a melhor informação possível"
#)


web_search = TavilySearch(
    max_results=3,
    search_depth="advanced", 
    description="Usa isto para pesquisar na internet por informações atuais, notícias, resultados desportivos ou factos.",
    tavily_api_key=chave_tavily
)


@tool('weather', description='Tool para pesquisar o estado do tempo, temperatura ou previsão de chuva numa cidade especifica')
def get_weather(localizacao : str):
    """Permite procurar o clima e a existência de chuva em determinadas localizações"""
    try:
        resposta = requests.get(f"https://wttr.in/{localizacao}?format=%C,+Temp:+%t,+Chuva:+%p")
        return resposta.text
    except Exception as e:
        return f'Não foi possível obter o tempo: {e}'
    

@tool('open_program', description = 'Tool para abrir programas no computador. Apenas podes abrir os programas permitidos!!')
def open_program(nome_app: str):
    """Executa apenas aplicações permitidas usando subprocessos seguros"""
    
    apps_permitidas = {
            "bloco de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "notas": "notepad.exe",
            "calculadora": "calc.exe",
            "calc": "calc.exe",
            "chrome": "chrome.exe",
            "browser": "chrome.exe",
            "internet": "chrome.exe",
            "tradingview": "TradingView.exe"
    }
    
    app_limpa = nome_app.lower().replace(' ', '')
    if app_limpa in apps_permitidas:
        try:
            subprocess.run([apps_permitidas[app_limpa]], check=True, shell=False)
            return f"A abrir {nome_app}."
        except Exception as e:
            return f"Erro ao executar: {e}"
    else:
        return f"Acesso negado."


@tool('play_spotify_music', description='Usa esta tool para abrir o Spotify e procurar por uma música, artista ou podcast específico.')
def play_spotify_music(pesquisa: str):
    """Abre o Spotify com a pesquisa formatada."""
    try:
        query_formatada = urllib.parse.quote(pesquisa)
        os.system(f"start spotify:search:{query_formatada}")
        
        return f"O Spotify foi aberto com a pesquisa: {pesquisa}."
    except Exception as e:
        return f"Erro aos sistemas de áudio: {e}"
    


@tool('remember_user_facts', description='Usa esta tool quando for necessário guardar informação, gostos pessoais ou tarefas do utilizador')
def remember_user_facts(new_facts : dict):
    """Guarda ou atualiza informações no perfil do utilizador (perfil.json)."""

    file = 'perfil.json'
    dados_perfil = {}

    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                dados_perfil = json.load(f)
        except json.JSONDecodeError:
            print("Aviso: O perfil.json estava corrompido e foi limpo")
            dados_perfil = {}

    dados_perfil.update(new_facts)

    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(dados_perfil, f, indent=4, ensure_ascii=False)
        return f"Sucesso: Guardei as {len(new_facts)} informação na minha memória permanente."

    except Exception as e:
        return f"Erro ao tentar guardar na memória: {e}"



@tool('execute_code_local', description='Esta toll serve para executar código LOCALMENTE. Deve ser utilizada como ferramenta principal e por defeito para escrever/testar código, com excepções dos casos em que o user menciona a cloud!')
def execute_code_local(code: str):

    try:
        client = docker.from_env()

        comando = ["timeout", "10", "python", "-c", code]

        print('Jarvis a instanciar o docker...')

        resultado = client.containers.run(
            image='python:3.10-alpine',
            command=comando,
            remove=True,
            network_disabled=True,
            mem_limit='200m'
        )
    
        return f"Output do Docker Local:\n{resultado.decode('utf-8')}"

    except docker.errors.ContainerError as e:
        erro_txt = e.stderr.decode('utf-8') if e.stderr else 'Timeout de excedido'
        print(f"Erro no código do docker: {erro_txt}")
        return f"O código falhou. Erro:\n{erro_txt}"
    
    except Exception as e:
        print(f'Erro a instanciar o docker: {e}')
        return f'Erro no Docker Local: {e}'



@tool('execute_code_cloud', description='Esta tool serve para executar código na CLOUD utilizando o E2B. ATENÇÃO: Usa APENAS se o utilizador pedir explicitamente para correr na "nuvem", "cloud" ou "E2B".')
def execute_code_cloud(code: str):
    """Executa código numa Sandbox remota e segura"""
    
    sbx = None
    
    try:
        print('A instanciar a sandbox na cloud')
        sbx = Sandbox.create(timeout=60)

        caminho_ficheiro = "/tmp/script_jarvis.py"
        sbx.files.write(caminho_ficheiro, code)

        resultado = sbx.commands.run(f"python {caminho_ficheiro}")

        output = resultado.error
        erro = resultado.stderr

        if erro:
            return f'Código com erros:\nErro: {erro}\nOutput: {output}'

        return f"Resultado da Cloud:\n{output if output else 'Código executado (sem output no terminal).'}"

    except Exception as e:
        print(f'Erro na tool: {e}')
        return f"Erro na ligação: {e}"

    finally:
        if sbx:
            sbx.kill()


@tool('get_daily_prices', description='Esta tool serve para ir buscar informações sobre preços diários de uma ação/ETF à base de dados. Usa esta tool quando o utilizador perguntar por variações DIÁRIAS')
def get_daily_prices(ticker: str, dias: int):
    
    try:

        conn = psycopg2.connect(
            host="localhost",
            database="market_data",
            user=chave_db_user,
            password=chave_db_pass,
            port="5432"
        )

        cur = conn.cursor()

        query = """
            SELECT price_date, close_price, volume
            FROM daily_prices
            WHERE ticker = %s
            ORDER BY price_date DESC
            LIMIT %s;
        """

        cur.execute(query, (ticker, dias))
        linhas = cur.fetchall()

        if not linhas:
            return f"Não foram encontrados encontrei dados para o ticker '{ticker}' na base de dados. Informa o utilizador que é necessário extrair os dados primeiro."
        
        relatorio = f'Dados históricos recentes para {ticker}:\n'

        for linha in linhas:
            data_preco, preco, volume = linha
            relatorio += f"- Data: {data_preco} | Preço de Fecho: ${preco} | Volume: {volume}\n"

        return relatorio
    
    except Exception as e:
        return f"Erro ao tentar ler a base de dados: {e}"
    
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()


@tool('get_weekly_prices', description='Esta tool serve para ir buscar informações sobre preços semanais de uma ação/ETF à base de dados. Usa esta tool quando o utilizador perguntar por variações SEMANAIS')
def get_weekly_prices(ticker: str, semanas: int):
    
    try:

        conn = psycopg2.connect(
            host="localhost",
            database="market_data",
            user=chave_db_user,
            password=chave_db_pass,
            port="5432"
        )

        cur = conn.cursor()

        query = """
                    SELECT week_start, max_close_price, min_close_price, avg_close_price, total_weekly_volume
                    FROM weekly_prices
                    WHERE ticker = %s
                    LIMIT %s;
                """

        cur.execute(query, (ticker, semanas))
        linhas = cur.fetchall()

        if not linhas:
            return f"Não foram encontrados encontrei dados para o ticker '{ticker}' na base de dados. Informa o utilizador que é necessário extrair os dados primeiro."
        
        relatorio = f'Dados históricos recentes para {ticker}:\n'

        for linha in linhas:
            data_preco, preco_maximo, preco_minimo, preco_medio, volume = linha
            relatorio += f"- Semana: {data_preco} | Preço Maximo: {preco_maximo} | Preço Minimo: {preco_minimo}$ | Preço Médio: {preco_medio}$ | Volume: {volume}\n"

        return relatorio
    
    except Exception as e:
        return f"Erro ao tentar ler a base de dados: {e}"
    
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()