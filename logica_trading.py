"""
Módulo de Lógica de Trading.

Este arquivo implementa a lógica de decisão para identificar sinais de compra
e venda com base em um conjunto de indicadores técnicos e condições de mercado.
As funções aqui utilizam dados de candles e indicadores pré-calculados para
determinar se uma oportunidade de trading existe.
"""
import pandas as pd
import config # Importar o módulo de configuração

def verificar_sinal_de_compra(df_completo: pd.DataFrame) -> bool:
    """
    Verifica se há um sinal de compra com base nos indicadores técnicos do DataFrame.

    Um sinal de compra é considerado válido se todas as seguintes condições forem atendidas:
    1.  **Tendência Principal de Alta**: O preço de fechamento atual está acima da Média Móvel Exponencial de 200 períodos (EMA 200).
    2.  **Sinal de Entrada Primário**:
        a.  **Cruzamento de EMAs**: A EMA de 12 períodos cruza acima da EMA de 26 períodos.
        OU
        b.  **Cruzamento de MACD**: A linha MACD cruza acima da linha de Sinal MACD, e o histograma MACD está positivo.
    3.  **Momentum RSI Favorável**: O RSI de 14 períodos está entre 50 e 75 (indicando momentum de alta, mas não sobrecompra extrema).
    4.  **Volume Significativo**: O volume do candle atual é pelo menos 20% maior que a Média Móvel Simples de 20 períodos do volume.

    Args:
        df_completo (pd.DataFrame): DataFrame contendo preços (close, volume) e
                                    colunas de indicadores calculados (ema_12, ema_26,
                                    ema_200, macd_line, macd_signal, macd_hist,
                                    rsi_14, sma_volume_20). As colunas devem ter os nomes
                                    exatos conforme listado.

    Returns:
        bool: True se um sinal de compra for identificado, False caso contrário.
              Retorna False também em caso de colunas faltantes ou dados insuficientes.
    """
    colunas_necessarias = [
        'close', 'volume', 'ema_12', 'ema_26', 'ema_200',
        'macd_line', 'macd_signal', 'macd_hist', 'rsi_14', 'sma_volume_20'
    ]

    try:
        # Validação inicial: verificar se todas as colunas necessárias existem
        for col in colunas_necessarias:
            if col not in df_completo.columns:
                # Idealmente, isso seria logado em um sistema de produção.
                # print(f"Aviso em verificar_sinal_de_compra: Coluna '{col}' não encontrada.")
                raise KeyError(f"Coluna '{col}' não encontrada no DataFrame.")

        # Validação inicial: DataFrame deve ter pelo menos 2 linhas para permitir a verificação de cruzamentos
        if len(df_completo) < 2:
            return False

        # Seleciona os dados do candle atual (última linha) e do candle anterior (penúltima linha)
        atual = df_completo.iloc[-1]
        anterior = df_completo.iloc[-2]

        # Condição 1: Tendência Principal de Alta
        # O preço de fechamento atual deve ser maior que a EMA de 200 períodos.
        cond_tendencia = atual['close'] > atual['ema_200']

        # Condição 2: Sinal de Entrada Primário (Cruzamento de EMAs OU Cruzamento de MACD)
        # a. Cruzamento de EMAs: EMA curta (12) cruza acima da EMA longa (26).
        ema_cross_compra = (atual['ema_12'] > atual['ema_26']) and \
                           (anterior['ema_12'] < anterior['ema_26'])
        
        # b. Cruzamento de MACD: Linha MACD cruza acima da Linha de Sinal, com histograma positivo.
        #    Histograma positivo (atual['macd_hist'] > 0) confirma a força do movimento de alta.
        macd_cross_compra = (atual['macd_line'] > atual['macd_signal']) and \
                            (anterior['macd_line'] < anterior['macd_signal']) and \
                            (atual['macd_hist'] > 0)
        
        cond_sinal_primario = ema_cross_compra or macd_cross_compra

        # Condição 3: Momentum RSI Favorável
        # RSI (14) deve estar entre o limite inferior e superior definidos para compra.
        # Isso sugere que há momentum de alta, mas o ativo ainda não está excessivamente sobrecomprado.
        cond_rsi = (atual['rsi_14'] > config.RSI_LIMITE_INFERIOR_COMPRA) and \
                   (atual['rsi_14'] < config.RSI_LIMITE_SUPERIOR_COMPRA)

        # Condição 4: Volume Significativo
        # O volume do candle atual deve ser maior que a SMA do volume (20 períodos) multiplicada por um fator.
        # Isso indica que o movimento de preço é suportado por um volume de negociação robusto.
        # Verifica se sma_volume_20 é válido antes de usar.
        if pd.isna(atual['sma_volume_20']) or atual['sma_volume_20'] is None or atual['sma_volume_20'] == 0:
            cond_volume = False # Não pode avaliar se SMA do volume é inválido ou zero (para evitar divisão por zero implícita ou lógica falha)
        else:
            cond_volume = atual['volume'] >= (config.FATOR_AUMENTO_VOLUME * atual['sma_volume_20'])

        # Resultado Final: Todas as condições devem ser verdadeiras para um sinal de compra.
        sinal_compra = cond_tendencia and cond_sinal_primario and cond_rsi and cond_volume
        
        return sinal_compra

    except KeyError as e:
        # Este print pode ser substituído por logging em um ambiente de produção.
        print(f"Aviso em verificar_sinal_de_compra (KeyError): {e}")
        return False
    except Exception as e:
        # Captura genérica para outros erros inesperados durante a lógica.
        print(f"Erro inesperado em verificar_sinal_de_compra: {e}")
        return False

