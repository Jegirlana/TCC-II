@echo off
chcp 65001 >nul
echo ==========================================
echo   EXCESSIVE LOGS ANALYZER - Interface Web
echo ==========================================
echo.

if not exist "venv\" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Execute: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

venv\Scripts\python.exe -c "import streamlit" >nul 2>&1
if not %errorlevel%==0 (
    echo Instalando Streamlit...
    venv\Scripts\pip.exe install streamlit --quiet
)

echo Iniciando interface web...
echo   Acesse em: http://127.0.0.1:8501
echo   Para encerrar: Ctrl+C
echo.

venv\Scripts\streamlit.exe run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
