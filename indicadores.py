"""
Módulo para Cálculo de Indicadores Técnicos.

Este arquivo contém funções que utilizam a biblioteca 'ta' para calcular
diversos indicadores técnicos comumente usados em análise de séries temporais
financeiras, como Médias Móveis Exponenciais (EMA), MACD, RSI e SMA de Volume.
"""
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volume import VolumeSMAIndicator

def calcular_ema(series_fechamento: pd.Series, periodo: int) -> pd.Series:
    """
    Calcula a Média Móvel Exponencial (EMA) para uma série de preços de fechamento.

    Args:
        series_fechamento (pd.Series): Série Pandas contendo os preços de fechamento.
        periodo (int): O período (número de candles) para o cálculo da EMA.

    Returns:
        pd.Series: Uma Série Pandas contendo os valores da EMA.
                   Valores NaN são retornados no início da série onde não há dados suficientes para o cálculo.
    """
    if not isinstance(series_fechamento, pd.Series):
        raise TypeError("series_fechamento deve ser uma Series do Pandas.")
    if not isinstance(periodo, int) or periodo <= 0:
        raise ValueError("periodo deve ser um inteiro positivo.")
    
    ema_obj = EMAIndicator(close=series_fechamento, window=periodo, fillna=False)
    return ema_obj.ema_indicator()

