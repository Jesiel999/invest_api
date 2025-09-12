import requests
from datetime import datetime
import time
import db  

cursor = db.cursor

def salvar_investimento(dados):
    sql = """
    INSERT INTO invest 
    (inv_codigo, inv_nome, inv_tipo, inv_bolsa, inv_moeda, inv_preco_atual, inv_variacao_dia, inv_variacao_12m, inv_dividend_yield, inv_patrimonio, inv_volume_medio, inv_risco, inv_emissor, inv_vencimento, inv_rentabilidade, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        inv_preco_atual = VALUES(inv_preco_atual),
        inv_variacao_dia = VALUES(inv_variacao_dia),
        inv_variacao_12m = VALUES(inv_variacao_12m),
        inv_dividend_yield = VALUES(inv_dividend_yield),
        inv_patrimonio = VALUES(inv_patrimonio),
        inv_volume_medio = VALUES(inv_volume_medio),
        updated_at = VALUES(updated_at)
    """
    cursor.execute(sql, dados)
    db.db.commit()

def requisicao_com_retry(url, retries=3, delay=2):
    for tentativa in range(retries):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print("Rate limite atingido, aguardando...")
                time.sleep(delay)
            else:
                print(f"Erro na API: {r.status_code}")
        except requests.Timeout:
            print("Tentando novamente...")
            time.sleep(delay)
        except requests.RequestException as e:
            print(f"Error: {e}")
            time.sleep(delay)
    return None

#importação ações
def importar_acoes(acoes):
    total_importadas = 0
    for codigo in acoes:
        url = f"https://brapi.dev/api/quote/{codigo}?token={db.token}"
        
        print(f"🔗 Requisitando: {url}") 
        
        r = requisicao_com_retry(url)
        if not r or "results" not in r or len(r["results"]) == 0:
            print(f"❌ Nenhum resultado retornado da BRAPI para {codigo}")
            continue

        acao = r["results"][0]
        dados = (
            acao["symbol"],
            acao.get("longName", acao["symbol"]),
            "ACAO",
            "B3",
            "BRL",
            acao.get("regularMarketPrice"),
            acao.get("regularMarketChangePercent"),
            None,
            acao.get("dividendYield"),
            None,
            acao.get("regularMarketVolume"),
            None,
            acao.get("longName", acao["symbol"]),
            None,
            None,
            datetime.now()
        )
        salvar_investimento(dados)
        total_importadas += 1

        time.sleep(1)
    return total_importadas


#importação cripto
def importar_cripto(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requisicao_com_retry(url)
    if not r:
        return
    dados = (
        r["symbol"],
        r["symbol"],
        "CRIPTO",
        "BINANCE",
        "BRL",
        float(r["lastPrice"]),
        float(r["priceChangePercent"]),
        None,
        None,
        None,
        float(r["volume"]),
        "ALTO",
        "BINANCE",
        None,
        None,
        datetime.now()
    )
    salvar_investimento(dados)

# Lista de ações
acoes = ["PETR4","VALE3","ITUB4","BBDC4","ABEV3","BBAS3","WEGE3","MGLU3",
         "LREN3","GGBR4","SUZB3","JBSS3","ELET3","ELET6","USIM5","RAIL3",
         "RENT3","B3SA3","LMTB34","PQDP11","GEOO34","IBMB34","STYI11",
         "K1LA34","EGDB11","I1RP34"]

# Lista de criptos
criptos = ["BTCBRL","ETHBRL","LTCBRL","SOLBRL","ADABRL","BNBBRL",
           "XRPBRL","DOGEBRL","MATICBRL","DOTBRL","AVAXBRL","SHIBBRL"]

total_acoes = importar_acoes(acoes)
print(f"Total de ações importadas: {total_acoes}")

total_criptos = 0
for cripto in criptos:
    if importar_cripto(cripto):
        total_criptos += 1
    time.sleep(0.5)

print(f"Total de criptos importadas: {total_criptos}")
print(f"Total geral de investimentos importados: {total_acoes + total_criptos}")
