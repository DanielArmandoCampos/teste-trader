# Robô de Trading para Mercado Bitcoin - Guia de Configuração e Execução

Este guia fornece instruções passo a passo para configurar e executar o robô de trading desenvolvido para operar na API V4 do Mercado Bitcoin.

## 1. Pré-requisitos

*   **Python 3.7+**: Certifique-se de ter o Python 3.7 ou uma versão mais recente instalada. Você pode baixar o Python em [python.org](https://www.python.org/downloads/).
*   **Pip**: O gerenciador de pacotes do Python, geralmente instalado automaticamente com o Python.
*   **Git**: Para clonar o repositório (opcional, se você já tiver os arquivos).

## 2. Configuração do Ambiente

### 2.1. Clone o Repositório (Opcional)

Se você ainda não tem os arquivos do projeto, clone o repositório para sua máquina local:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_DIRETORIO_DO_PROJETO>
```

Substitua `<URL_DO_REPOSITORIO>` pela URL correta do repositório e `<NOME_DO_DIRETORIO_DO_PROJETO>` pelo nome da pasta criada.

### 2.2. Crie um Ambiente Virtual (Recomendado)

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto:

```bash
python -m venv venv
```

### 2.3. Ative o Ambiente Virtual

*   **No Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **No macOS e Linux:**
    ```bash
    source venv/bin/activate
    ```
    Você deverá ver `(venv)` no início do prompt do seu terminal, indicando que o ambiente virtual está ativo.

### 2.4. Instale as Dependências

Com o ambiente virtual ativo, instale as bibliotecas Python necessárias listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```
Isso instalará bibliotecas como `requests`, `pandas`, `numpy` e `ta`.

## 3. Configuração do Robô

O comportamento do robô é controlado pelo arquivo `config.py`. Abra este arquivo em um editor de texto e ajuste os parâmetros conforme sua estratégia e preferências.

Principais parâmetros em `config.py`:

*   **Períodos de EMA**: `EMA_PERIODO_CURTO`, `EMA_PERIODO_LONGO`, `EMA_PERIODO_TENDENCIA`
*   **Períodos do MACD**: `MACD_PERIODO_RAPIDO`, `MACD_PERIODO_LENTO`, `MACD_PERIODO_SINAL`
*   **Configurações do RSI**: `RSI_PERIODO`, limites para compra (`RSI_LIMITE_SUPERIOR_COMPRA`, `RSI_LIMITE_INFERIOR_COMPRA`) e venda (`RSI_LIMITE_SUPERIOR_VENDA`, `RSI_LIMITE_INFERIOR_VENDA`).
*   **Configurações de Volume**: `SMA_VOLUME_PERIODO`, `FATOR_AUMENTO_VOLUME`.
*   **Configurações da API e Robô**:
    *   `SIMBOLO_TRADING`: O par de moedas a ser negociado (ex: "BTC-BRL", "ETH-BRL").
    *   `RESOLUCAO_CANDLES`: O timeframe dos candles (ex: "1h", "1d").
    *   `NUM_CANDLES_BUSCAR`: Quantidade de candles para buscar da API. Certifique-se de que é suficiente para o cálculo do indicador mais longo (EMA 200) e o aquecimento dos demais.

**Exemplo:**
Para operar com ETH-BRL em candles de 4 horas:
```python
SIMBOLO_TRADING = "ETH-BRL"
RESOLUCAO_CANDLES = "4h"
```

## 4. Executando o Robô

Após configurar o ambiente e o arquivo `config.py`, você pode executar o robô. Certifique-se de que o ambiente virtual ainda está ativo.

Execute o script principal:

```bash
python main.py
```

O robô começará a operar, exibindo logs no console e salvando-os no arquivo `bot_trades.log` (na mesma pasta do projeto).

## 5. Monitorando o Robô

*   **Console**: Acompanhe as operações em tempo real através das mensagens de log impressas no terminal.
*   **Arquivo de Log (`bot_trades.log`)**: Todas as mensagens de log, incluindo informações de inicialização, busca de dados, cálculo de indicadores, sinais de compra/venda e erros, são salvas neste arquivo. Isso é útil para análise posterior e depuração.

## 6. Parando o Robô

Para parar o robô, pressione `Ctrl+C` no terminal onde ele está sendo executado. O robô foi programado para capturar essa interrupção e finalizar suas operações de forma organizada.

## 7. Testando os Módulos (Opcional)

Os módulos `api_mercado_bitcoin.py`, `indicadores.py`, e `logica_trading.py` contêm blocos `if __name__ == "__main__":` que permitem testar suas funcionalidades de forma isolada. Para executar esses testes:

```bash
python api_mercado_bitcoin.py
python indicadores.py
python logica_trading.py
```
Isso pode ser útil para verificar se cada componente está funcionando como esperado, especialmente após modificações.

## 8. Observações Importantes

*   **Simulação**: Este robô, na forma fornecida, simula ordens de compra e venda. Ele não executa transações reais em uma exchange.
*   **Chaves de API**: Para operar de verdade, seria necessário integrar chamadas à API de negociação da exchange, o que exigiria o uso de chaves de API. **Este robô não implementa essa funcionalidade e não requer chaves de API.**
*   **Gerenciamento de Risco**: Nenhuma estratégia de gerenciamento de risco (como stop-loss ou take-profit) está implementada. Em um ambiente real, isso seria crucial.
*   **Teste em Conta Demonstração**: Antes de usar qualquer robô de trading com dinheiro real, teste-o exaustivamente em uma conta de demonstração (se disponível) ou com valores muito pequenos.
*   **Sem Garantias**: O uso deste software é por sua conta e risco. Não há garantias de lucro, e perdas financeiras podem ocorrer.

---

Boa sorte e boas negociações (simuladas)!
