# 🚀 Início Rápido - 5 Análises com IA 100% Gratuitas

Configure em **3 minutos** para ter todas as análises (Groq + Gemini + Claude + ChatGPT + Standard) **completamente grátis**!

---

## ⚡ Passo 1: Obter API Keys Gratuitas (2 minutos)

### Groq (GRATUITO - 30 RPM)
1. Acesse: https://console.groq.com/
2. Faça login/cadastro (pode usar Google)
3. Vá em "API Keys" → "Create API Key"
4. Copie a chave (começa com `gsk_...`)

### Google Gemini (GRATUITO - 15 RPM)
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API key"
4. Copie a chave (começa com `AIza...`)

---

## ⚡ Passo 2: Configurar no .env (30 segundos)

Abra o arquivo `.env` e cole suas chaves:

```bash
# APIs GRATUITAS
GROQ_API_KEY=gsk_sua_chave_groq_aqui
GOOGLE_API_KEY=AIzaSua_chave_google_aqui

# Claude e ChatGPT usarão Puter automaticamente (não precisa de chaves!)
```

Salve o arquivo!

---

## ⚡ Passo 3: Iniciar a Interface Gráfica

### Linux/Mac

```bash
# (Opcional) Ative Claude e ChatGPT via Puter em um terminal separado
./start_puter.sh

# Inicie a interface gráfica
./start_ui.sh
```

Acesse `http://127.0.0.1:8501` no navegador.

### Windows

```bat
:: (Opcional) Ative Claude e ChatGPT via Puter em uma janela separada
start_puter.bat

:: Inicie a interface gráfica (duplo clique ou pelo Prompt de Comando)
start_ui.bat
```

O navegador abre automaticamente em `http://127.0.0.1:8501`.

---

**O que acontece ao clicar em "Executar Análise":**
1. Os logs são carregados e as estatísticas calculadas
2. Cada provedor selecionado executa as 3 análises independentemente
3. Os resultados aparecem em abas separadas com gráficos e ações prioritárias
4. Os relatórios JSON são salvos automaticamente em `reports/`

---

### Alternativa: Executar via linha de comando com Puter

```bash
./run_with_puter.sh       # Linux/Mac
run_with_puter.bat        # Windows
```

**O que acontece:**
1. 🚀 Puter Bridge inicia automaticamente em background
2. 🌐 Navegador abre para autenticação (primeira vez)
3. ✅ Faça login com Google/GitHub/Email no Puter
4. 🤖 Análise executa com 5 modos de IA gratuitamente!

---

## ✅ Pronto! O que você tem agora:

### 5 Análises com IA - 100% GRATUITO:

1. ✅ **Groq (Llama 3.3)** - Análise extremamente rápida
2. ✅ **Google Gemini** - Análise de alta qualidade
3. ✅ **Claude via Puter** - Claude Sonnet 4 gratuito
4. ✅ **ChatGPT via Puter** - GPT-5.4 Nano gratuito
5. ✅ **Standard** - Análise estatística

**Todos os relatórios em:** `reports/`
- `synthetic_logs_groq.json`
- `synthetic_logs_gemini.json`
- `synthetic_logs_claude_ai.json` (via Puter 🆓)
- `synthetic_logs_chatgpt.json` (via Puter 🆓)
- `synthetic_logs_sem_ia.json`
- `synthetic_logs_comparativo.json`

---

## 📊 Comparação de Custos

| Execução | Antes (APIs pagas) | Agora (Tudo grátis) |
|----------|-------------------|---------------------|
| 1 análise | ~$0.05 | **$0.00** |
| 10 análises | ~$0.50 | **$0.00** |
| 100 análises | ~$5.00 | **$0.00** |

---

## 🔧 Comandos Úteis

### Iniciar interface gráfica

```bash
./start_ui.sh          # Linux/Mac
start_ui.bat           # Windows
```

Acesse `http://127.0.0.1:8501` no navegador.

### Ver relatórios gerados

```bash
ls -lh reports/                        # Linux/Mac
dir reports\                           # Windows
```

### Ver resumo de uma análise

```bash
cat reports/synthetic_logs_claude_ai.json | jq '.overall_assessment'
```

### Parar Puter Bridge

```bash
./stop_puter.sh        # Linux/Mac
stop_puter.bat         # Windows
```

### Ver logs do Puter

```bash
tail -f puter-bridge.log
```

### Executar novamente via linha de comando (Puter já rodando)

```bash
./run_with_puter.sh    # Linux/Mac
run_with_puter.bat     # Windows
```

---

## ❓ Troubleshooting

### Interface não abre / "venv não encontrado"

O ambiente virtual precisa ser criado antes de usar `start_ui.sh` / `start_ui.bat`:

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Porta 8501 já em uso

Edite `start_ui.sh` ou `start_ui.bat` e troque `--server.port 8501` por outra porta (ex: `8502`).

### Erro "Não foi possível inicializar CLAUDE via Puter"

Certifique-se de que o Puter Bridge está rodando:

```bash
curl http://localhost:3000/health    # Linux/Mac
```

Se não estiver, inicie-o:

```bash
./start_puter.sh    # Linux/Mac
start_puter.bat     # Windows
```

### "Porta 3000 em uso"

Mude a porta no `puter-bridge/.env`:

```
PORT=3001
```

E no `.env` principal:

```
PUTER_BRIDGE_URL=http://localhost:3001
```

### Navegador não abre para autenticação do Puter

Execute manualmente:

```bash
cd puter-bridge
npm run auth
```

### API keys Groq/Gemini não funcionam

Verifique se a chave está correta no `.env`:

```bash
cat .env | grep -E "GROQ|GOOGLE"    # Linux/Mac
type .env | findstr "GROQ GOOGLE"   # Windows
```

---

## 🎯 Vantagens da Configuração Atual

| Recurso | Status |
|---------|--------|
| Claude Sonnet 4 | ✅ Gratuito via Puter |
| GPT-5.4 Nano | ✅ Gratuito via Puter |
| Llama 3.3 70B | ✅ Gratuito via Groq |
| Gemini 1.5 Flash | ✅ Gratuito via Google |
| Análise Estatística | ✅ Gratuito (sem IA) |
| **Total de custos** | **$0.00** 🎉 |

---

## 🎓 Próximos Passos

1. ✅ Execute a primeira análise: `./run_with_puter.sh`
2. 📊 Veja os resultados em `reports/`
3. 🔄 Execute quantas vezes quiser - **é tudo grátis!**
4. 📚 Leia a documentação completa: [README.md](../README.md)

---

**Pronto para começar?** Execute `./run_with_puter.sh` agora! 🚀
