#!/bin/bash
# Script para executar a análise completa de logs
# Executa automaticamente Claude AI + ChatGPT + Standard (sem IA)
# Gera relatórios separados na pasta reports/

echo "=========================================="
echo "  EXCESSIVE LOGS ANALYZER"
echo "  Análise Completa: Claude + ChatGPT + Standard"
echo "=========================================="
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado."
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado."
    echo "As análises com IA (Claude/ChatGPT) podem falhar sem API keys."
    echo ""
fi

# Define arquivo de entrada
LOG_FILE="${1:-dataset/synthetic_logs.json}"

# Verifica se o arquivo existe
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Erro: Arquivo de logs não encontrado: $LOG_FILE"
    exit 1
fi

# Executa a análise
echo "📂 Arquivo de entrada: $LOG_FILE"
echo "📁 Relatórios serão salvos em: reports/"
echo ""

if [ -n "$2" ]; then
    venv/bin/python3 src/main.py "$LOG_FILE" -o "$2"
else
    venv/bin/python3 src/main.py "$LOG_FILE"
fi

echo ""
echo "=========================================="
echo "✅ Análise concluída!"
echo "📂 Verifique os relatórios em reports/"
echo "=========================================="
