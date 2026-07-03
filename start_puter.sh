#!/bin/bash
# Script para iniciar o Puter Bridge facilmente

echo "=========================================="
echo "  PUTER BRIDGE - ChatGPT Gratuito"
echo "=========================================="
echo ""

cd "$(dirname "$0")/puter-bridge"

# Verifica se já está autenticado
if [ ! -f ".env" ]; then
    echo "⚠️  Primeira execução detectada!"
    echo "📱 Abrindo navegador para autenticação..."
    echo ""
    npm run auth
    echo ""
fi

# Verifica se a autenticação foi bem-sucedida
if [ ! -f ".env" ]; then
    echo "❌ Autenticação falhou. Execute manualmente:"
    echo "   cd puter-bridge && npm run auth"
    exit 1
fi

echo "🚀 Iniciando Puter Bridge..."
echo "📡 Servidor rodará em: http://localhost:3000"
echo ""
echo "💡 Para parar: Ctrl+C"
echo "💡 Para executar em background: Ctrl+Z, depois 'bg'"
echo ""
echo "=========================================="
echo ""

npm start