def calcular_macd(series_fechamento: pd.Series, periodo_curto: int = 12, periodo_longo: int = 26, periodo_sinal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calcula o Moving Average Convergence Divergence (MACD).

    O MACD é composto por três componentes:
    1. Linha MACD: Diferença entre duas EMAs (curta e longa).
    2. Linha de Sinal: Uma EMA da Linha MACD.
    3. Histograma MACD: Diferença entre a Linha MACD e a Linha de Sinal.

    Args:
        series_fechamento (pd.Series): Série Pandas contendo os preços de fechamento.
        periodo_curto (int, optional): Período da EMA rápida. Default é 12.
        periodo_longo (int, optional): Período da EMA lenta. Default é 26.
        periodo_sinal (int, optional): Período da EMA de sinal. Default é 9.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: Uma tupla contendo três Séries Pandas:
            - Linha MACD.
            - Linha de Sinal.
            - Histograma MACD.
        Valores NaN são retornados no início das séries onde não há dados suficientes.
    """
    if not isinstance(series_fechamento, pd.Series):
        raise TypeError("series_fechamento deve ser uma Series do Pandas.")
    if not all(isinstance(p, int) and p > 0 for p in [periodo_curto, periodo_longo, periodo_sinal]):
        raise ValueError("Todos os períodos devem ser inteiros positivos.")
    if periodo_curto >= periodo_longo:
        raise ValueError("periodo_curto deve ser menor que periodo_longo.")

    macd_obj = MACD(close=series_fechamento, window_slow=periodo_longo, window_fast=periodo_curto, window_sign=periodo_sinal, fillna=False)
    return macd_obj.macd(), macd_obj.macd_signal(), macd_obj.macd_diff()

def calcular_rsi(series_fechamento: pd.Series, periodo: int = 14) -> pd.Series:
    """
    Calcula o Índice de Força Relativa (RSI).

    O RSI é um oscilador de momentum que mede a velocidade e a mudança 
    dos movimentos de preços. Valores típicos de sobrecompra são acima de 70 
    e de sobrevenda abaixo de 30.

    Args:
        series_fechamento (pd.Series): Série Pandas contendo os preços de fechamento.
        periodo (int, optional): O período (número de candles) para o cálculo do RSI. Default é 14.

    Returns:
        pd.Series: Uma Série Pandas contendo os valores do RSI.
                   Valores NaN são retornados no início da série onde não há dados suficientes.
    """
    if not isinstance(series_fechamento, pd.Series):
        raise TypeError("series_fechamento deve ser uma Series do Pandas.")
    if not isinstance(periodo, int) or periodo <= 0:
        raise ValueError("periodo deve ser um inteiro positivo.")

    rsi_obj = RSIIndicator(close=series_fechamento, window=periodo, fillna=False)
    return rsi_obj.rsi()

def calcular_sma_volume(series_volume: pd.Series, periodo: int = 20) -> pd.Series:
    """
    Calcula a Média Móvel Simples (SMA) do Volume.

    Args:
        series_volume (pd.Series): Série Pandas contendo os volumes de negociação.
        periodo (int, optional): O período (número de candles) para o cálculo da SMA do Volume. Default é 20.

    Returns:
        pd.Series: Uma Série Pandas contendo os valores da SMA do Volume.
                   Valores NaN são retornados no início da série onde não há dados suficientes.
    """
    if not isinstance(series_volume, pd.Series):
        raise TypeError("series_volume deve ser uma Series do Pandas.")
    if not isinstance(periodo, int) or periodo <= 0:
        raise ValueError("periodo deve ser um inteiro positivo.")

    sma_vol_obj = VolumeSMAIndicator(volume=series_volume, window=periodo, fillna=False)
    return sma_vol_obj.volume_sma()

if __name__ == "__main__":
    # Dados de exemplo para teste (simulados e mais realistas)
    data_size = 60 
    # Geração de preços simulados com alguma tendência e volatilidade
    precos_base = pd.Series([50 + i + (i/5)**2 for i in range(data_size)]) + pd.Series(pd.np.random.normal(0, 2, data_size)).cumsum()
    precos_fechamento = precos_base.round(2)
    precos_fechamento.iloc[0] = abs(precos_fechamento.iloc[0]) 
    precos_fechamento = precos_fechamento.cummax() 
    precos_fechamento = precos_fechamento + pd.Series(pd.np.random.normal(0, 1, data_size)).cumsum().round(2)
    precos_fechamento = precos_fechamento.apply(lambda x: max(1, x)) 

    # Geração de volumes simulados
    volumes = pd.Series(pd.np.random.randint(100, 500, data_size)) + (precos_fechamento - precos_fechamento.shift(1)).abs() * 1000
    volumes = volumes.fillna(100).astype(int).apply(lambda x: max(10, x))

    df_exemplo = pd.DataFrame({
        'close': precos_fechamento,
        'volume': volumes
    })
    
    df_exemplo.dropna(inplace=True) 
    df_exemplo.reset_index(drop=True, inplace=True)

    print(f"Número de pontos de dados para teste: {len(df_exemplo)}")
    if len(df_exemplo) < 35: 
        print("Alerta: Dados de exemplo insuficientes para alguns indicadores após limpeza. Aumente data_size.")
    
    print("DataFrame de Exemplo (primeiras 5 linhas):")
    print(df_exemplo.head())
    print("\n" + "="*80 + "\n")

    # Testar EMA
    periodo_ema = 10
    print(f"Testando EMA({periodo_ema})...")
    df_exemplo['ema'] = calcular_ema(df_exemplo['close'], periodo_ema)
    print(f"EMA ({periodo_ema}) - Últimas 10 linhas (de {len(df_exemplo)} totais):")
    print(df_exemplo[['close', 'ema']].tail(10))
    print("\n" + "="*80 + "\n")

    # Testar MACD
    periodo_curto_macd = 12
    periodo_longo_macd = 26
    periodo_sinal_macd = 9
    print(f"Testando MACD({periodo_curto_macd}, {periodo_longo_macd}, {periodo_sinal_macd})...")
    df_exemplo['macd_line'], df_exemplo['macd_signal_line'], df_exemplo['macd_histogram'] = calcular_macd(
        df_exemplo['close'], periodo_curto_macd, periodo_longo_macd, periodo_sinal_macd
    )
    print(f"MACD ({periodo_curto_macd}, {periodo_longo_macd}, {periodo_sinal_macd}) - Últimas 10 linhas:")
    print(df_exemplo[['close', 'macd_line', 'macd_signal_line', 'macd_histogram']].tail(10))
    print("\n" + "="*80 + "\n")

    # Testar RSI
    periodo_rsi = 14
    print(f"Testando RSI({periodo_rsi})...")
    df_exemplo['rsi'] = calcular_rsi(df_exemplo['close'], periodo_rsi)
    print(f"RSI ({periodo_rsi}) - Últimas 10 linhas:")
    print(df_exemplo[['close', 'rsi']].tail(10))
    print("\n" + "="*80 + "\n")

    # Testar SMA do Volume
    periodo_sma_volume = 20
    print(f"Testando SMA Volume({periodo_sma_volume})...")
    df_exemplo['sma_volume'] = calcular_sma_volume(df_exemplo['volume'], periodo_sma_volume)
    print(f"SMA Volume ({periodo_sma_volume}) - Últimas 10 linhas:")
    print(df_exemplo[['volume', 'sma_volume']].tail(10))
    print("\n" + "="*80 + "\n")

    print("Verificando NaNs no início das séries calculadas (esperado):")
    print(f"EMA NaNs: {df_exemplo['ema'].isnull().sum()} de {len(df_exemplo)} (esperado ~{periodo_ema-1})")
    print(f"MACD Line NaNs: {df_exemplo['macd_line'].isnull().sum()} (esperado ~{periodo_longo_macd-1})")
    print(f"MACD Signal Line NaNs: {df_exemplo['macd_signal_line'].isnull().sum()} (esperado ~{periodo_longo_macd + periodo_sinal_macd - 2})")
    print(f"MACD Histogram NaNs: {df_exemplo['macd_histogram'].isnull().sum()} (esperado ~{periodo_longo_macd + periodo_sinal_macd - 2})")
    print(f"RSI NaNs: {df_exemplo['rsi'].isnull().sum()} (esperado ~{periodo_rsi})") 
    print(f"SMA Volume NaNs: {df_exemplo['sma_volume'].isnull().sum()} (esperado ~{periodo_sma_volume-1})")

    print("\nTestes concluídos.")
