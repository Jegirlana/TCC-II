@echo off
chcp 65001 >nul
echo ==========================================
echo   EXCESSIVE LOGS ANALYZER + PUTER
echo   Claude ^& ChatGPT via Puter (GRATUITO)
echo ==========================================
echo.

if not exist "venv\" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Execute: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

REM Verifica se Puter Bridge esta rodando
curl -s http://localhost:3000/health >nul 2>&1
if %errorlevel%==0 (
    echo Puter Bridge ja esta rodando
    goto run_analysis
)

echo Iniciando Puter Bridge em background...

if not exist "puter-bridge\.env" (
    echo Primeira execucao detectada!
    echo Abrindo navegador para autenticacao Puter...
    echo.
    cd puter-bridge
    npm run auth
    cd ..
    echo.
)

if not exist "puter-bridge\.env" (
    echo ERRO: Autenticacao Puter falhou. Execute manualmente:
    echo   cd puter-bridge ^&^& npm run auth
    exit /b 1
)

cd puter-bridge
start /b npm start > ..\puter-bridge.log 2>&1
cd ..

echo Aguardando Puter Bridge iniciar...
timeout /t 5 /nobreak >nul

curl -s http://localhost:3000/health >nul 2>&1
if not %errorlevel%==0 (
    echo ERRO ao iniciar Puter Bridge. Verifique puter-bridge.log
    exit /b 1
)
echo Puter Bridge iniciado com sucesso

:run_analysis
echo.

set LOG_FILE=%1
if "%LOG_FILE%"=="" set LOG_FILE=dataset\synthetic_logs.json

if not exist "%LOG_FILE%" (
    echo ERRO: Arquivo de logs nao encontrado: %LOG_FILE%
    exit /b 1
)

echo Arquivo de entrada: %LOG_FILE%
echo Relatorios serao salvos em: reports\
echo Usando Claude ^& ChatGPT via Puter (GRATUITO)
echo.

if not "%2"=="" (
    venv\Scripts\python.exe src\main.py "%LOG_FILE%" -o "%2"
) else (
    venv\Scripts\python.exe src\main.py "%LOG_FILE%"
)

set EXIT_CODE=%errorlevel%

echo.
echo ==========================================
if %EXIT_CODE%==0 (
    echo Analise concluida!
    echo Verifique os relatorios em reports\
) else (
    echo Analise finalizada com avisos
)
echo.
echo Puter Bridge continua rodando em background
echo Para parar: execute stop_puter.bat
echo Para ver logs: puter-bridge.log
echo ==========================================

exit /b %EXIT_CODE%
