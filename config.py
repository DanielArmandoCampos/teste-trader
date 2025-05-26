# Arquivo de Configuração para o Robô de Trading
# Este arquivo centraliza todas as variáveis de configuração utilizadas pelo robô,
# facilitando ajustes e manutenibilidade.

# Configurações para Médias Móveis Exponenciais (EMA)
EMA_PERIODO_CURTO = 12      # Período para a EMA rápida
EMA_PERIODO_LONGO = 26      # Período para a EMA lenta
EMA_PERIODO_TENDENCIA = 200 # Período para a EMA de definição de tendência principal

# Configurações para o Moving Average Convergence Divergence (MACD)
MACD_PERIODO_RAPIDO = 12    # Período da EMA rápida do MACD
MACD_PERIODO_LENTO = 26     # Período da EMA lenta do MACD
MACD_PERIODO_SINAL = 9      # Período da EMA de sinal do MACD

# Configurações para o Índice de Força Relativa (RSI)
RSI_PERIODO = 14
RSI_LIMITE_SUPERIOR_COMPRA = 75 # Limite superior do RSI para considerar um sinal de compra (condição: RSI < este valor)
RSI_LIMITE_INFERIOR_COMPRA = 50 # Limite inferior do RSI para considerar um sinal de compra (condição: RSI > este valor)
RSI_LIMITE_SUPERIOR_VENDA = 50  # Limite superior do RSI para considerar um sinal de venda (condição: RSI < este valor)
RSI_LIMITE_INFERIOR_VENDA = 25  # Limite inferior do RSI para considerar um sinal de venda (condição: RSI > este valor)

# Configurações para Análise de Volume
SMA_VOLUME_PERIODO = 20     # Período para a Média Móvel Simples do Volume
FATOR_AUMENTO_VOLUME = 1.2  # Fator pelo qual o volume atual deve superar a SMA do volume

# Configurações da API do Mercado Bitcoin e Parâmetros do Robô
SIMBOLO_TRADING = "BTC-BRL"         # Par de negociação (ex: "BTC-BRL", "ETH-BRL")
RESOLUCAO_CANDLES = "1h"            # Resolução dos candles (ex: "1m", "5m", "1h", "1d")
NUM_CANDLES_BUSCAR = 300            # Número de candles a serem buscados na API.
                                    # Deve ser suficiente para o cálculo do indicador mais longo (EMA 200)
                                    # e para o período de aquecimento dos outros indicadores.
