# Excessive Logs Analyzer

Ferramenta de análise de logs para identificar e mitigar o antipadrão "Excessive Logs" usando Large Multimodal Models (LMMs).

## Descrição

Esta ferramenta implementa 3 soluções principais sobre o antipadrão "Excessive Logs":

### 1. **Análise de Níveis de Log** (Use log levels effectively)
- Detecta uso inadequado de níveis de log (DEBUG em produção, excesso de INFO, etc.)
- Identifica serviços com distribuição problemática
- Recomenda ajustes de configuração por ambiente

### 2. **Detecção de Logs Desnecessários** (Log only what's necessary)
- Identifica logs de assets estáticos
- Detecta logs de operações triviais bem-sucedidas
- Encontra padrões excessivamente duplicados
- Calcula potencial de redução de volume

### 3. **Recomendação de Sampling** (Implement log sampling)
- Analisa volume e taxa de logs
- Recomenda estratégias de amostragem (rate-based, time-based, adaptive, priority-based)
- Fornece configurações específicas por serviço
- Estima redução de custos

## Requisitos

```bash
pip install -r requirements.txt
```

## Configuração

### 🆓 Opção 1: APIs Gratuitas (Recomendado)

**Configure Groq e/ou Google Gemini** para análises com IA totalmente gratuitas:

```bash
# Groq API (GRATUITO - 30 RPM, 14.400 RPD)
GROQ_API_KEY=sua_chave_groq_aqui

# Google Gemini API (GRATUITO - 15 RPM, 1M tokens/mês)
GOOGLE_API_KEY=sua_chave_google_aqui
```

📖 **[Como obter as API keys gratuitas](COMO_OBTER_API_KEYS_GRATUITAS.md)**

### 💰 Opção 2: APIs Pagas (Opcional)

```bash
# Claude/Anthropic API (PAGO)
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui

# OpenAI/ChatGPT API (PAGO)
OPENAI_API_KEY=sua_chave_openai_aqui
```

## Modos de Análise

A ferramenta executa **até 5 análises simultaneamente**:

| Modo | Descrição | Custo | Qualidade |
|------|-----------|-------|-----------|
| **Groq** 🆓 | Llama 3.3 (70B) - Extremamente rápido | **Gratuito** | ⭐⭐⭐⭐ |
| **Gemini** 🆓 | Google Gemini 1.5 Flash | **Gratuito** | ⭐⭐⭐⭐⭐ |
| **Claude** 🆓 | **SEMPRE via Puter (Claude Sonnet 4)** | **Gratuito** | ⭐⭐⭐⭐⭐ |
| **ChatGPT** 🆓 | **SEMPRE via Puter (GPT-5.4)** | **Gratuito** | ⭐⭐⭐⭐⭐ |
| `standard` | Análise estatística sem IA | Gratuito | ⭐⭐⭐ |

**🎯 CONFIGURAÇÃO ATUAL:**
- **Claude & ChatGPT:** Configurados para **SEMPRE usar Puter (100% gratuito)**
- Não é mais necessário configurar `ANTHROPIC_API_KEY` ou `OPENAI_API_KEY`
- Basta ter o Puter Bridge rodando para acessar Claude e ChatGPT gratuitamente

**✅ RESULTADO**: **5 análises com IA 100% gratuitas** (Groq + Gemini + Claude via Puter + ChatGPT via Puter + Standard)!

## Uso

### 🚀 Método 1: Com Puter (Recomendado - Claude + ChatGPT Gratuitos)

```bash
./run_with_puter.sh
```

Este script:
- ✅ Inicia automaticamente o Puter Bridge em background
- ✅ Executa Claude e ChatGPT via Puter (100% gratuito)
- ✅ Continua rodando em background para próximas execuções

**Para parar o Puter Bridge:**
```bash
./stop_puter.sh
```

Ou especificar um arquivo diferente:
```bash
./run_with_puter.sh caminho/para/seu/arquivo.json
```

### Método 2: Script básico (sem Claude/ChatGPT)

```bash
./run_analysis.sh
```

Este script executa apenas Groq + Gemini + Standard (Claude/ChatGPT requerem Puter Bridge rodando)

### Método 2: Comando direto

```bash
# Usando o ambiente virtual
venv/bin/python3 src/main.py dataset/synthetic_logs.json
```

### Especificar nome customizado para os relatórios

```bash
venv/bin/python3 src/main.py dataset/synthetic_logs.json -o meu_relatorio
```

Isso irá gerar na pasta `reports/`:
- `meu_relatorio_groq.json` - Análise com Groq (GRATUITO)
- `meu_relatorio_gemini.json` - Análise com Google Gemini (GRATUITO)
- `meu_relatorio_claude_ai.json` - Análise com Claude AI
- `meu_relatorio_chatgpt.json` - Análise com ChatGPT
- `meu_relatorio_sem_ia.json` - Análise sem IA
- `meu_relatorio_comparativo.json` - Relatório comparativo

**Nota Importante**: 
- Os arquivos são **sobrescritos** a cada execução (não são criados timestamps)
- A aplicação executa **todas as análises disponíveis** (APIs configuradas)
- Use o parâmetro `-o` para gerar relatórios com nomes diferentes se quiser manter versões anteriores

## Formato de Log

A ferramenta espera logs no seguinte formato JSON:

