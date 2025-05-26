"""
Ponto de Entrada Principal do Robô de Trading.

Este módulo é responsável por orquestrar o funcionamento do robô de trading.
Ele inicializa o loop principal que busca dados de mercado, calcula indicadores,
aplica a lógica de trading para tomar decisões de compra/venda e gerencia
o ciclo de operações em intervalos regulares.
"""
from api_mercado_bitcoin import buscar_candles_horarios
from indicadores import calcular_ema, calcular_macd, calcular_rsi, calcular_sma_volume
from logica_trading import verificar_sinal_de_compra, verificar_sinal_de_venda
import pandas as pd
import time
from datetime import datetime, timedelta
import config # Importar o módulo de configuração
import logging

# Configuração do Logging
# Define o nível de log, o formato das mensagens e os handlers (arquivo e console).
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_trades.log", mode='a'), # Salva logs em arquivo, modo 'append'
        logging.StreamHandler() # Imprime logs no console
    ]
)
# logger = logging.getLogger(__name__) # Cria um logger específico para este módulo, se necessário.
                                     # Por enquanto, o logger raiz configurado por basicConfig é usado.

def loop_principal():
    """
    Motor Central do Robô de Trading.

    Esta função executa um loop infinito que constitui o ciclo de vida operacional do robô.
    A cada iteração, o robô:
    1. Busca os dados mais recentes de candles do mercado.
    2. Calcula os indicadores técnicos necessários para a estratégia.
    3. Aplica a lógica de trading para verificar sinais de compra ou venda.
    4. Simula ordens de compra/venda com base nos sinais.
    5. Gerencia o estado da posição (aberta/fechada) e o preço de compra.
    6. Aguarda até o próximo candle para repetir o ciclo.
    A função também inclui tratamento de exceções para robustez.
    """
    tem_posicao_aberta = False  # Flag para controlar se uma posição está atualmente aberta
    preco_compra = 0.0          # Preço de compra da posição aberta
    # timestamp_compra = None   # Poderia ser usado para registrar o momento da compra

    logging.info("Robô de Trading Iniciando...")
    logging.info("="*50)
    logging.info("Configurações Carregadas:")
    logging.info(f"- Símbolo: {config.SIMBOLO_TRADING}")
    logging.info(f"- Resolução/Timeframe: {config.RESOLUCAO_CANDLES}")
    logging.info(f"- Indicadores: EMA({config.EMA_PERIODO_CURTO}, {config.EMA_PERIODO_LONGO}, {config.EMA_PERIODO_TENDENCIA}), "
                 f"MACD({config.MACD_PERIODO_RAPIDO},{config.MACD_PERIODO_LENTO},{config.MACD_PERIODO_SINAL}), "
                 f"RSI({config.RSI_PERIODO}), SMA Volume({config.SMA_VOLUME_PERIODO})")
    logging.info(f"- Fator Aumento Volume: {config.FATOR_AUMENTO_VOLUME}")
    logging.info(f"- RSI Compra (Inferior/Superior): {config.RSI_LIMITE_INFERIOR_COMPRA} / {config.RSI_LIMITE_SUPERIOR_COMPRA}")
    logging.info(f"- RSI Venda (Inferior/Superior): {config.RSI_LIMITE_INFERIOR_VENDA} / {config.RSI_LIMITE_SUPERIOR_VENDA}")
    logging.info(f"- Candles a buscar na API: {config.NUM_CANDLES_BUSCAR}")
    logging.info("Estratégia de Compra Detalhada:")
    logging.info(f"  1. Preço de Fechamento > EMA({config.EMA_PERIODO_TENDENCIA})")
    logging.info(f"  2. EMA({config.EMA_PERIODO_CURTO}) cruza EMA({config.EMA_PERIODO_LONGO}) para cima OU ")
    logging.info(f"     (Linha MACD({config.MACD_PERIODO_RAPIDO},{config.MACD_PERIODO_LENTO}) cruza Linha de Sinal({config.MACD_PERIODO_SINAL}) para cima E Histograma MACD > 0)")
    logging.info(f"  3. RSI({config.RSI_PERIODO}) entre {config.RSI_LIMITE_INFERIOR_COMPRA} e {config.RSI_LIMITE_SUPERIOR_COMPRA}")
    logging.info(f"  4. Volume >= {config.FATOR_AUMENTO_VOLUME} * SMA Volume({config.SMA_VOLUME_PERIODO})")
    logging.info("Estratégia de Venda Detalhada:")
    logging.info(f"  1. Preço de Fechamento < EMA({config.EMA_PERIODO_TENDENCIA})")
    logging.info(f"  2. EMA({config.EMA_PERIODO_CURTO}) cruza EMA({config.EMA_PERIODO_LONGO}) para baixo OU ")
    logging.info(f"     (Linha MACD({config.MACD_PERIODO_RAPIDO},{config.MACD_PERIODO_LENTO}) cruza Linha de Sinal({config.MACD_PERIODO_SINAL}) para baixo E Histograma MACD < 0)")
    logging.info(f"  3. RSI({config.RSI_PERIODO}) entre {config.RSI_LIMITE_INFERIOR_VENDA} e {config.RSI_LIMITE_SUPERIOR_VENDA}")
    logging.info(f"  4. Volume >= {config.FATOR_Aumento_VOLUME} * SMA Volume({config.SMA_VOLUME_PERIODO})")
    logging.info("="*50)

    while True:
        try:
            logging.info("Nova iteração do loop principal...")

            # ## BUSCAR DADOS DE MERCADO ##
            logging.info(f"Buscando {config.NUM_CANDLES_BUSCAR} candles ({config.RESOLUCAO_CANDLES}) para {config.SIMBOLO_TRADING}...")
            df_candles = buscar_candles_horarios(
                simbolo=config.SIMBOLO_TRADING, 
                resolucao=config.RESOLUCAO_CANDLES, 
                limit=config.NUM_CANDLES_BUSCAR
            )

            # Validação primária dos dados recebidos da API
            # É necessário um número mínimo de candles para calcular todos os indicadores (especialmente EMA longa)
            min_candles_necessarios = config.EMA_PERIODO_TENDENCIA + 50 # Margem para aquecimento de outros indicadores
            if df_candles.empty or len(df_candles) < min_candles_necessarios:
                logging.warning(f"Dados insuficientes ({len(df_candles)} de {min_candles_necessarios} necessários) ou erro ao buscar candles. Tentando novamente em 1 minuto.")
                time.sleep(60) # Aguarda 1 minuto antes de tentar novamente
                continue # Pula para a próxima iteração

            logging.info(f"Dados recebidos: {len(df_candles)} candles, do {df_candles.iloc[0]['timestamp']} ao {df_candles.iloc[-1]['timestamp']}")

            # ## CALCULAR INDICADORES TÉCNICOS ##
            logging.info("Calculando indicadores técnicos...")
            df_candles['ema_12'] = calcular_ema(df_candles['close'], config.EMA_PERIODO_CURTO)
            df_candles['ema_26'] = calcular_ema(df_candles['close'], config.EMA_PERIODO_LONGO)
            df_candles['ema_200'] = calcular_ema(df_candles['close'], config.EMA_PERIODO_TENDENCIA)
            df_candles['macd_line'], df_candles['macd_signal'], df_candles['macd_hist'] = calcular_macd(
                df_candles['close'], 
                window_fast=config.MACD_PERIODO_RAPIDO, 
                window_slow=config.MACD_PERIODO_LENTO, 
                window_sign=config.MACD_PERIODO_SINAL
            )
            # O nome da coluna é mantido como 'rsi_14' por compatibilidade com a lógica de trading,
            # mas o período é configurável via config.RSI_PERIODO.
            df_candles['rsi_14'] = calcular_rsi(df_candles['close'], config.RSI_PERIODO)
            # Similarmente para 'sma_volume_20'.
            df_candles['sma_volume_20'] = calcular_sma_volume(df_candles['volume'], config.SMA_VOLUME_PERIODO)

            # Remove linhas com NaN resultantes do cálculo de indicadores (período de aquecimento)
            df_analise = df_candles.dropna().copy()

            # Validação secundária: após remover NaNs, ainda há dados suficientes para análise?
            # A lógica de trading requer pelo menos 2 linhas para verificar cruzamentos.
            if df_analise.empty or len(df_analise) < 2: 
                logging.warning("Dados insuficientes após cálculo de indicadores e remoção de NaNs. Tentando novamente em 1 minuto.")
                time.sleep(60)
                continue
            
            logging.info(f"Último candle processado (com indicadores): {df_analise.iloc[-1]['timestamp']} (Close: {df_analise.iloc[-1]['close']})")

            # ## LÓGICA DE DECISÃO DE TRADING ##
            if not tem_posicao_aberta:
                logging.info("Verificando sinal de COMPRA...")
                sinal_compra = verificar_sinal_de_compra(df_analise)
                if sinal_compra:
                    tem_posicao_aberta = True
                    preco_compra = df_analise.iloc[-1]['close']
                    timestamp_compra = df_analise.iloc[-1]['timestamp']
                    logging.info("="*30)
                    logging.info(f"*** SINAL DE COMPRA DETECTADO E POSIÇÃO ABERTA ***")
                    logging.info(f"ORDEM DE COMPRA (simulada): {config.SIMBOLO_TRADING} em {preco_compra:.2f} no candle de {timestamp_compra}")
                    logging.info("="*30)
                else:
                    logging.info("Nenhum sinal de compra identificado. Aguardando...")
            else: # Se tem_posicao_aberta is True
                logging.info(f"Posição ABERTA. Preço de compra: {preco_compra:.2f}. Verificando sinal de VENDA...")
                sinal_venda = verificar_sinal_de_venda(df_analise)
                if sinal_venda:
                    preco_venda = df_analise.iloc[-1]['close']
                    timestamp_venda = df_analise.iloc[-1]['timestamp']
                    resultado_op = ((preco_venda - preco_compra) / preco_compra) * 100 if preco_compra > 0 else 0
                    logging.info("="*30)
                    logging.info(f"*** SINAL DE VENDA DETECTADO E POSIÇÃO FECHADA ***")
                    logging.info(f"ORDEM DE VENDA (simulada): {config.SIMBOLO_TRADING} em {preco_venda:.2f} no candle de {timestamp_venda}. Resultado: {resultado_op:.2f}%")
                    logging.info("="*30)
                    tem_posicao_aberta = False
                    preco_compra = 0.0
                else:
                    logging.info(f"Mantendo posição comprada. Preço atual ({config.SIMBOLO_TRADING}): {df_analise.iloc[-1]['close']:.2f}. Preço de compra: {preco_compra:.2f}")

            # ## AGUARDAR PRÓXIMO CANDLE ##
            agora = datetime.now()
            # Calcula o início da próxima hora e adiciona um pequeno buffer (1 minuto)
            # para garantir que o novo candle horário já esteja disponível na API ao buscar.
            proxima_hora = (agora + timedelta(hours=1)).replace(minute=1, second=0, microsecond=0) 
            
            tempo_espera_segundos = (proxima_hora - agora).total_seconds()

            # Se, por algum motivo (ex: processamento muito longo), o tempo de espera calculado for negativo,
            # ajusta para esperar até a hora seguinte ou um mínimo de 60 segundos.
            if tempo_espera_segundos < 0: 
                logging.warning(f"Tempo de espera calculado ({tempo_espera_segundos:.0f}s) é negativo. Ajustando para a próxima hora.")
                proxima_hora = (agora + timedelta(hours=2)).replace(minute=1, second=0, microsecond=0) # Tenta a hora seguinte
                tempo_espera_segundos = (proxima_hora - agora).total_seconds()
                if tempo_espera_segundos < 0: # Se ainda for negativo (improvável), usa um fallback.
                    logging.warning(f"Tempo de espera ainda negativo ({tempo_espera_segundos:.0f}s) após ajuste. Usando fallback de 60s.")
                    tempo_espera_segundos = 60 

            logging.info(f"Aguardando {tempo_espera_segundos:.0f} segundos até a próxima vela ({proxima_hora.strftime('%Y-%m-%d %H:%M:%S')})...")
            time.sleep(tempo_espera_segundos)

        except requests.exceptions.RequestException as re:
            logging.error(f"Erro de conexão com a API: {re}. Tentando novamente em 1 minuto.")
            time.sleep(60)
        except pd.errors.EmptyDataError as ede: # Pode ocorrer se a API retornar resposta vazia inesperada
            logging.error(f"Erro de dados vazios no Pandas (EmptyDataError): {ede}. Pode ser um problema com a resposta da API. Tentando novamente em 1 minuto.")
            time.sleep(60)
        except KeyError as ke: # Erro comum se a estrutura dos dados mudar ou uma coluna esperada faltar
            logging.error(f"Erro de chave (KeyError) nos dados do DataFrame: {ke}. Verifique os nomes das colunas e a integridade dos dados. Tentando novamente em 1 minuto.")
            time.sleep(60)
        except Exception as e: # Captura qualquer outra exceção não prevista
            logging.exception(f"Ocorreu um erro inesperado na iteração do loop principal: {e}")
            logging.info("Tentando novamente em 5 minutos devido a erro inesperado...")
            time.sleep(300) # Espera mais longa para erros desconhecidos


if __name__ == "__main__":
    # Importa 'requests.exceptions' para que o bloco 'except' no loop principal possa usá-lo.
    # 'traceback' não é mais importado diretamente aqui, pois 'logging.exception()' já lida com o traceback.
    import requests.exceptions 

    try:
        loop_principal()
    except KeyboardInterrupt: # Permite que o usuário pare o robô com Ctrl+C
        logging.info("Robô interrompido pelo usuário (KeyboardInterrupt). Finalizando...")
    except Exception as e:
        # Este bloco captura exceções que podem ocorrer fora do loop 'while True' em 'loop_principal',
        # ou durante a inicialização do próprio 'loop_principal' antes que seu try-except interno seja ativado.
        logging.exception(f"Ocorreu um erro fatal fora do loop principal do robô: {e}")
    finally:
        logging.info("Robô finalizado.")
