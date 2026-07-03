#!/bin/bash
# Script para parar o Puter Bridge

echo "🛑 Parando Puter Bridge..."

if [ -f ".puter.pid" ]; then
    PID=$(cat .puter.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        rm .puter.pid
        echo "✓ Puter Bridge parado (PID: $PID)"
    else
        echo "⚠️  Processo $PID não está rodando"
        rm .puter.pid
    fi
else
    echo "⚠️  Arquivo .puter.pid não encontrado"
    echo "   Procurando processos do Puter Bridge..."

    # Tenta encontrar e matar processos do node relacionados ao puter-bridge
    PIDS=$(ps aux | grep "puter-bridge" | grep -v grep | awk '{print $2}')

    if [ -n "$PIDS" ]; then
        echo "   Encontrados PIDs: $PIDS"
        echo "$PIDS" | xargs kill
        echo "✓ Processos parados"
    else
        echo "   Nenhum processo encontrado"
    fi
fi

echo "✓ Puter Bridge parado"