def verificar_sinal_de_venda(df_completo: pd.DataFrame) -> bool:
    """
    Verifica se há um sinal de venda com base nos indicadores técnicos do DataFrame.

    Um sinal de venda é considerado válido se todas as seguintes condições forem atendidas:
    1.  **Tendência Principal de Baixa**: O preço de fechamento atual está abaixo da Média Móvel Exponencial de 200 períodos (EMA 200).
    2.  **Sinal de Saída/Venda Primário**:
        a.  **Cruzamento de EMAs**: A EMA de 12 períodos cruza abaixo da EMA de 26 períodos.
        OU
        b.  **Cruzamento de MACD**: A linha MACD cruza abaixo da linha de Sinal MACD, e o histograma MACD está negativo.
    3.  **Momentum RSI Favorável para Venda**: O RSI de 14 períodos está entre 25 e 50 (indicando momentum de baixa, mas não sobrevenda extrema).
    4.  **Volume Significativo**: O volume do candle atual é pelo menos 20% maior que a Média Móvel Simples de 20 períodos do volume.

    Args:
        df_completo (pd.DataFrame): DataFrame contendo preços (close, volume) e
                                    colunas de indicadores calculados (ema_12, ema_26,
                                    ema_200, macd_line, macd_signal, macd_hist,
                                    rsi_14, sma_volume_20).

    Returns:
        bool: True se um sinal de venda for identificado, False caso contrário.
              Retorna False também em caso de colunas faltantes ou dados insuficientes.
    """
    colunas_necessarias = [
        'close', 'volume', 'ema_12', 'ema_26', 'ema_200',
        'macd_line', 'macd_signal', 'macd_hist', 'rsi_14', 'sma_volume_20'
    ]

    try:
        # Validação inicial: verificar se todas as colunas necessárias existem
        for col in colunas_necessarias:
            if col not in df_completo.columns:
                # print(f"Aviso em verificar_sinal_de_venda: Coluna '{col}' não encontrada.")
                raise KeyError(f"Coluna '{col}' não encontrada no DataFrame.")

        # Validação inicial: DataFrame deve ter pelo menos 2 linhas para cruzamentos
        if len(df_completo) < 2:
            return False

        # Seleciona os dados do candle atual (última linha) e do candle anterior (penúltima linha)
        atual = df_completo.iloc[-1]
        anterior = df_completo.iloc[-2]

        # Condição 1: Filtro de Tendência Principal para Venda
        # O preço de fechamento atual deve ser menor que a EMA de 200 períodos.
        cond_tendencia = atual['close'] < atual['ema_200']

        # Condição 2: Sinal de Saída/Venda Primário (Cruzamento de EMAs OU Cruzamento de MACD)
        # a. Cruzamento de EMAs: EMA curta (12) cruza abaixo da EMA longa (26).
        ema_cross_venda = (atual['ema_12'] < atual['ema_26']) and \
                          (anterior['ema_12'] > anterior['ema_26'])
        
        # b. Cruzamento de MACD: Linha MACD cruza abaixo da Linha de Sinal, com histograma negativo.
        #    Histograma negativo (atual['macd_hist'] < 0) confirma a força do movimento de baixa.
        macd_cross_venda = (atual['macd_line'] < atual['macd_signal']) and \
                           (anterior['macd_line'] > anterior['macd_signal']) and \
                           (atual['macd_hist'] < 0)
        
        cond_sinal_primario = ema_cross_venda or macd_cross_venda

        # Condição 3: Momentum RSI Favorável para Venda
        # RSI (14) deve estar entre o limite inferior e superior definidos para venda.
        # Isso sugere que há momentum de baixa, mas o ativo ainda não está excessivamente sobrevendido.
        cond_rsi = (atual['rsi_14'] < config.RSI_LIMITE_SUPERIOR_VENDA) and \
                   (atual['rsi_14'] > config.RSI_LIMITE_INFERIOR_VENDA)

        # Condição 4: Volume Significativo para Venda
        # O volume do candle atual deve ser maior que a SMA do volume (20 períodos) multiplicada por um fator.
        # Verifica se sma_volume_20 é válido.
        if pd.isna(atual['sma_volume_20']) or atual['sma_volume_20'] is None or atual['sma_volume_20'] == 0:
            cond_volume = False
        else:
            cond_volume = atual['volume'] >= (config.FATOR_AUMENTO_VOLUME * atual['sma_volume_20'])

        # Resultado Final: Todas as condições devem ser verdadeiras para um sinal de venda.
        sinal_venda = cond_tendencia and cond_sinal_primario and cond_rsi and cond_volume
        
        return sinal_venda

    except KeyError as e:
        # Este print pode ser substituído por logging.
        print(f"Aviso em verificar_sinal_de_venda (KeyError): {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado em verificar_sinal_de_venda: {e}")
        return False


