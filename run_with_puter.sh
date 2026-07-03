#!/bin/bash
# Script para executar a análise completa com Puter Bridge automático
# Garante que Claude e ChatGPT sempre usem Puter gratuitamente

echo "=========================================="
echo "  EXCESSIVE LOGS ANALYZER + PUTER"
echo "  Claude & ChatGPT via Puter (GRATUITO)"
echo "=========================================="
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado."
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Função para verificar se Puter Bridge está rodando
check_puter() {
    curl -s http://localhost:3000/health > /dev/null 2>&1
    return $?
}

# Verifica se Puter Bridge já está rodando
if check_puter; then
    echo "✓ Puter Bridge já está rodando"
else
    echo "🚀 Iniciando Puter Bridge em background..."

    # Verifica se já está autenticado
    if [ ! -f "puter-bridge/.env" ]; then
        echo "⚠️  Primeira execução detectada!"
        echo "📱 Abrindo navegador para autenticação Puter..."
        echo ""
        cd puter-bridge
        npm run auth
        cd ..
        echo ""
    fi

    # Verifica se a autenticação foi bem-sucedida
    if [ ! -f "puter-bridge/.env" ]; then
        echo "❌ Autenticação Puter falhou. Execute manualmente:"
        echo "   cd puter-bridge && npm run auth"
        exit 1
    fi

    # Inicia Puter Bridge em background
    cd puter-bridge
    nohup npm start > ../puter-bridge.log 2>&1 &
    PUTER_PID=$!
    cd ..

    # Salva PID para poder parar depois
    echo $PUTER_PID > .puter.pid

    echo "⏳ Aguardando Puter Bridge iniciar..."
    sleep 5

    # Verifica se iniciou corretamente
    if check_puter; then
        echo "✓ Puter Bridge iniciado com sucesso (PID: $PUTER_PID)"
        echo "📋 Logs em: puter-bridge.log"
    else
        echo "❌ Erro ao iniciar Puter Bridge. Verifique puter-bridge.log"
        exit 1
    fi
fi

echo ""

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
echo "🤖 Usando Claude & ChatGPT via Puter (GRATUITO)"
echo ""

if [ -n "$2" ]; then
    venv/bin/python3 src/main.py "$LOG_FILE" -o "$2"
else
    venv/bin/python3 src/main.py "$LOG_FILE"
fi

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Análise concluída!"
    echo "📂 Verifique os relatórios em reports/"
else
    echo "⚠️  Análise finalizada com avisos"
fi
echo ""
echo "💡 Puter Bridge continua rodando em background"
echo "   Para parar: kill \$(cat .puter.pid)"
echo "   Para ver logs: tail -f puter-bridge.log"
echo "=========================================="

exit $EXIT_CODE