```json
{
  "timestamp": "2026-04-14T23:18:52.773Z",
  "level": "ERROR",
  "service": "customers-service",
  "instance": "pod-1768",
  "request_id": "req-4e9875",
  "trace_id": "9d1f0e9cdc4a",
  "message": "Failed to fetch customer 169: timeout",
  "http": {
    "method": "GET",
    "path": "/customers/169",
    "status_code": 504
  },
  "error": {
    "type": "TimeoutException",
    "message": "timeout"
  },
  "tags": ["customer", "read", "timeout"]
}
```

## Geração de Logs Sintéticos

Para gerar logs sintéticos para teste:

```bash
cd dataset
python3 generate_synthetic_logs.py
```

Isso criará um arquivo `synthetic_logs.json` com ~1000 logs seguindo o padrão definido.

## Estrutura do Projeto

```
.
├── dataset/
│   ├── log_model.json              # Modelo/schema do formato de log
│   ├── generate_synthetic_logs.py  # Gerador de logs sintéticos
│   └── synthetic_logs.json         # Logs gerados (após execução)
├── src/
│   ├── analyzers/
│   │   ├── log_level_analyzer.py          # Análise de níveis de log
│   │   ├── unnecessary_logs_detector.py   # Detecção de logs desnecessários
│   │   └── sampling_recommender.py        # Recomendação de sampling
│   ├── utils/
│   │   ├── llm_client.py           # Cliente multi-LLM (Groq, Gemini, Claude, ChatGPT)
│   │   └── log_processor.py        # Processamento e estatísticas
│   └── main.py                     # Script principal
├── .env.example                    # Exemplo de configuração
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

## Saída da Análise

A ferramenta gera **até 6 arquivos JSON** na pasta `reports/` (sobrescreve a cada execução):

### 🆓 Análises Gratuitas:

1. **`synthetic_logs_groq.json`** - Análise com Groq (Llama 3.1)
   - Estatísticas gerais dos logs
   - Análise com IA extremamente rápida
   - **100% GRATUITO**

2. **`synthetic_logs_gemini.json`** - Análise com Google Gemini
   - Análise de alta qualidade
   - Issues identificados com severidade
   - **100% GRATUITO**

### 💰 Análises Pagas (opcional):

3. **`synthetic_logs_claude_ai.json`** - Análise com Claude AI
4. **`synthetic_logs_chatgpt.json`** - Análise com ChatGPT

### 📊 Análise Básica:

5. **`synthetic_logs_sem_ia.json`** - Análise sem IA (estatísticas)
   - Baseada em regras e thresholds
   - Não requer API keys

### 📈 Relatório Consolidado:

6. **`synthetic_logs_comparativo.json`** - Comparação de todos os modos

⚠️ **Atenção**: Os arquivos são automaticamente **sobrescritos** a cada nova execução. Use o parâmetro `-o nome_customizado` se precisar manter versões antigas dos relatórios.

**Resumo no console** com:
- Tabela comparativa entre os 3 modos
- Health Score (0-100) de cada análise
- Severidade geral
- Ações prioritárias
- Estatísticas detalhadas por modo

## Exemplo de Saída

```
🔍 Analisando logs de: dataset/synthetic_logs.json
  ✓ 1036 logs carregados
  ✓ Estatísticas processadas

  📊 Executando Análise 1: Efetividade dos Níveis de Log...
  ✓ Encontrados 2 issues

  🔎 Executando Análise 2: Detecção de Logs Desnecessários...
  ✓ Potencial de redução: 45.2%

  📈 Executando Análise 3: Recomendações de Sampling...
  ✓ 3 estratégias recomendadas

================================================================================
RESUMO DA ANÁLISE DE LOGS EXCESSIVOS
================================================================================

📊 Total de logs analisados: 1036
⏱️  Taxa: 45.3 logs/min
🏥 Health Score: 60/100
⚠️  Severidade: MEDIUM
📋 Issues encontrados: 8

🎯 AÇÕES PRIORITÁRIAS:
  1. Remover logs desnecessários
     → Potencial de redução de 45.2%
  2. Implementar sampling
     → Volume de logs requer sampling
```

## Métricas e Thresholds

### Níveis de Log
- INFO < 70% do total
- DEBUG < 5% em produção
- ERROR >= 1% do total
- WARN >= 5% do total

### Volume
- Normal: < 50 logs/min
- Moderado: 50-100 logs/min
- Alto: 100-500 logs/min (sampling recomendado)
- Crítico: > 500 logs/min (sampling urgente)

### Redução Potencial
- Low: < 15%
- Medium: 15-30%
- High: 30-50%
- Critical: > 50%

## Integração com Claude API

A ferramenta utiliza a Claude API (Anthropic) para análise avançada:

- **Modelo padrão**: `claude-sonnet-4-6`
- **Prompt caching**: Otimiza custos em análises repetitivas
- **Análise contextual**: LLM analisa padrões e fornece insights específicos

## 📚 Documentação

A documentação completa está organizada nos seguintes arquivos:

- **[Início Rápido](docs/INICIO_RAPIDO.md)** - Configure e execute em 3 minutos (5 análises gratuitas)
- **[Guia de Uso](docs/GUIA_USO.md)** - Como instalar, configurar e usar a ferramenta
- **[Arquitetura](docs/ARQUITETURA.md)** - Documentação técnica, arquitetura e integração Puter
- **[Tabela de Comparação](docs/TABELA_COMPARACAO.md)** - Comparação entre os diferentes modos de análise

## 🧪 Testando

```bash
# Executar análise com todos os modos
./run_with_puter.sh

# Ver status do Puter Bridge
curl http://localhost:3000/health

# Parar o Puter Bridge
./stop_puter.sh
```

## Licença

MIT

## Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.
