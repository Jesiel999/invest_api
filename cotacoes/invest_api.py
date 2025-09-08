import requests
from datetime import datetime

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

def importar_acao(codigo):
    url = f"https://brapi.dev/api/quote/{codigo}?token=SEU_TOKEN"
    r = requests.get(url).json()
    
    if "results" in r:
        acao = r["results"][0]
        dados = (
            acao["symbol"],                  # codigo
            acao["longName"],                # nome
            "ACAO",                          # tipo_investimento
            "B3",                            # bolsa
            "BRL",                           # moeda
            acao["regularMarketPrice"],      # preco_atual
            acao["regularMarketChangePercent"], # variacao_dia
            None,                            # variacao_12m (pode calcular separado)
            acao.get("dividendYield"),       # dividend_yield
            None,                            # patrimonio
            acao.get("regularMarketVolume"), # volume_medio
            None,                            # risco
            acao.get("longName"),            # emissor (pode ajustar)
            None,                            # vencimento
            None,                            # rentabilidade
            datetime.now()                   # updated_at
        )
        salvar_investimento(dados)

def importar_cripto(symbol="BTCBRL"):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url).json()

    dados = (
        r["symbol"],                        # codigo
        r["symbol"],                        # nome (simplificado)
        "CRIPTO",                           # tipo_investimento
        "BINANCE",                          # bolsa
        "BRL",                              # moeda
        float(r["lastPrice"]),              # preco_atual
        float(r["priceChangePercent"]),     # variacao_dia
        None,                               # variacao_12m
        None,                               # dividend_yield
        None,                               # patrimonio
        float(r["volume"]),                 # volume_medio
        "ALTO",                             # risco
        "BINANCE",                          # emissor
        None,                               # vencimento
        None,                               # rentabilidade
        datetime.now()                      # updated_at
    )
    salvar_investimento(dados)


importar_acao("PETR4")   
importar_acao("VALE3")  
importar_cripto("BTCBRL")
importar_cripto("ETHBRL")
importar_cripto("LTCBRL")
importar_cripto("SOLBRL")
importar_cripto("ADABRL")

print("Investimentos importados com sucesso!")
