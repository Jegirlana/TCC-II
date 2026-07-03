# Puter Bridge - Node.js HTTP API Wrapper

Servidor Node.js que expõe a API do Puter.js via HTTP REST para consumo por aplicações Python.

## 🎯 O que é isso?

O Puter.js é uma biblioteca JavaScript que oferece acesso gratuito e ilimitado a modelos de IA (GPT-5.4, Claude, Gemini, etc.) sem necessidade de API keys próprias. Este wrapper permite usar essas funcionalidades em aplicações Python.

## 📦 Instalação

```bash
cd puter-bridge
npm install
```

## 🔐 Autenticação

Antes de usar, você precisa autenticar com o Puter:

```bash
npm run auth
```

Isso abrirá uma janela do navegador para login. Após autenticar, o token será salvo automaticamente em `.env`.

## 🚀 Executando o Servidor

```bash
npm start
```

O servidor iniciará em `http://localhost:3000`

## 📡 API Endpoints

### Health Check

```bash
GET http://localhost:3000/health
```

### Chat com IA

```bash
POST http://localhost:3000/ai/chat
Content-Type: application/json

{
  "prompt": "Explique inteligência artificial em 2 frases",
  "model": "gpt-5.4-nano",
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Parâmetros:**

- `prompt` (string, obrigatório se não usar messages): Texto do prompt
- `messages` (array, opcional): Array de mensagens no formato chat
- `model` (string, padrão: "gpt-5.4-nano"): Modelo a usar
- `stream` (boolean, padrão: false): Streaming de resposta
- `temperature` (float, opcional): Controle de aleatoriedade (0-2)
- `max_tokens` (int, opcional): Limite de tokens
- `tools` (array, opcional): Function calling

**Modelos Disponíveis:**

- `gpt-5.4-nano` - OpenAI GPT-5.4 Nano (recomendado)
- `gpt-5.3-chat` - OpenAI GPT-5.3 Chat
- `claude-sonnet-4` - Anthropic Claude Sonnet 4
- `gemini-2.5-flash-lite` - Google Gemini 2.5 Flash Lite

### Listar Modelos

```bash
GET http://localhost:3000/ai/models
```

## 🐍 Uso com Python

Veja o arquivo `src/utils/puter_client.py` no diretório principal do projeto.

Exemplo básico:

```python
import requests

response = requests.post("http://localhost:3000/ai/chat", json={
    "prompt": "O que é vida?",
    "model": "gpt-5.4-nano"
})

data = response.json()
print(data["response"]["text"])
```

## 💡 Exemplo com Streaming

```python
import requests

response = requests.post(
    "http://localhost:3000/ai/chat",
    json={
        "prompt": "Conte uma história curta",
        "model": "gpt-5.4-nano",
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = line_str[6:]
            if data != '[DONE]':
                import json
                chunk = json.loads(data)
                print(chunk.get('text', ''), end='', flush=True)
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
PUTER_AUTH_TOKEN=seu_token_aqui
PORT=3000
NODE_ENV=production
```

### Function Calling

```json
{
  "prompt": "Qual o clima em Paris?",
  "model": "gpt-5.4-nano",
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Obtém clima de uma localidade",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "Cidade ou localização"
          }
        },
        "required": ["location"]
      }
    }
  }]
}
```

## 📝 Logs

O servidor registra todas as requisições:

```
📤 Requisição recebida - Modelo: gpt-5.4-nano, Stream: false
✅ Resposta enviada com sucesso
```

## ⚠️ Limitações

- O servidor deve estar rodando para o Python fazer chamadas
- Requer autenticação inicial via navegador
- Depende da disponibilidade do serviço Puter.com

## 🔗 Links Úteis

- [Documentação Puter.js](https://docs.puter.com)
- [Puter Developer](https://developer.puter.com)
- [Tutorial OpenAI API Gratuita](https://developer.puter.com/tutorials/free-unlimited-openai-api/)

## 📄 Licença

MIT
