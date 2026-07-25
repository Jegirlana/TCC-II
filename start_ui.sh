#!/bin/bash
# Inicia a interface gráfica do Excessive Logs Analyzer

echo "=========================================="
echo "  EXCESSIVE LOGS ANALYZER — Interface Web"
echo "=========================================="
echo ""

if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado."
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if ! venv/bin/python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Instalando Streamlit..."
    venv/bin/pip install streamlit --quiet
fi

echo "🚀 Iniciando interface web..."
echo "   Acesse em: http://127.0.0.1:8501"
echo "   Para encerrar: Ctrl+C"
echo ""

venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
