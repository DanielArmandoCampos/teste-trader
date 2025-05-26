@echo off
echo Iniciando o build do TradingBotBTCBRL para Windows...
REM Ativa o ambiente virtual se existir
IF EXIST "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual localmente para este script...
    call venv\Scripts\activate.bat
) ELSE (
    echo AVISO: Ambiente virtual 'venv' nao encontrado.
    echo Continuando com o Python global/ambiente atual. Certifique-se de que pyinstaller esta instalado.
)
echo Instalando/atualizando dependencias (incluindo pyinstaller)...
pip install -r requirements.txt
echo Executando PyInstaller...
python -m PyInstaller --name TradingBotBTCBRL --clean main.py
echo Build concluido. Verifique as pastas 'dist' e 'build'.
echo O executavel principal estara em 'dist\TradingBotBTCBRL' (ou similar).
pause
