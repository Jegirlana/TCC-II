@echo off
chcp 65001 >nul
echo Parando Puter Bridge...

REM Mata processos node.js rodando o server.js do puter-bridge
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Encerrando processo na porta 3000 (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
    echo Puter Bridge parado
    goto done
)

echo Nenhum processo encontrado na porta 3000

:done
if exist ".puter.pid" del /f ".puter.pid"
