# Guia de Uso - Excessive Logs Analyzer

Guia completo para utilizar a ferramenta de análise de logs excessivos.

---

## 📋 Índice

1. [Instalação](#instalação)
2. [Como Funciona](#como-funciona)
3. [Uso Básico](#uso-básico)
4. [Configuração](#configuração)
5. [Interpretação de Resultados](#interpretação-de-resultados)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Troubleshooting](#troubleshooting)

---

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

```bash
# 1. Navegue até o diretório do projeto
cd Application

# 2. Crie um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o Puter Bridge (para Claude e ChatGPT gratuitos)
cd puter-bridge
npm install
npm run auth
cd ..

# 5. Teste a instalação
python3 src/main.py dataset/synthetic_logs.json
```

Se ver o relatório de análise, a instalação está correta!

---

## Como Funciona

A ferramenta executa **todas as análises disponíveis** em uma única chamada, usando cada provedor configurado:

| Provedor | Custo | Requer configuração |
|----------|-------|---------------------|
| **Groq** (Llama 3.3) | Gratuito | `GROQ_API_KEY` no `.env` |
| **Google Gemini** | Gratuito | `GOOGLE_API_KEY` no `.env` |
| **Claude** via Puter | Gratuito | Puter Bridge rodando |
| **ChatGPT** via Puter | Gratuito | Puter Bridge rodando |
| **Standard** (sem IA) | Gratuito | Nenhuma |

Cada provedor disponível executa as 3 análises independentemente. Os resultados são comparados no relatório final, o que permite avaliar a consistência entre diferentes modelos.

---

## Uso Básico

### Sintaxe do Comando

```bash
python3 src/main.py <arquivo_logs> [opções]
```

### Opções Disponíveis

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `-o, --output` | Nome base para os arquivos de relatório (sem extensão) | `-o meu_relatorio` |

### Exemplos de Comandos

```bash
# Análise completa (todos os provedores disponíveis)
python3 src/main.py dataset/synthetic_logs.json

# Com nome de saída personalizado
python3 src/main.py production_logs.json -o relatorio_producao

# Usando o script que inicia o Puter Bridge automaticamente
./run_with_puter.sh dataset/synthetic_logs.json
```

### Formato de Entrada

A ferramenta espera logs em formato JSON com a seguinte estrutura:

```json
{
  "timestamp": "2026-04-21T10:30:00.000Z",
  "level": "ERROR",
  "service": "payment-service",
  "instance": "pod-123",
  "request_id": "req-abc",
  "message": "Payment processing failed",
  "http": {
    "method": "POST",
    "path": "/api/payments",
    "status_code": 500
  },
  "error": {
    "type": "DatabaseException",
    "message": "Connection timeout"
  },
  "tags": ["payment", "error", "timeout"]
}
```

**Campos principais:**
- `timestamp` - Data/hora do log (ISO 8601)
- `level` - Nível: DEBUG, INFO, WARN, ERROR
- `service` - Nome do serviço
- `message` - Mensagem do log
- `http` (opcional) - Dados HTTP
- `error` (opcional) - Dados de erro
- `tags` (opcional) - Tags do log

---

## Configuração

### Arquivo .env

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### Configuração para Groq (GRATUITO)

```bash
# .env
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

**Como obter a API key:**
1. Acesse https://console.groq.com/
2. Crie uma conta gratuita
3. Gere uma API key em API Keys

### Configuração para Google Gemini (GRATUITO)

```bash
# .env
GOOGLE_API_KEY=sua_chave_google_aqui
GEMINI_MODEL_NAME=gemini-flash-latest
```

**Como obter a API key:**
1. Acesse https://aistudio.google.com/app/apikey
2. Crie uma conta Google
3. Gere uma API key

### Configuração para Claude e ChatGPT (via Puter — GRATUITO)

O Puter Bridge permite usar Claude e ChatGPT sem custo. Inicie-o antes de executar a análise:

```bash
# Inicia o Puter Bridge
./start_puter.sh

# Execute a análise normalmente
python3 src/main.py dataset/synthetic_logs.json

# Para o Puter Bridge ao terminar
./stop_puter.sh
```

Ou use o script integrado que gerencia tudo automaticamente:

```bash
./run_with_puter.sh dataset/synthetic_logs.json
```

---

## Interpretação de Resultados

### Arquivos Gerados

Após a análise, os relatórios são salvos na pasta `reports/`:

```
reports/
├── synthetic_logs_groq.json       # Resultado do Groq
├── synthetic_logs_gemini.json     # Resultado do Gemini
├── synthetic_logs_claude_ai.json  # Resultado do Claude
├── synthetic_logs_chatgpt.json    # Resultado do ChatGPT
├── synthetic_logs_sem_ia.json     # Resultado Standard (sem IA)
└── synthetic_logs_comparativo.json # Comparativo consolidado
```

> **Atenção:** os arquivos são sobrescritos a cada execução. Use `-o` para nomear relatórios que precisem ser preservados.

### Health Score

Métrica de 0 a 100 que indica a saúde do sistema de logs:

| Score | Status | Ação |
|-------|--------|------|
| 80-100 | ✅ Excelente | Manter boas práticas |
| 60-79 | ⚠️ Bom | Melhorias recomendadas |
| 40-59 | 🟠 Regular | Ação necessária |
| 0-39 | 🔴 Crítico | Ação urgente |

### Níveis de Severidade

- **ok** - Tudo certo ✅
- **low** - Problemas menores 🟡
- **medium** - Atenção necessária 🟠
- **high** - Ação necessária 🔴
- **critical** - Urgente ⚠️

### Estrutura do Relatório Individual

```json
{
  "metadata": {
    "analysis_timestamp": "...",
    "analysis_mode": "groq",
    "llm_provider": "groq",
    "model": "llama-3.3-70b-versatile"
  },
  "summary": {
    "total_logs": 1000,
    "level_distribution": {},
    "log_rate": {}
  },
  "analyses": {
    "log_levels": {},
    "unnecessary_logs": {},
    "sampling_recommendations": {}
  },
  "overall_assessment": {
    "health_score": 75,
    "overall_severity": "medium",
    "total_issues": 5,
    "priority_actions": []
  }
}
```

### Ações Prioritárias

O relatório lista ações ordenadas por prioridade:

```json
"priority_actions": [
  {
    "priority": 1,
    "action": "Ajustar níveis de log",
    "reason": "Configuração inadequada detectada"
  },
  {
    "priority": 2,
    "action": "Remover logs desnecessários",
    "reason": "Potencial de redução de 35%"
  }
]
```

**Comece sempre pela ação de prioridade 1!**

---

## Exemplos Práticos

### Exemplo 1: Primeira Análise

```bash
# Análise completa com todos os provedores disponíveis
python3 src/main.py production_logs.json -o initial_report

# Ver Health Score do modo Standard
cat reports/initial_report_sem_ia.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Health Score:', data['overall_assessment']['health_score'])
print('Severidade:', data['overall_assessment']['overall_severity'])
"
```

**Resultado típico:**
```
Health Score: 65/100
Severidade: MEDIUM
Issues: 8
Potencial de redução: 28%
```

---

### Exemplo 2: Comparar Provedores

```bash
# Executa todos e gera relatório comparativo
python3 src/main.py production_logs.json -o comparacao

# Ver comparativo consolidado
cat reports/comparacao_comparativo.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for mode, result in data['results_by_mode'].items():
    score = result['overall_assessment']['health_score']
    issues = result['overall_assessment']['total_issues']
    print(f'{mode:10s}: Health={score}/100  Issues={issues}')
"
```

---

### Exemplo 3: Workflow Completo de Melhoria

**Passo 1: Análise antes da intervenção**
```bash
python3 src/main.py logs.json -o before
```

**Passo 2: Implementar recomendações**
```bash
# Ver recomendações detalhadas do Groq
cat reports/before_groq.json | python3 -m json.tool | less
```

**Passo 3: Validar melhorias**
```bash
python3 src/main.py logs_after.json -o after

# Comparar scores
echo "Antes:" && cat reports/before_sem_ia.json | python3 -c "
import json, sys; d = json.load(sys.stdin)
print('  Health Score:', d['overall_assessment']['health_score'])
"
echo "Depois:" && cat reports/after_sem_ia.json | python3 -c "
import json, sys; d = json.load(sys.stdin)
print('  Health Score:', d['overall_assessment']['health_score'])
"
```

---

### Exemplo 4: CI/CD Integration

```yaml
# .github/workflows/analyze-logs.yml
analyze_logs:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Analyze logs
      run: python3 src/main.py logs/test.json -o report

    - name: Check Health Score
      run: |
        SCORE=$(cat reports/report_sem_ia.json | python3 -c "
        import json, sys
        print(json.load(sys.stdin)['overall_assessment']['health_score'])
        ")
        if [ $SCORE -lt 70 ]; then
          echo "❌ Health Score muito baixo: $SCORE"
          exit 1
        fi
```

---

### Exemplo 5: Análise Periódica

```bash
#!/bin/bash
# Script para análise diária
DATE=$(date +%Y%m%d)

python3 src/main.py /var/logs/app.json -o "daily_${DATE}"

SCORE=$(cat "reports/daily_${DATE}_sem_ia.json" | python3 -c "
import json, sys
print(json.load(sys.stdin)['overall_assessment']['health_score'])
")

if [ $SCORE -lt 70 ]; then
    echo "⚠️ Health Score: $SCORE" | mail -s "Log Alert" admin@example.com
fi
```

---

### Exemplo 6: Filtrar Resultados com jq

```bash
# Ver apenas ações prioritárias do Groq
cat reports/analysis_groq.json | jq '.overall_assessment.priority_actions'

# Ver potencial de redução
cat reports/analysis_groq.json | jq '.analyses.unnecessary_logs.reduction_potential_percentage'

# Ver estratégias de sampling
cat reports/analysis_groq.json | jq '.analyses.sampling_recommendations.recommended_strategies'

# Comparar Health Scores de todos os provedores
cat reports/analysis_comparativo.json | jq '.results_by_mode | to_entries[] | {mode: .key, score: .value.overall_assessment.health_score}'
```

---

## Troubleshooting

### Erro: "Módulo não instalado"

```bash
pip install -r requirements.txt
```

### Erro: "API Key não encontrada"

```bash
# Verificar se .env existe
ls -la .env

# Criar a partir do exemplo
cp .env.example .env
# Editar e adicionar sua chave
nano .env
```

### Erro: "Arquivo de logs não encontrado"

```bash
# Usar caminho absoluto
python3 src/main.py /caminho/completo/logs.json
```

### Puter Bridge não conecta

```bash
# Verifique se o bridge está rodando
curl http://localhost:3000/health

# Se não estiver, inicie-o
./start_puter.sh

# Verifique os logs do bridge
cat puter-bridge.log
```

### Análise não usa IA mesmo com chave configurada

```bash
# Verificar se a chave está sendo carregada
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GROQ:', os.getenv('GROQ_API_KEY', 'NÃO ENCONTRADA'))
print('GOOGLE:', os.getenv('GOOGLE_API_KEY', 'NÃO ENCONTRADA'))
"
```

### Formato de log inválido

Certifique-se que seu log tem os campos mínimos:

```json
{
  "timestamp": "2026-04-21T10:00:00.000Z",
  "level": "INFO",
  "service": "my-service",
  "message": "Log message"
}
```

---

## Dicas e Boas Práticas

### 1. Preserve Relatórios Importantes

```bash
# Use -o com nome descritivo para não sobrescrever
python3 src/main.py logs.json -o "producao_$(date +%Y%m%d)"
```

### 2. Compare Provedores para Maior Confiança

Quando diferentes provedores concordam em um issue, a probabilidade de ser um problema real é maior. Divergências indicam casos limítrofes que merecem análise manual.

### 3. Use o Modo Standard como Baseline

O modo Standard é determinístico — os mesmos logs sempre produzem o mesmo resultado. Use-o para comparações antes/depois de mudanças no sistema de logging.

### 4. Dataset de Teste

Use os logs sintéticos incluídos para validar a instalação e entender o formato esperado:

```bash
python3 src/main.py dataset/synthetic_logs.json
```

---

## Recursos Adicionais

- **Executar com Puter Bridge automático:** `./run_with_puter.sh`
- **Executar análise sem Puter:** `./run_analysis.sh`
- **Parar Puter Bridge:** `./stop_puter.sh`
- **Gerar novo dataset sintético:** `python3 dataset/generate_synthetic_logs.py`
- **Documentação técnica:** `docs/ARQUITETURA.md`
- **Comparativo de provedores:** `docs/TABELA_COMPARACAO.md`

---

## Suporte

- Issues: Abra uma issue no repositório
- Contribuições: Pull requests são bem-vindos

---

**Versão:** 4.0
**Última atualização:** Julho 2026