if __name__ == "__main__":
    # O bloco __main__ é usado para testes unitários das funções de lógica de trading.
    # Estes testes são importantes para garantir que as condições de sinal funcionam como esperado
    # em diferentes cenários de mercado simulados.
    print("Iniciando testes para verificar_sinal_de_compra...")

    # --- Teste 1: Compra Verdadeira (usando EMA cross) ---
    # Simula um cenário onde todas as condições de compra via cruzamento de EMA são atendidas.
    data_compra_verdadeira_ema = {
        'close': [100, 105], 'volume': [1000, 1500],
        'ema_12': [98, 104], 'ema_26': [100, 103],  
        'ema_200': [90, 92],                        
        'macd_line': [-0.5, 0.1], 'macd_signal': [0, 0.2], 
        'macd_hist': [-0.5, -0.1],                   
        'rsi_14': [48, 60],                         
        'sma_volume_20': [1000, 1000]               
    }
    df_teste_compra_verdadeira_ema = pd.DataFrame(data_compra_verdadeira_ema)
    resultado = verificar_sinal_de_compra(df_teste_compra_verdadeira_ema)
    print(f"\nTeste Compra Verdadeira (EMA cross): Esperado=True, Obtido={resultado} -> {'Passou' if resultado else 'Falhou'}")
    assert resultado is True

    # --- Teste 2: Compra Verdadeira (usando MACD cross) ---
    # Simula um cenário onde todas as condições de compra via cruzamento de MACD são atendidas.
    data_compra_verdadeira_macd = {
        'close': [100, 105], 'volume': [1000, 1500],
        'ema_12': [98, 102], 'ema_26': [100, 103],  
        'ema_200': [90, 92],                        
        'macd_line': [-0.5, 0.5], 'macd_signal': [0, 0.2], 
        'macd_hist': [-0.5, 0.3],                   
        'rsi_14': [48, 60],                         
        'sma_volume_20': [1000, 1000]               
    }
    df_teste_compra_verdadeira_macd = pd.DataFrame(data_compra_verdadeira_macd)
    resultado = verificar_sinal_de_compra(df_teste_compra_verdadeira_macd)
    print(f"Teste Compra Verdadeira (MACD cross): Esperado=True, Obtido={resultado} -> {'Passou' if resultado else 'Falhou'}")
    assert resultado is True

    # Testes subsequentes simulam falhas em cada uma das condições para garantir robustez.
    # ... (outros testes de compra) ...

    # --- Teste 3: Compra Falsa (Tendência Principal Falha) ---
    data_compra_falsa_tendencia = {
        'close': [100, 105], 'volume': [1000, 1500],
        'ema_12': [98, 104], 'ema_26': [100, 103],
        'ema_200': [110, 112], # Preço ABAIXO da EMA 200
        'macd_line': [-0.5, 0.5], 'macd_signal': [0, 0.2],
        'macd_hist': [-0.5, 0.3],
        'rsi_14': [48, 60],
        'sma_volume_20': [1000, 1000]
    }
    df_teste_compra_falsa_tendencia = pd.DataFrame(data_compra_falsa_tendencia)
    resultado = verificar_sinal_de_compra(df_teste_compra_falsa_tendencia)
    print(f"Teste Compra Falsa (Tendência): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    # --- Teste 4: Compra Falsa (RSI Falha - abaixo de 50) ---
    data_compra_falsa_rsi_baixo = data_compra_verdadeira_macd.copy()
    data_compra_falsa_rsi_baixo['rsi_14'] = [30, config.RSI_LIMITE_INFERIOR_COMPRA - 5] # RSI abaixo do limite inferior
    df_teste_compra_falsa_rsi_baixo = pd.DataFrame(data_compra_falsa_rsi_baixo)
    resultado = verificar_sinal_de_compra(df_teste_compra_falsa_rsi_baixo)
    print(f"Teste Compra Falsa (RSI < {config.RSI_LIMITE_INFERIOR_COMPRA}): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    # --- Teste 5: Compra Falsa (RSI Falha - acima de 75) ---
    data_compra_falsa_rsi_alto = data_compra_verdadeira_macd.copy()
    data_compra_falsa_rsi_alto['rsi_14'] = [70, config.RSI_LIMITE_SUPERIOR_COMPRA + 5] # RSI acima do limite superior
    df_teste_compra_falsa_rsi_alto = pd.DataFrame(data_compra_falsa_rsi_alto)
    resultado = verificar_sinal_de_compra(df_teste_compra_falsa_rsi_alto)
    print(f"Teste Compra Falsa (RSI > {config.RSI_LIMITE_SUPERIOR_COMPRA}): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    # --- Teste 6: Compra Falsa (Volume Falha) ---
    data_compra_falsa_volume = data_compra_verdadeira_macd.copy()
    data_compra_falsa_volume['volume'] = [1000, int(1.1 * 1000)] # Volume não atinge o fator de config.FATOR_AUMENTO_VOLUME
    df_teste_compra_falsa_volume = pd.DataFrame(data_compra_falsa_volume)
    resultado = verificar_sinal_de_compra(df_teste_compra_falsa_volume)
    print(f"Teste Compra Falsa (Volume): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False
    
    # --- Teste 7: Compra Falsa (Sinal Primário Falha - Sem Cruzamentos) ---
    data_compra_falsa_sinal_primario = {
        'close': [100, 105], 'volume': [1000, 1500],
        'ema_12': [98, 102], 'ema_26': [100, 103],  # Sem cruzamento EMA
        'ema_200': [90, 92], # Tendencia OK
        'macd_line': [-0.5, 0.1], 'macd_signal': [0, 0.2], # Sem cruzamento MACD
        'macd_hist': [-0.5, -0.1], # Histograma MACD não positivo
        'rsi_14': [48, 60], # RSI OK
        'sma_volume_20': [1000, 1000] # Volume OK
    }
    df_teste_compra_falsa_sinal_primario = pd.DataFrame(data_compra_falsa_sinal_primario)
    resultado = verificar_sinal_de_compra(df_teste_compra_falsa_sinal_primario)
    print(f"Teste Compra Falsa (Sinal Primário): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    # --- Teste 8: DataFrame com menos de 2 linhas ---
    df_menos_2_linhas = pd.DataFrame({'close': [100]}, columns=data_compra_verdadeira_ema.keys())
    resultado = verificar_sinal_de_compra(df_menos_2_linhas)
    print(f"Teste DataFrame < 2 linhas: Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    # --- Teste 9: DataFrame com coluna faltando ---
    df_coluna_faltando = df_teste_compra_verdadeira_ema.drop(columns=['ema_200'])
    resultado = verificar_sinal_de_compra(df_coluna_faltando)
    print(f"Teste Coluna Faltando (ema_200): Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False
    
    # --- Teste 10: SMA Volume é NaN ---
    data_sma_nan = data_compra_verdadeira_macd.copy()
    data_sma_nan['sma_volume_20'] = [1000, pd.NA]
    df_sma_nan = pd.DataFrame(data_sma_nan)
    resultado = verificar_sinal_de_compra(df_sma_nan)
    print(f"Teste SMA Volume NaN: Esperado=False, Obtido={resultado} -> {'Passou' if not resultado else 'Falhou'}")
    assert resultado is False

    print("\nTodos os testes unitários de COMPRA concluídos.")

    print("\n\nIniciando testes para verificar_sinal_de_venda...")

    # --- Teste V1: Venda Verdadeira (usando EMA cross) ---
    # Simula um cenário onde todas as condições de venda via cruzamento de EMA são atendidas.
    data_venda_verdadeira_ema = {
        'close': [105, 100], 'volume': [1000, 1500],
        'ema_12': [107, 102], 'ema_26': [105, 103], 
        'ema_200': [110, 108],                     
        'macd_line': [0.5, -0.1], 'macd_signal': [0.2, 0], 
        'macd_hist': [0.3, -0.1],                  
        'rsi_14': [52, 40],                        
        'sma_volume_20': [1000, 1000]              
    }
    df_teste_venda_verdadeira_ema = pd.DataFrame(data_venda_verdadeira_ema)
    resultado_venda = verificar_sinal_de_venda(df_teste_venda_verdadeira_ema)
    print(f"\nTeste Venda Verdadeira (EMA cross): Esperado=True, Obtido={resultado_venda} -> {'Passou' if resultado_venda else 'Falhou'}")
    assert resultado_venda is True

    # --- Teste V2: Venda Verdadeira (usando MACD cross) ---
    # Simula um cenário onde todas as condições de venda via cruzamento de MACD são atendidas.
    data_venda_verdadeira_macd = {
        'close': [105, 100], 'volume': [1000, 1500],
        'ema_12': [107, 104], 'ema_26': [105, 103],  
        'ema_200': [110, 108],                      
        'macd_line': [0.5, -0.5], 'macd_signal': [0.2, 0], 
        'macd_hist': [0.3, -0.5],                   
        'rsi_14': [52, 40],                         
        'sma_volume_20': [1000, 1000]               
    }
    df_teste_venda_verdadeira_macd = pd.DataFrame(data_venda_verdadeira_macd)
    resultado_venda = verificar_sinal_de_venda(df_teste_venda_verdadeira_macd)
    print(f"Teste Venda Verdadeira (MACD cross): Esperado=True, Obtido={resultado_venda} -> {'Passou' if resultado_venda else 'Falhou'}")
    assert resultado_venda is True
    
    # ... (outros testes de venda) ...

    # --- Teste V3: Venda Falsa (Tendência Principal Falha - close >= ema_200) ---
    data_venda_falsa_tendencia = data_venda_verdadeira_ema.copy()
    data_venda_falsa_tendencia['ema_200'] = [90, 95] # Preço (100) NÃO está abaixo da EMA 200 (95) -> FALHA
    df_teste_venda_falsa_tendencia = pd.DataFrame(data_venda_falsa_tendencia)
    resultado_venda = verificar_sinal_de_venda(df_teste_venda_falsa_tendencia)
    print(f"Teste Venda Falsa (Tendência): Esperado=False, Obtido={resultado_venda} -> {'Passou' if not resultado_venda else 'Falhou'}")
    assert resultado_venda is False

    # --- Teste V4: Venda Falsa (RSI Falha - RSI > 50) ---
    data_venda_falsa_rsi_alto = data_venda_verdadeira_ema.copy()
    data_venda_falsa_rsi_alto['rsi_14'] = [60, config.RSI_LIMITE_SUPERIOR_VENDA + 5] # RSI acima do limite superior de venda
    df_teste_venda_falsa_rsi_alto = pd.DataFrame(data_venda_falsa_rsi_alto)
    resultado_venda = verificar_sinal_de_venda(df_teste_venda_falsa_rsi_alto)
    print(f"Teste Venda Falsa (RSI > {config.RSI_LIMITE_SUPERIOR_VENDA}): Esperado=False, Obtido={resultado_venda} -> {'Passou' if not resultado_venda else 'Falhou'}")
    assert resultado_venda is False

    # --- Teste V5: Venda Falsa (RSI Falha - RSI < 25) ---
    data_venda_falsa_rsi_baixo = data_venda_verdadeira_ema.copy()
    data_venda_falsa_rsi_baixo['rsi_14'] = [30, config.RSI_LIMITE_INFERIOR_VENDA - 5] # RSI abaixo do limite inferior de venda
    df_teste_venda_falsa_rsi_baixo = pd.DataFrame(data_venda_falsa_rsi_baixo)
    resultado_venda = verificar_sinal_de_venda(df_teste_venda_falsa_rsi_baixo)
    print(f"Teste Venda Falsa (RSI < {config.RSI_LIMITE_INFERIOR_VENDA}): Esperado=False, Obtido={resultado_venda} -> {'Passou' if not resultado_venda else 'Falhou'}")
    assert resultado_venda is False
    
    print("\nTodos os testes de Venda concluídos.")
