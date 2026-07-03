# Arquitetura - Excessive Logs Analyzer

Documentação técnica completa da arquitetura e implementação da ferramenta.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Soluções Implementadas](#soluções-implementadas)
4. [Componentes Principais](#componentes-principais)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Estrutura de Arquivos](#estrutura-de-arquivos)
7. [Modelo de Dados](#modelo-de-dados)
8. [Métricas e Thresholds](#métricas-e-thresholds)

---

## Visão Geral

O **Excessive Logs Analyzer** é uma ferramenta que identifica e mitiga o antipadrão "Excessive Logs" implementando 3 soluções principais com suporte opcional de IA (Claude ou ChatGPT).

### Objetivos

- ✅ Detectar uso inadequado de níveis de log
- ✅ Identificar logs desnecessários
- ✅ Recomendar estratégias de sampling
- ✅ Fornecer relatórios acionáveis
- ✅ Estimar impacto e ROI

### Tecnologias

- **Linguagem:** Python 3.8+
- **IA (múltiplos provedores):**
  - **Gratuitos:** Groq API (Llama 3.3 70B), Google Gemini 1.5 Flash
  - **Pagos (opcional):** Anthropic Claude API, OpenAI ChatGPT API
- **Formato:** JSON para entrada e saída
- **Dependências:** anthropic, openai, groq, google-generativeai, python-dotenv

---

## Arquitetura do Sistema

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────┐
│                   CAMADA DE ENTRADA                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   Logs   │  │Sintéticos│  │  Seus    │              │
│  │   JSON   │  │ Gerados  │  │  Logs    │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼─────────────────────┘
        └─────────────┴─────────────┘
                      │
┌─────────────────────┼───────────────────────────────────┐
│           CAMADA DE PROCESSAMENTO                       │
│                     ▼                                   │
│         ┌─────────────────────┐                         │
│         │   main.py           │                         │
│         │  ExcessiveLogs      │                         │
│         │    Analyzer         │                         │
│         │  (Modo: ALL)        │                         │
│         └──────────┬──────────┘                         │
│                    │                                    │
│      ┌─────────────┴─────────────┐                     │
│      ▼                           ▼                     │
│  ┌──────────┐          ┌──────────────────┐            │
│  │   Log    │          │   LLM Clients    │            │
│  │Processor │          │   (Multi-Provider)│            │
│  │          │          │                  │            │
│  │• Stats   │          │• Groq 🆓         │            │
│  │• Dups    │          │• Gemini 🆓       │            │
│  │• Rate    │          │• Claude 💰       │            │
│  │          │          │• ChatGPT 💰      │            │
│  │          │          │• Standard (none) │            │
│  └──────────┘          └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────┐
│         CAMADA DE ANÁLISE (POR PROVEDOR)                │
│                     │                                   │
│  ┌──────────────────┴───────────────────────┐          │
│  │   Para cada provedor disponível:         │          │
│  │                                           │          │
│  │   ┌──────────────┬──────────────┬──────────────┐    │
│  │   ▼              ▼              ▼              │    │
│  │ ┌────────┐   ┌────────┐   ┌────────┐           │    │
│  │ │ Log    │   │Unneces-│   │Sampling│           │    │
│  │ │ Levels │   │ sary   │   │        │           │    │
│  │ │Analyzer│   │ Logs   │   │Recom.  │           │    │
│  │ └────────┘   └────────┘   └────────┘           │    │
│  │      │            │            │                │    │
│  │      └────────────┴────────────┘                │    │
│  │                   │                             │    │
│  │                   ▼                             │    │
│  │          Relatório do Provedor                 │    │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────┐
│               CAMADA DE SAÍDA                           │
│                     ▼                                   │
│  ┌────────────────────────────────────────┐            │
│  │  Múltiplos Relatórios JSON             │            │
│  │                                        │            │
│  │  • synthetic_logs_groq.json           │            │
│  │  • synthetic_logs_gemini.json         │            │
│  │  • synthetic_logs_claude_ai.json      │            │
│  │  • synthetic_logs_chatgpt.json        │            │
│  │  • synthetic_logs_sem_ia.json         │            │
│  └────────────────┬───────────────────────┘            │
│                   │                                    │
│                   ▼                                    │
│  ┌────────────────────────────────────────┐            │
│  │  run_with_puter.sh                      │            │
│  │  • Comparação de métricas              │            │
│  │  • Análise de diferenças               │            │
│  │  • Insights consolidados               │            │
│  └────────────────┬───────────────────────┘            │
│                   │                                    │
│                   ▼                                    │
│  ┌────────────────────────────────────────┐            │
│  │  synthetic_logs_comparativo.json       │            │
│  └────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Padrões de Design

**1. Strategy Pattern (Modos de Análise)**
- 5 modos de análise disponíveis:
  - Standard (sem IA)
  - Groq (gratuito - Llama 3.3 70B)
  - Google Gemini (gratuito - Gemini 1.5 Flash)
  - Claude (pago - Claude 3.5 Sonnet)
  - ChatGPT (pago - GPT-4o)
- Interface comum: `LLMClient`
- Implementações específicas por provedor
- Execução paralela de todos os modos disponíveis

**2. Pipeline Pattern**
- Processamento sequencial
- Cada etapa alimenta a próxima
- Agregação final de resultados

**3. Factory Pattern**
- Criação de analyzers
- Inicialização de clientes LLM

---

## Soluções Implementadas

### Solução 1: Use Log Levels Effectively

**Arquivo:** `src/analyzers/log_level_analyzer.py`

**Objetivo:** Detectar uso inadequado de níveis de log

**Detecções:**
- Excesso de logs INFO (> 70%)
- DEBUG em produção (> 5%)
- Falta de logs ERROR (< 1%)
- Falta de logs WARN (< 5%)
- Desbalanceamento por serviço

**Thresholds:**
```python
THRESHOLDS = {
    'INFO_MAX_PERCENTAGE': 70,
    'DEBUG_MAX_PERCENTAGE': 5,
    'ERROR_MIN_PERCENTAGE': 1,
    'WARN_MIN_PERCENTAGE': 5
}
```

**Saída Exemplo:**
```json
{
  "severity": "high",
  "issues": [
    {
      "type": "excessive_info",
      "description": "75% de logs INFO (limite: 70%)",
      "recommendation": "Converter logs triviais para DEBUG"
    }
  ]
}
```

---

### Solução 2: Log Only What's Necessary

**Arquivo:** `src/analyzers/unnecessary_logs_detector.py`

**Objetivo:** Identificar logs desnecessários

**Detecções:**
- Logs de assets estáticos (.js, .css, /static/)
- Logs triviais de sucesso (GET 200)
- Padrões duplicados (> 10 ocorrências)
- Mensagens vazias/genéricas

**Algoritmos:**

1. **Assets Estáticos:**
```python
STATIC_PATTERNS = [
    r'\.js$', r'\.css$', r'\.png$', 
    r'/static/', r'/assets/'
]
```

2. **Duplicatas:**
```python
def find_duplicates(logs):
    counter = Counter(log['message'] for log in logs)
    return {k: v for k, v in counter.items() if v > 10}
```

3. **Cálculo de Redução:**
```python
total_unnecessary = (
    static_logs +
    trivial_success_logs +
    excessive_duplicates
)
reduction_percentage = (total_unnecessary / total_logs) * 100
```

**Saída Exemplo:**
```json
{
  "unnecessary_logs_count": 125,
  "reduction_potential_percentage": 12.2,
  "issues": [
    {
      "type": "static_assets",
      "count": 45,
      "recommendation": "Desabilitar logging de assets"
    }
  ]
}
```

---

### Solução 3: Implement Log Sampling

**Arquivo:** `src/analyzers/sampling_recommender.py`

**Objetivo:** Recomendar estratégias de sampling

**Estratégias:**

**1. Priority-based Sampling**
```
ERROR/FATAL/WARN: 100% (sempre)
INFO: 10-20% (amostragem)
DEBUG: 0-1% (produção)
```

**2. Rate-based Sampling**
```
1:N (ex: 1:5 = 20%)
Baseado em volume total
```

**3. Time-based Sampling**
```
1 log por intervalo (ex: 1/min)
Para eventos repetitivos
```

**4. Adaptive Sampling**
```
< 50 logs/min: sem sampling
50-100: sampling 50%
> 100: sampling 80%
```

**Análise de Volume:**
```python
VOLUME_THRESHOLDS = {
    'NORMAL': 50,      # logs/min
    'MODERATE': 100,
    'HIGH': 500,
    'CRITICAL': 1000
}
```

**Saída Exemplo:**
```json
{
  "severity": "medium",
  "recommended_strategies": [
    {
      "strategy": "priority_based",
      "priority": "high",
      "implementation": {
        "rules": ["ERROR: 100%", "INFO: 10-20%"],
        "expected_reduction": "40-60%"
      }
    }
  ]
}
```

---

## Componentes Principais

### 1. ExcessiveLogsAnalyzer (main.py)

**Responsabilidade:** Orquestração da análise

**Métodos principais:**

```python
class ExcessiveLogsAnalyzer:
    def __init__(self, analysis_mode: str):
        # Inicializa modo (standard/claude/chatgpt)
        # Cria LLM client se necessário
        # Instancia analyzers
        
    def analyze_file(self, log_file_path: str) -> Dict:
        # 1. Carrega logs
        # 2. Processa estatísticas
        # 3. Executa 3 analyses
        # 4. Compila relatório
        # 5. Calcula assessment
        
    def _calculate_overall_assessment(self, ...) -> Dict:
        # Calcula Health Score
        # Define severidade geral
        # Prioriza ações
```

---

### 2. LogProcessor (utils/log_processor.py)

**Responsabilidade:** Processamento estatístico

**Métodos:**

```python
class LogProcessor:
    def load_logs(self, file_path: str) -> List[Dict]:
        # Carrega JSON
        
    def get_level_distribution(self, logs) -> Dict:
        # Conta por nível
        
    def find_duplicate_logs(self, logs) -> Dict:
        # Detecta padrões repetidos
        
    def calculate_log_rate(self, logs) -> Dict:
        # Calcula logs/min
        
    def get_service_distribution(self, logs) -> Dict:
        # Distribui por serviço
```

---

### 3. LLMClient (utils/llm_client.py)

**Responsabilidade:** Integração com IAs (Multi-Provedor)

**Arquitetura Multi-Provedor:**

```python
class LLMClient:
    def __init__(self, provider: str, model: str):
        if provider == "claude":
            self._init_claude(model)
        elif provider == "chatgpt":
            self._init_chatgpt(model)
        elif provider == "groq":
            self._init_groq(model)
        elif provider == "gemini":
            self._init_gemini(model)
            
    def analyze_with_caching(self, system, user, cached):
        if self.provider == "claude":
            return self._analyze_claude_with_caching(...)
        elif self.provider == "chatgpt":
            return self._analyze_chatgpt(...)
        elif self.provider == "groq":
            return self._analyze_groq(...)
        elif self.provider == "gemini":
            return self._analyze_gemini(...)
```

**Provedores Suportados:**

1. **Groq (GRATUITO):**
   - Modelo: Llama 3.3 70B
   - Limites: 30 RPM, 14.400 RPD
   - Análise extremamente rápida

2. **Google Gemini (GRATUITO):**
   - Modelo: Gemini 1.5 Flash
   - Limites: 15 RPM, 1M tokens/mês
   - Alta qualidade de análise

3. **Claude (PAGO):**
   - Modelo padrão: Claude 3.5 Sonnet
   - Prompt caching ativo
   - ~90% redução de custo em análises repetidas

4. **ChatGPT (PAGO):**
   - Modelo padrão: GPT-4o
   - Análise contextual avançada

**Prompt Caching (Claude):**
```python
system = [
    {"type": "text", "text": system_prompt},
    {
        "type": "text",
        "text": cached_content,
        "cache_control": {"type": "ephemeral"}
    }
]
```

---

## Arquitetura de Execução Paralela

### Modelo Multi-Provedor

A aplicação foi redesenhada para executar **todas as análises disponíveis simultaneamente**:

```
┌─────────────────────────────────────────────────────────┐
│                  ENTRADA ÚNICA                          │
│              synthetic_logs.json                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Carregamento de Logs  │ (UMA VEZ)
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ Processamento Stats   │ (UMA VEZ)
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────────────────────┐
        │                                       │
        ▼           ▼         ▼         ▼       ▼
    ┌─────┐   ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐
    │Groq │   │Gemini│  │Claude│  │ChatGPT│ │Standard│
    │ 🆓  │   │ 🆓   │  │ 💰   │  │ 💰    │ │   📊   │
    └──┬──┘   └───┬──┘  └───┬──┘  └───┬───┘ └────┬───┘
       │          │         │         │          │
       ▼          ▼         ▼         ▼          ▼
  [3 análises] [3 análises] [3 análises] [3 análises] [3 análises]
       │          │         │         │          │
       ▼          ▼         ▼         ▼          ▼
┌──────────────────────────────────────────────────────┐
│              SAÍDAS INDEPENDENTES                    │
│  groq.json | gemini.json | claude_ai.json |         │
│  chatgpt.json | sem_ia.json                          │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │run_with_puter.sh │
            └──────────┬───────┘
                       │
                       ▼
            ┌──────────────────┐
            │comparativo.json  │
            └──────────────────┘
```

### Vantagens da Arquitetura

1. **Eficiência:** Estatísticas calculadas uma única vez
2. **Independência:** Falha em um provedor não afeta os outros
3. **Flexibilidade:** Usuário escolhe quais APIs configurar
4. **Comparabilidade:** Todos os modos analisam os mesmos dados
5. **Economia:** Opções gratuitas (Groq/Gemini) disponíveis

### Gestão de Falhas

```python
# Cada provedor é inicializado de forma independente
try:
    self.llm_clients['groq'] = LLMClient(provider='groq')
    print(f"✓ Cliente Groq (GRATUITO) inicializado")
except Exception as e:
    print(f"⚠ Não foi possível inicializar GROQ: {e}")
    self.llm_clients['groq'] = None
```

**Comportamento:**
- Se API key não configurada: modo desabilitado
- Se erro na inicialização: modo desabilitado
- Standard sempre funciona (não requer APIs)
- Executa análise com todos os modos disponíveis

---

## Fluxo de Execução

### 1. Inicialização

```
Usuário executa:
python3 src/main.py logs.json [-o nome_saida]
        │
        ▼
ExcessiveLogsAnalyzer.__init__(analysis_mode="all")
        │
        ├─> Tenta inicializar Groq (GRATUITO)
        ├─> Tenta inicializar Gemini (GRATUITO)
        ├─> Tenta inicializar Claude (PAGO)
        ├─> Tenta inicializar ChatGPT (PAGO)
        └─> Standard sempre disponível (sem LLM)
        │
        ▼
Executará análises com TODOS os provedores disponíveis
```

### 2. Carregamento

```
analyze_file(log_file_path)
        │
        ▼
LogProcessor.load_logs(file_path)
        │
        ▼
Carrega JSON e valida estrutura
        │
        ▼
Retorna List[Dict] com logs
```

### 3. Processamento Estatístico

```
LogProcessor executa:
        │
        ├─> get_level_distribution()
        ├─> get_service_distribution()
        ├─> group_by_service_and_level()
        ├─> find_duplicate_logs()
        ├─> calculate_log_rate()
        ├─> get_error_types()
        ├─> get_http_status_distribution()
        └─> get_tags_distribution()
        │
        ▼
Dados estatísticos prontos
```

### 4. Análises (Múltiplos Modos em Paralelo)

```
Para cada provedor disponível (Groq, Gemini, Claude, ChatGPT, Standard):
        │
        ┌─────────────────────────────────┐
        │                                 │
        ▼                ▼                ▼
LogLevelAnalyzer  UnnecessaryLogs  SamplingRecommender
        │                │                │
        │ (usa stats)    │ (usa dups)     │ (usa rate)
        │                │                │
        ├─> Detecta      ├─> Identifica  ├─> Calcula
        │   issues       │   unnecessary  │   volume
        │                │                │
        ├─> LLM?         ├─> LLM?         ├─> LLM?
        │   insights     │   insights     │   insights
        │                │                │
        └────────────────┴────────────────┘
                      │
                      ▼
        Gera relatório específico para o modo
        │
        ▼
Salva: nome_provedor.json (ex: synthetic_logs_groq.json)
```

**Execução:**
- Cada modo executa independentemente as 3 análises
- Gera relatório individual (ex: `synthetic_logs_groq.json`, `synthetic_logs_gemini.json`)
- Script `run_with_puter.sh` executa análise com todos os modos disponíveis

### 5. Agregação e Assessment

```
_calculate_overall_assessment()
        │
        ├─> Determina severidade máxima
        ├─> Conta total de issues
        ├─> Calcula Health Score
        └─> Prioriza ações
        │
        ▼
Relatório completo compilado
```

### 6. Saída (Múltiplos Relatórios)

```
        ┌───────────────────────────────────┐
        │                                   │
        ▼                ▼                  ▼
  groq.json      gemini.json    claude_ai.json
        │                │                  │
        ▼                ▼                  ▼
 chatgpt.json     sem_ia.json   comparativo.json
        │                │                  │
        └────────────────┴──────────────────┘
                         │
                         ▼
            Todos salvos em reports/
                         │
                         ▼
        Relatórios JSON são gerados em reports/
```

**Arquivos Gerados:**
- `{nome}_groq.json` - Análise com Groq (se disponível)
- `{nome}_gemini.json` - Análise com Gemini (se disponível)
- `{nome}_claude_ai.json` - Análise com Claude (se disponível)
- `{nome}_chatgpt.json` - Análise com ChatGPT (se disponível)
- `{nome}_sem_ia.json` - Análise Standard
- `{nome}_comparativo.json` - Consolidação de todos os modos

---

## Estrutura de Arquivos

```
Application/
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Orquestrador principal (executa todos os modos)
│   │
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── log_level_analyzer.py          # Solução 1
│   │   ├── unnecessary_logs_detector.py   # Solução 2
│   │   └── sampling_recommender.py        # Solução 3
│   │
│   └── utils/
│       ├── __init__.py
│       ├── llm_client.py          # Cliente Multi-LLM (Groq/Gemini/Claude/ChatGPT)
│       └── log_processor.py       # Processamento estatístico
│
├── dataset/
│   ├── log_model.json             # Schema do formato
│   ├── generate_synthetic_logs.py # Gerador de logs
│   └── synthetic_logs.json        # Logs de exemplo
│
├── reports/                       # Relatórios gerados (NOVO)
│   ├── *_groq.json               # Análise com Groq
│   ├── *_gemini.json             # Análise com Gemini
│   ├── *_claude_ai.json          # Análise com Claude
│   ├── *_chatgpt.json            # Análise com ChatGPT
│   ├── *_sem_ia.json             # Análise Standard
│   └── *_comparativo.json        # Relatório consolidado
│
├── docs/
│   ├── GUIA_USO.md                # Guia de uso
│   └── ARQUITETURA.md             # Documentação técnica (este arquivo)
│
├── run_with_puter.sh              # Script principal de execução (com Puter)
├── run_analysis.sh                # Script de análise básica (sem Puter)
├── start_puter.sh                 # Inicia Puter Bridge em background
├── stop_puter.sh                  # Para Puter Bridge
├── run_analysis.sh                # Script simplificado de execução (NOVO)
│
├── .env                           # Configuração de API keys
├── .env.example                   # Exemplo de configuração
├── requirements.txt               # Dependências (inclui groq e google-generativeai)
├── INICIO_RAPIDO.md              # Início rápido
└── README.md                      # Documentação principal
```

### Tamanho dos Componentes

| Arquivo | Linhas | Complexidade |
|---------|--------|--------------|
| main.py | ~620 | Alta |
| log_level_analyzer.py | ~420 | Média |
| unnecessary_logs_detector.py | ~530 | Média |
| sampling_recommender.py | ~680 | Alta |
| llm_client.py | ~260 | Média |
| log_processor.py | ~180 | Baixa |
| run_with_puter.sh | ~95 | Baixa |
| start_puter.sh | ~30 | Baixa |
| stop_puter.sh | ~25 | Baixa |

---

## Modelo de Dados

### Formato de Entrada (Log)

```json
{
  "timestamp": "2026-04-21T10:30:00.000Z",
  "level": "ERROR|WARN|INFO|DEBUG",
  "service": "service-name",
  "instance": "pod-123",
  "request_id": "req-abc",
  "trace_id": "trace-xyz",
  "message": "Log message",
  "http": {
    "method": "GET|POST|PUT|DELETE",
    "path": "/api/endpoint",
    "status_code": 200
  },
  "error": {
    "type": "ExceptionType",
    "message": "Error details"
  },
  "tags": ["tag1", "tag2"]
}
```

### Formato de Saída (Relatório)

```json
{
  "metadata": {
    "analysis_timestamp": "ISO-8601",
    "log_file": "path/to/file",
    "analysis_mode": "groq|gemini|claude|chatgpt|standard",
    "llm_provider": "groq|gemini|claude|chatgpt|null",
    "model": "llama-3.3-70b|gemini-1.5-flash|claude-3-5-sonnet|gpt-4o|null"
  },
  "summary": {
    "total_logs": 1000,
    "level_distribution": {...},
    "service_distribution": {...},
    "log_rate": {...},
    "error_types": {...},
    "http_status_distribution": {...},
    "tags_distribution": {...},
    "duplicate_patterns": 15
  },
  "analyses": {
    "log_levels": {
      "severity": "ok|low|medium|high|critical",
      "issues": [...],
      "recommendations": [...],
      "level_percentages": {...}
    },
    "unnecessary_logs": {
      "severity": "...",
      "unnecessary_logs_count": 125,
      "reduction_potential_percentage": 12.2,
      "issues": [...],
      "recommendations": [...]
    },
    "sampling_recommendations": {
      "severity": "...",
      "current_state": {...},
      "volume_analysis": {...},
      "recommended_strategies": [...],
      "estimated_reduction": {...}
    }
  },
  "overall_assessment": {
    "overall_severity": "ok|low|medium|high|critical",
    "health_score": 80,
    "total_issues": 5,
    "priority_actions": [
      {
        "priority": 1,
        "action": "Action description",
        "reason": "Reason for action"
      }
    ],
    "summary": "Overall summary text"
  }
}
```

---

## Métricas e Thresholds

### Health Score

**Cálculo:**
```python
if max_severity == 'critical':
    health_score = 20
elif max_severity == 'high':
    health_score = 40
elif max_severity == 'medium':
    health_score = 60
elif max_severity == 'low':
    health_score = 80
else:  # 'ok'
    health_score = 100
```

### Severidade

**Ordem:**
```python
severity_order = ['ok', 'low', 'medium', 'high', 'critical']
max_severity = max(all_severities, key=lambda s: severity_order.index(s))
```

### Thresholds Principais

**Níveis de Log:**
```python
INFO_MAX = 70%       # Máximo de INFO
DEBUG_MAX = 5%       # Máximo de DEBUG (produção)
ERROR_MIN = 1%       # Mínimo de ERROR
WARN_MIN = 5%        # Mínimo de WARN
```

**Volume:**
```python
NORMAL = < 50 logs/min
MODERATE = 50-100 logs/min
HIGH = 100-500 logs/min
CRITICAL = > 500 logs/min
```

**Duplicatas:**
```python
EXCESSIVE_DUPLICATES = > 10 ocorrências
```

**Redução Potencial:**
```python
LOW = < 15%
MEDIUM = 15-30%
HIGH = 30-50%
CRITICAL = > 50%
```

---

## Ferramentas e Scripts

### run_analysis.sh

Script simplificado para executar análises:

```bash
./run_analysis.sh [arquivo.json]
```

**Funcionalidades:**
- Executa análise em todos os modos disponíveis
- Usa arquivo padrão `dataset/synthetic_logs.json` se não especificado
- Gera relatórios na pasta `reports/`

### run_with_puter.sh

Script principal para executar análise com todos os modos (incluindo Claude e ChatGPT gratuitos via Puter):

```bash
./run_with_puter.sh
```

**Funcionalidades:**
- Inicia Puter Bridge automaticamente em background
- Executa análise com todos os 5 modos disponíveis
- Gera relatórios separados em `reports/`
- Mantém Puter rodando para próximas execuções

### start_puter.sh

Inicia o Puter Bridge em background:

```bash
./start_puter.sh
```

**Processo:**
1. Abre navegador para autenticação (primeira vez)
2. Inicia servidor Node.js em http://localhost:3000
3. Salva PID em `.puter.pid` para controle

### stop_puter.sh

Para o Puter Bridge:

```bash
./stop_puter.sh
```

**Ação:**
- Encerra processo usando PID salvo
- Remove arquivo `.puter.pid`

---

## Integração com Puter.js (Claude e ChatGPT Gratuitos)

### 📖 O que é Puter.js?

[Puter.js](https://docs.puter.com) é uma biblioteca JavaScript que oferece acesso **gratuito e ilimitado** a modelos de IA avançados, permitindo usar Claude Sonnet 4 e GPT-5.4 sem custos.

### 🏗️ Arquitetura do Bridge

Como Puter.js é uma biblioteca JavaScript e este projeto é Python, criamos uma **arquitetura de ponte (bridge)**:

```
┌─────────────────────────────────────────────────────────┐
│                  Python Application                     │
│           (Excessive Logs Analyzer)                     │
│                                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │  src/utils/llm_client.py                     │      │
│  │  • LLMClient(provider='puter')               │      │
│  └────────────────┬─────────────────────────────┘      │
│                   │ HTTP Request                       │
│  ┌────────────────▼─────────────────────────────┐      │
│  │  src/utils/puter_client.py                   │      │
│  │  • PuterClient()                             │      │
│  │  • Faz chamadas HTTP                         │      │
│  └────────────────┬─────────────────────────────┘      │
└───────────────────┼─────────────────────────────────────┘
                    │
                    │ POST http://localhost:3000/ai/chat
                    │
┌───────────────────▼─────────────────────────────────────┐
│            Node.js Bridge Server                        │
│              (puter-bridge/)                            │
│                                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │  server.js (Express API)                     │      │
│  │  • Recebe requisições HTTP                   │      │
│  │  • Converte para formato Puter.js           │      │
│  └────────────────┬─────────────────────────────┘      │
│                   │                                    │
│  ┌────────────────▼─────────────────────────────┐      │
│  │  @heyputer/puter.js                          │      │
│  │  • puter.ai.chat()                           │      │
│  │  • Autenticação com Puter                    │      │
│  └────────────────┬─────────────────────────────┘      │
└───────────────────┼─────────────────────────────────────┘
                    │
                    │ WebSocket/API
                    │
┌───────────────────▼─────────────────────────────────────┐
│                  Puter Cloud                            │
│         (https://puter.com)                             │
│                                                         │
│  • GPT-5.4 Nano                                         │
│  • Claude Sonnet 4                                      │
│  • Gemini 2.5 Flash Lite                                │
│  • 500+ outros modelos                                  │
└─────────────────────────────────────────────────────────┘
```

### 🎯 Vantagens

✅ **100% Gratuito** - Claude e ChatGPT sem custos  
✅ **Sem API Keys próprias** - Não precisa pagar Anthropic ou OpenAI  
✅ **Acesso ilimitado** - Sem limites de requisições (fair use)  
✅ **Múltiplos modelos** - Claude, GPT, Gemini e 500+ outros  

### 📡 Endpoints do Bridge

**Chat com IA:**
```bash
POST http://localhost:3000/ai/chat
Content-Type: application/json

{
  "prompt": "Analise estes logs...",
  "model": "claude-sonnet-4",
  "stream": false
}
```

**Listar modelos:**
```bash
GET http://localhost:3000/ai/models
```

**Health check:**
```bash
GET http://localhost:3000/health
```

---

## Integração com APIs de IA

A ferramenta suporta múltiplos provedores de LLM, priorizando opções gratuitas:

### Provedores Gratuitos (Recomendado) 🆓

**1. Groq API**
- **Modelo:** Llama 3.3 70B Versatile
- **Velocidade:** Extremamente rápido (2-5s por análise)
- **Limites:** 30 RPM, 14.400 RPD
- **Qualidade:** Alta (⭐⭐⭐⭐)
- **API Key:** Obter em https://console.groq.com
- **Variável de ambiente:** `GROQ_API_KEY`

**2. Google Gemini API**
- **Modelo:** Gemini 1.5 Flash
- **Velocidade:** Rápido (4-8s por análise)
- **Limites:** 15 RPM, 1M tokens/mês
- **Qualidade:** Muito alta (⭐⭐⭐⭐⭐)
- **API Key:** Obter em https://aistudio.google.com/app/apikey
- **Variável de ambiente:** `GOOGLE_API_KEY`

### Provedores Pagos (Opcional) 💰

**3. Puter.js (Claude + ChatGPT Gratuitos)**
- **Modelos:** Claude Sonnet 4, GPT-5.4 Nano, Gemini 2.5 Flash Lite
- **Velocidade:** Moderado (5-15s por análise)
- **Qualidade:** Muito alta (⭐⭐⭐⭐⭐)
- **Custo:** **GRATUITO** 🎉
- **Setup:** Veja seção "Integração com Puter.js" acima
- **Variável de ambiente:** `PUTER_BRIDGE_URL`

**4. Anthropic Claude API (Pago - Opcional)**
- **Modelo padrão:** Claude 3.5 Sonnet
- **Prompt caching:** Ativo (~90% redução de custo)
- **Velocidade:** Moderado (5-15s por análise)
- **Qualidade:** Muito alta (⭐⭐⭐⭐⭐)
- **Custo:** ~$0.003-0.01 por análise
- **Variável de ambiente:** `ANTHROPIC_API_KEY`
- **Nota:** Use Puter.js para Claude gratuito

**5. OpenAI ChatGPT API (Pago - Opcional)**
- **Modelo padrão:** GPT-4o
- **Velocidade:** Moderado (5-15s por análise)
- **Qualidade:** Muito alta (⭐⭐⭐⭐⭐)
- **Custo:** ~$0.005-0.015 por análise
- **Variável de ambiente:** `OPENAI_API_KEY`
- **Nota:** Use Puter.js para GPT gratuito

### Análise sem IA (Standard)

- **Baseada em regras** e thresholds estatísticos
- **Sempre disponível** (não requer API keys)
- **Velocidade:** Muito rápido (< 1s)
- **Qualidade:** Boa para detecções básicas (⭐⭐⭐)
- **Ideal para:** Análises rápidas, ambientes sem internet, testes

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```bash
# APIs Gratuitas (recomendado)
GROQ_API_KEY=sua_chave_groq_aqui
GOOGLE_API_KEY=sua_chave_google_aqui

# Puter Bridge (Claude e ChatGPT gratuitos)
PUTER_BRIDGE_URL=http://localhost:3000

# APIs Pagas (opcional - não necessário se usar Puter)
# ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
# OPENAI_API_KEY=sua_chave_openai_aqui
```

**Nota:** A aplicação automaticamente detecta quais APIs estão configuradas e executa análises apenas com os provedores disponíveis.

---

## Extensibilidade

### Adicionar Novo Analyzer

1. Criar arquivo em `src/analyzers/`
2. Implementar método `analyze(logs, ...) -> Dict`
3. Retornar estrutura padrão com `severity`, `issues`, `recommendations`
4. Registrar em `main.py`

### Adicionar Novo Provedor LLM

1. Adicionar import em `llm_client.py`
2. Implementar método `_init_<provider>()`
3. Implementar método `_analyze_<provider>()`
4. Atualizar `__init__()` e `analyze_with_caching()`
5. Adicionar inicialização em `main.py` (ExcessiveLogsAnalyzer.__init__)
6. Executar `./run_with_puter.sh` para testar o novo modo

### Customizar Thresholds

Editar constantes nos arquivos de analyzer:
- `log_level_analyzer.py`: níveis
- `unnecessary_logs_detector.py`: duplicatas
- `sampling_recommender.py`: volume

---

## Performance

### Otimizações

- **Prompt Caching (Claude):** ~90% redução de custo em análises repetidas
- **Execução paralela:** Todos os provedores executam simultaneamente
- **Lazy loading:** LLMs carregados apenas se API keys disponíveis
- **Reutilização de dados:** Estatísticas calculadas uma única vez para todos os modos

### Benchmarks

| Operação | Tempo (1000 logs) |
|----------|-------------------|
| Load logs | < 100ms |
| Stats processing | < 200ms |
| Analysis (standard) | < 500ms |
| Analysis (Groq) | 2-5s ⚡ |
| Analysis (Gemini) | 4-8s |
| Analysis (Claude) | 5-15s |
| Analysis (ChatGPT) | 5-15s |
| Total (standard) | < 1s |
| Total (Groq) | 3-6s |
| Total (Gemini) | 5-9s |
| Total (Claude/ChatGPT) | 6-16s |
| **Total (Todos os modos)** | 15-30s (paralelo) |

### Custos

| Provedor | Custo por Análise | Limites |
|----------|------------------|---------|
| **Groq** | **GRATUITO** | 30 RPM, 14.400 RPD |
| **Gemini** | **GRATUITO** | 15 RPM, 1M tokens/mês |
| Claude | ~$0.003-0.01 | Pay-per-use |
| ChatGPT | ~$0.005-0.015 | Pay-per-use |
| Standard | GRATUITO | Sem limites |

---

## Histórico de Versões

### Versão 3.0 (Abril 2026)
- ✅ Adicionado suporte a **Groq API** (Llama 3.3 70B) - GRATUITO
- ✅ Adicionado suporte a **Google Gemini API** (Gemini 1.5 Flash) - GRATUITO
- ✅ Refatoração para **execução paralela** de todos os provedores
- ✅ Novo script `run_analysis.sh` para análise simplificada
- ✅ Scripts `run_with_puter.sh`, `start_puter.sh` e `stop_puter.sh` para gerenciamento do Puter Bridge
- ✅ Geração de múltiplos relatórios independentes por provedor
- ✅ Relatório comparativo consolidado
- ✅ Priorização de APIs gratuitas

### Versão 2.0 (Abril 2026)
- Suporte a Claude API e ChatGPT API
- Implementação das 3 soluções principais
- Prompt caching para Claude

### Versão 1.0
- Versão inicial com análise Standard (sem IA)

---

**Versão Atual:** 3.0  
**Última Atualização:** 26 de Abril de 2026
