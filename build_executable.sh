#!/bin/bash
echo "Iniciando o build do TradingBotBTCBRL para Linux/macOS..."
# Ativa o ambiente virtual se existir e não estiver ativo
if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "Ativando ambiente virtual localmente para este script..."
    source venv/bin/activate
elif [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "AVISO: Ambiente virtual 'venv' não encontrado e nenhum ambiente virtual global ativo."
    echo "Continuando com o Python global/ambiente atual. Certifique-se de que pyinstaller está instalado."
fi
echo "Instalando/atualizando dependências (incluindo pyinstaller)..."
pip install -r requirements.txt
echo "Executando PyInstaller..."
python -m PyInstaller --name TradingBotBTCBRL --clean main.py
echo "Build concluído. Verifique as pastas 'dist' e 'build'."
echo "O executável principal estará em 'dist/TradingBotBTCBRL/' (ou similar)."
