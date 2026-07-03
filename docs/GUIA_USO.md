# Guia de Uso - Excessive Logs Analyzer

Guia completo para utilizar a ferramenta de análise de logs excessivos.

---

## 📋 Índice

1. [Instalação](#instalação)
2. [Modos de Análise](#modos-de-análise)
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
./run_with_puter.sh
```

### Verificação

Execute um teste rápido com os dados de exemplo:

```bash
python3 src/main.py dataset/synthetic_logs.json --mode standard
```

Se ver o relatório de análise, a instalação está correta!

---

## Modos de Análise

A ferramenta oferece **3 modos de análise**:

### 📊 Comparação dos Modos

| Aspecto | Standard | Claude | ChatGPT |
|---------|----------|--------|---------|
| **Custo** | Gratuito | ~$0.003-0.01/1000 logs | ~$0.005-0.02/1000 logs |
| **Velocidade** | Muito rápido (< 1s) | Moderado (5-15s) | Moderado (5-15s) |
| **Qualidade** | Boa | Excelente | Excelente |
| **Recomendações** | Genéricas | Específicas | Específicas |
| **API Key** | Não requer | Anthropic | OpenAI |
| **Uso offline** | ✅ Sim | ❌ Não | ❌ Não |

### 1️⃣ Modo Standard (Padrão)

**Quando usar:**
- Análises rápidas e exploratórias
- CI/CD pipelines
- Análises de rotina
- Sem orçamento para APIs

**Características:**
- ✅ Completamente gratuito
- ✅ Não precisa de configuração
- ✅ Processamento rápido
- ✅ Análise baseada em regras e heurísticas
- ⚠️ Recomendações genéricas

**Como usar:**
```bash
python3 src/main.py logs.json --mode standard
```

---

### 2️⃣ Modo Claude (Anthropic AI)

**Quando usar:**
- Análises profundas e auditorias
- Identificar problemas complexos
- Obter recomendações específicas de código
- Otimização de custos com prompt caching

**Características:**
- ✅ Análise contextual profunda
- ✅ Recomendações personalizadas
- ✅ Sugestões específicas de código
- ✅ Prompt caching (reduz custos)
- 💰 Requer API key paga

**Como usar:**
```bash
python3 src/main.py logs.json --mode claude
```

**Modelos disponíveis:**
- `claude-sonnet-4-6` - Recomendado (equilíbrio)
- `claude-opus-4-6` - Mais poderoso
- `claude-haiku-4-5` - Mais rápido

---

### 3️⃣ Modo ChatGPT (OpenAI)

**Quando usar:**
- Análises profundas e auditorias
- Alternativa ao Claude
- Já tem conta OpenAI
- Preferência pelo ecossistema OpenAI

**Características:**
- ✅ Análise contextual profunda
- ✅ Recomendações personalizadas
- ✅ Ampla disponibilidade global
- 💰 Requer API key paga

**Como usar:**
```bash
python3 src/main.py logs.json --mode chatgpt
```

**Modelos disponíveis:**
- `gpt-4o` - Recomendado (GPT-4 Omni)
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - Mais barato

---

## Uso Básico

### Sintaxe do Comando

```bash
python3 src/main.py <arquivo_logs> [opções]
```

### Opções Disponíveis

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--mode` | Modo de análise (standard/claude/chatgpt) | `--mode claude` |
| `-o, --output` | Arquivo de saída do relatório | `-o report.json` |
| `--no-llm` | (Deprecated) Use `--mode standard` | |

### Exemplos de Comandos

```bash
# Análise padrão (gratuita)
python3 src/main.py dataset/synthetic_logs.json --mode standard

# Análise com Claude
python3 src/main.py production_logs.json --mode claude -o report.json

# Análise com ChatGPT
python3 src/main.py staging_logs.json --mode chatgpt

# Comparar todos os modos
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

### Configuração para Claude

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CLAUDE_MODEL_NAME=claude-sonnet-4-6
```

**Como obter a API key:**
1. Acesse https://console.anthropic.com/
2. Crie uma conta
3. Adicione créditos (mínimo $5)
4. Gere uma API key em Settings → API Keys

### Configuração para ChatGPT

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL_NAME=gpt-4o
```

**Como obter a API key:**
1. Acesse https://platform.openai.com/
2. Crie uma conta
3. Adicione créditos
4. Gere uma API key em API keys

### Testar Configuração

```bash
# Verifica quais modos estão disponíveis
python3 test_modes.py
```

---

## Interpretação de Resultados

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

### Estrutura do Relatório

O relatório JSON contém:

```json
{
  "metadata": {
    "analysis_timestamp": "...",
    "analysis_mode": "standard|claude|chatgpt",
    "llm_provider": "...",
    "model": "..."
  },
  "summary": {
    "total_logs": 1000,
    "level_distribution": {...},
    "log_rate": {...}
  },
  "analyses": {
    "log_levels": {...},
    "unnecessary_logs": {...},
    "sampling_recommendations": {...}
  },
  "overall_assessment": {
    "health_score": 75,
    "overall_severity": "medium",
    "total_issues": 5,
    "priority_actions": [...]
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

### Exemplo 1: Primeira Análise (Standard)

```bash
# Análise rápida e gratuita
python3 src/main.py production_logs.json --mode standard -o initial_report.json

# Ver Health Score
cat initial_report.json | grep -A 5 'overall_assessment'

# Ver ações prioritárias
cat initial_report.json | grep -A 10 'priority_actions'
```

**Resultado típico:**
```
Health Score: 65/100
Severidade: MEDIUM
Issues: 8
Potencial de redução: 28%
```

---

### Exemplo 2: Análise Profunda (Claude)

Quando o Health Score está baixo, use IA para análise detalhada:

```bash
# Análise com Claude
python3 src/main.py production_logs.json --mode claude -o detailed_report.json
```

**Diferenças no output:**

**Standard:**
```json
{
  "recommendation": "Reduzir logs INFO desnecessários",
  "priority": "medium"
}
```

**Claude:**
```json
{
  "recommendation": "Remover log INFO em PaymentService.processPayment() linha 87",
  "rationale": "Duplica informação do log de confirmação",
  "code_suggestion": "// Remover: logger.info('Processing...')\n// Manter: logger.info('Payment confirmed', details)",
  "estimated_reduction": "8% dos logs INFO"
}
```

---

### Exemplo 3: Comparação de Modos

```bash
# Executar todos os modos
./compare_modes.sh production_logs.json

# Resultado:
# 📊 Standard:  15 issues | Health Score: 60/100
# 🤖 Claude:    18 issues | Health Score: 58/100  
# 💬 ChatGPT:   17 issues | Health Score: 59/100
```

---

### Exemplo 4: Workflow Completo

**Passo 1: Análise Inicial**
```bash
python3 src/main.py logs.json --mode standard -o before.json
```

**Passo 2: Se Health Score < 70, análise profunda**
```bash
SCORE=$(cat before.json | python3 -c "import json, sys; print(json.load(sys.stdin)['overall_assessment']['health_score'])")

if [ $SCORE -lt 70 ]; then
    python3 src/main.py logs.json --mode claude -o detailed.json
fi
```

**Passo 3: Implementar recomendações**
```bash
# Ver recomendações
cat detailed.json | python3 -m json.tool | less
```

**Passo 4: Validar melhorias**
```bash
python3 src/main.py logs_after.json --mode standard -o after.json

# Comparar scores
echo "Antes:" && cat before.json | grep health_score
echo "Depois:" && cat after.json | grep health_score
```

---

### Exemplo 5: CI/CD Integration

```yaml
# .github/workflows/analyze-logs.yml
analyze_logs:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    
    - name: Analyze logs
      run: |
        python3 src/main.py logs/test.json --mode standard -o report.json
        
    - name: Check Health Score
      run: |
        SCORE=$(cat report.json | python3 -c "import json, sys; print(json.load(sys.stdin)['overall_assessment']['health_score'])")
        if [ $SCORE -lt 70 ]; then
          echo "❌ Health Score muito baixo: $SCORE"
          exit 1
        fi
```

---

### Exemplo 6: Análise Periódica

```bash
# Script para análise diária
#!/bin/bash
DATE=$(date +%Y%m%d)

# Análise standard (gratuita)
python3 src/main.py /var/logs/app.json \
  --mode standard \
  -o "reports/daily_${DATE}.json"

# Alerta se Health Score < 70
SCORE=$(cat "reports/daily_${DATE}.json" | python3 -c "import json, sys; print(json.load(sys.stdin)['overall_assessment']['health_score'])")

if [ $SCORE -lt 70 ]; then
    echo "⚠️ Health Score: $SCORE" | mail -s "Log Alert" admin@example.com
fi

# Análise profunda mensal (no dia 1)
if [ $(date +%d) -eq 01 ]; then
    python3 src/main.py /var/logs/app.json \
      --mode claude \
      -o "reports/monthly_${DATE}.json"
fi
```

---

## Troubleshooting

### Erro: "Módulo não instalado"

```bash
# Solução
pip install -r requirements.txt
```

### Erro: "API Key não encontrada"

```bash
# Verificar se .env existe
ls -la .env

# Verificar conteúdo
cat .env

# Criar se não existir
cp .env.example .env
# Editar e adicionar sua chave
nano .env
```

### Erro: "Arquivo de logs não encontrado"

```bash
# Verificar caminho
ls -la caminho/para/logs.json

# Usar caminho absoluto
python3 src/main.py /caminho/completo/logs.json --mode standard
```

### Análise não usa IA mesmo com chave configurada

```bash
# Verificar se chave está sendo carregada
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"

# Se não aparecer, verificar .env
cat .env | grep ANTHROPIC
```

### Custo muito alto

**Soluções:**
- Use `--mode standard` para análises de rotina (gratuito)
- Com Claude, análises repetidas usam cache (~90% economia)
- Com ChatGPT, use `gpt-3.5-turbo` para custos menores

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

### 1. Escolha o Modo Certo

- **Exploração inicial?** → Standard
- **Problemas identificados?** → Claude/ChatGPT
- **CI/CD?** → Standard
- **Auditoria profunda?** → Claude/ChatGPT

### 2. Economize Custos

- Análises de rotina: Standard (gratuito)
- Análises profundas: Claude (prompt caching)
- Use ChatGPT 3.5-turbo para análises menos críticas

### 3. Automatize

```bash
# Diário: Standard
# Mensal: Claude/ChatGPT
# Após mudanças: Comparação antes/depois
```

### 4. Use jq para Filtrar

```bash
# Ver apenas ações prioritárias
cat report.json | jq '.overall_assessment.priority_actions'

# Ver potencial de redução
cat report.json | jq '.analyses.unnecessary_logs.reduction_potential_percentage'

# Ver estratégias de sampling
cat report.json | jq '.analyses.sampling_recommendations.recommended_strategies'
```

### 5. Salve Relatórios com Datas

```bash
python3 src/main.py logs.json --mode claude -o "report_$(date +%Y%m%d).json"
```

---

## Recursos Adicionais

- **Executar com Puter:** `./run_with_puter.sh`
- **Executar análise básica:** `./run_analysis.sh`
- **Parar Puter Bridge:** `./stop_puter.sh`
- **Gerador de logs sintéticos:** `dataset/generate_synthetic_logs.py`

---

## Suporte

- Documentação técnica: `docs/ARQUITETURA.md`
- Issues: Abra uma issue no repositório
- Contribuições: Pull requests são bem-vindos

---

**Versão:** 2.0  
**Última atualização:** Abril 2026
