@echo off
chcp 65001 >nul
echo ==========================================
echo   EXCESSIVE LOGS ANALYZER
echo   Analise Completa: Claude + ChatGPT + Standard
echo ==========================================
echo.

if not exist "venv\" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Execute: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

if not exist ".env" (
    echo AVISO: Arquivo .env nao encontrado.
    echo As analises com IA podem falhar sem API keys.
    echo.
)

set LOG_FILE=%1
if "%LOG_FILE%"=="" set LOG_FILE=dataset\synthetic_logs.json

if not exist "%LOG_FILE%" (
    echo ERRO: Arquivo de logs nao encontrado: %LOG_FILE%
    exit /b 1
)

echo Arquivo de entrada: %LOG_FILE%
echo Relatorios serao salvos em: reports\
echo.

if not "%2"=="" (
    venv\Scripts\python.exe src\main.py "%LOG_FILE%" -o "%2"
) else (
    venv\Scripts\python.exe src\main.py "%LOG_FILE%"
)

echo.
echo ==========================================
echo Analise concluida!
echo Verifique os relatorios em reports\
echo ==========================================
