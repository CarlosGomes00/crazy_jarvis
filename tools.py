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


#@tool('clock', description='Tool para obter dia e hora atual. Usa isto quando te perguntarem o dia ou a hora atual')
#def get_current_time(*args, **kwargs):
#    """Retorna a data e a hora atual. Útil para quando o utilizador perguntar que dia é hoje, ou que horas são."""
#    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


load_dotenv(find_dotenv())
chave_tavily = os.getenv('TAVILY_API_KEY')
chave_e2b = os.getenv('E2B_API_KEY')


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



@tool('execute_code_cloud', description='Esta tool serve para executar código na Cloud utilizando o E2B. ATENÇÃO: Usa APENAS se o utilizador pedir explicitamente para correr na "nuvem", "cloud" ou "E2B".')
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