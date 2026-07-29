@echo off
chcp 65001 >nul
echo ==========================================
echo   PUTER BRIDGE - ChatGPT Gratuito
echo ==========================================
echo.

cd /d "%~dp0puter-bridge"

if not exist ".env" (
    echo Primeira execucao detectada!
    echo Abrindo navegador para autenticacao...
    echo.
    npm run auth
    echo.
)

if not exist ".env" (
    echo ERRO: Autenticacao falhou. Execute manualmente:
    echo   cd puter-bridge ^&^& npm run auth
    exit /b 1
)

echo Iniciando Puter Bridge...
echo Servidor rodara em: http://localhost:3000
echo.
echo Para parar: Ctrl+C
echo.
echo ==========================================
echo.

npm start
