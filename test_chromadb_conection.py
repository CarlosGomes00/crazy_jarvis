import chromadb

try:

    cliente = chromadb.HttpClient(host='localhost', port=8000)

    pulso = cliente.heartbeat()
    print(f"Timestamp do servidor: {pulso}")

except Exception as e:
    print(f"Não foi possível ligar ao ChromaDB: {e}")