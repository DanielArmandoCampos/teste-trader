"""
Módulo para interação com a API V4 do Mercado Bitcoin.

Este módulo fornece funções para buscar dados de mercado, como informações
de candles (OHLCV), diretamente da API pública do Mercado Bitcoin.
"""
import requests
import pandas as pd
from datetime import datetime

API_V4_BASE_URL = "https://api.mercadobitcoin.net/api/v4/markets/" # URL base da API V4

def buscar_candles_horarios(simbolo: str = "BTC-BRL", resolucao: str = "1h", from_timestamp: int = None, to_timestamp: int = None, limit: int = 200):
    """
    Busca dados de candles (OHLCV - Open, High, Low, Close, Volume) da API V4 do Mercado Bitcoin.

    Args:
        simbolo (str, optional): O símbolo do par de negociação. Default "BTC-BRL".
                                 Exemplos: "BTC-BRL", "ETH-BRL".
        resolucao (str, optional): A resolução (timeframe) dos candles. Default "1h".
                                   Valores comuns: "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d".
        from_timestamp (int, optional): Timestamp UNIX (em segundos) do início do período desejado.
                                        Se não fornecido, a API retorna os candles mais recentes até 'to_timestamp' ou até o 'limit'.
        to_timestamp (int, optional): Timestamp UNIX (em segundos) do fim do período desejado.
                                      Se não fornecido, geralmente corresponde ao momento atual.
        limit (int, optional): Número máximo de candles a serem retornados. Default 200.
                               O máximo permitido pela API pode variar (ex: 1000 para algumas resoluções).

    Returns:
        pd.DataFrame: Um DataFrame do Pandas contendo os dados dos candles, com as seguintes colunas:
                      - 'timestamp': Timestamp do candle convertido para objeto datetime.
                      - 'open': Preço de abertura.
                      - 'close': Preço de fechamento.
                      - 'high': Preço máximo.
                      - 'low': Preço mínimo.
                      - 'volume': Volume negociado no período.
                      Retorna um DataFrame vazio em caso de erro na requisição, falha na decodificação JSON,
                      ou se a API retornar uma resposta inesperada.

    Raises:
        Este função trata exceções internamente e retorna um DataFrame vazio em caso de falha,
        imprimindo o erro no console.
    """
    # Constrói a URL completa para o endpoint de candles
    url = f"{API_V4_BASE_URL}{simbolo}/candles"
    
    # Monta o dicionário de parâmetros para a requisição GET
    params = {
        "resolution": resolucao, 
        "limit": limit
    }

    if from_timestamp:
        params["from"] = from_timestamp
    if to_timestamp:
        params["to"] = to_timestamp

    try:
        # Realiza a requisição GET para a API
        response = requests.get(url, params=params, timeout=10) # Timeout de 10 segundos
        response.raise_for_status()  # Levanta um erro HTTP para respostas ruins (4xx ou 5xx)
    except requests.exceptions.RequestException as e:
        # Tratamento de erros de requisição (ex: timeout, erro de DNS, etc.)
        print(f"Erro na requisição à API: {e}")
        return pd.DataFrame()

    # Colunas esperadas no DataFrame final
    expected_df_cols = ['timestamp', 'open', 'close', 'high', 'low', 'volume']

    if response.status_code == 200:
        try:
            # Tenta decodificar a resposta JSON
            data = response.json()
        except ValueError as e: 
            print(f"Erro ao decodificar JSON: {e}")
            return pd.DataFrame()

        # Verifica se a chave 'candles' existe e é uma lista
        if 'candles' not in data or not isinstance(data['candles'], list):
            print("Erro: 'candles' não encontrado ou não é uma lista na resposta da API.")
            return pd.DataFrame()

        candles_list = data['candles']
        
        if not candles_list:
            # Se a API retornar uma lista vazia de candles, retornar um DataFrame vazio com as colunas esperadas.
            return pd.DataFrame(columns=expected_df_cols)

        # Cria o DataFrame a partir da lista de candles
        df = pd.DataFrame(candles_list)

        if df.empty:
            return pd.DataFrame(columns=expected_df_cols)

        # Assegura que todas as colunas esperadas existam.
        if not all(col in df.columns for col in expected_df_cols):
            print(f"Erro: Colunas esperadas {expected_df_cols} não encontradas no DataFrame. Colunas atuais: {df.columns.tolist()}")
            # Tenta reestruturar o DataFrame com as colunas esperadas, preenchendo com NA onde faltar
            for col in expected_df_cols:
                if col not in df.columns:
                    df[col] = pd.NA 
            df = df[expected_df_cols] # Garante a ordem e presença das colunas
            # Se ainda assim estiver problemático (ex: 'timestamp' crucial faltando), pode ser melhor retornar vazio.
            if df['timestamp'].isnull().all(): # Exemplo de verificação crítica
                 return pd.DataFrame(columns=expected_df_cols)


        # Converte a coluna 'timestamp' de segundos para objetos datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Converte colunas numéricas para o tipo float, tratando erros
        numeric_cols = ['open', 'close', 'high', 'low', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce') # 'coerce' transforma erros em NaT/NaN
        
        return df
    else:
        # Tratamento para outros status codes de erro da API
        print(f"Erro na API: Status Code {response.status_code}")
        try:
            print(f"Conteúdo da resposta: {response.json()}")
        except ValueError: 
            print(f"Conteúdo da resposta (não JSON): {response.text}")
        return pd.DataFrame(columns=expected_df_cols)

if __name__ == "__main__":
    print("Exemplo 1: Buscando candles com parâmetros padrão (BTC-BRL, 1h, limit 200)...")
    candles_df_padrao = buscar_candles_horarios()
    if not candles_df_padrao.empty:
        print("Primeiras 5 linhas:")
        print(candles_df_padrao.head())
        print("\nÚltimas 5 linhas:")
        print(candles_df_padrao.tail())
        print(f"\nTotal de candles retornados: {len(candles_df_padrao)}")
    else:
        print("Nenhum dado retornado para a consulta padrão.")

    print("\n" + "="*80 + "\n")

    print("Exemplo 2: Buscando os últimos 3 candles de 1 hora para BTC-BRL...")
    to_timestamp_ex2 = int(datetime.now().timestamp())
    from_timestamp_ex2 = to_timestamp_ex2 - (3 * 3600) 

    print(f"Calculando para o período de {datetime.fromtimestamp(from_timestamp_ex2)} até {datetime.fromtimestamp(to_timestamp_ex2)}")

    candles_df_ultimos_3 = buscar_candles_horarios(
        simbolo="BTC-BRL",
        resolucao="1h",
        from_timestamp=from_timestamp_ex2,
        to_timestamp=to_timestamp_ex2,
        limit=3
    )

    if not candles_df_ultimos_3.empty:
        print("\nResultado para os últimos 3 candles (ou menos, se disponíveis na janela de 3h):")
        print(candles_df_ultimos_3)
    else:
        print("\nNenhum dado retornado para BTC-BRL, 1h, nas últimas 3 horas (limit 3).")

    print("\nFim dos exemplos de uso.")
