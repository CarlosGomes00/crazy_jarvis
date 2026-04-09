import datetime
import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool


@tool('clock', description='Tool para obter dia e hora atual. Usa isto quando te perguntarem o dia ou a hora atual')
def get_current_time(*args, **kwargs):
    """Retorna a data e a hora atual. Útil para quando o utilizador perguntar que dia é hoje, ou que horas são."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



@tool('calculator', description='Tool para fazer calculos. Usa isto para qualquer problema matemático')
def calculator(expression : str):
    """Avalia expressões matemáticas"""
    return str(eval(expression))


web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="Usa isto para pesquisar na internet por informações atuais, notícias ou factos que desconheces. Sê explicito na pesquisa para obter a melhor informação possível"
)


@tool('weather', description='Tool para pesquisar o estado do tempo numa cidade especifica')
def get_weather(localizacao : str):
    try:
        resposta = requests.get(f"https://wttr.in/{localizacao}?format=3")
        return resposta.text
    except Exception as e:
        return f'Não foi possível obter o tempo: {e}'