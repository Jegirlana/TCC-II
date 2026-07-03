"""
Cliente Python para Puter Bridge API
Comunica com o servidor Node.js que expõe Puter.js via HTTP
"""

import os
import requests
import json
from typing import Optional, List, Dict, Any, Iterator


class PuterClient:
    """Cliente para comunicação com Puter Bridge API."""

    def __init__(self, base_url: str = None, timeout: int = 120):
        """
        Inicializa cliente Puter.

        Args:
            base_url: URL base do servidor Puter Bridge (padrão: http://localhost:3000)
            timeout: Timeout para requisições em segundos (padrão: 120)
        """
        self.base_url = base_url or os.getenv("PUTER_BRIDGE_URL", "http://localhost:3000")
        self.timeout = timeout
        self._verify_connection()

    def _verify_connection(self):
        """Verifica se o servidor Puter Bridge está acessível."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            if data.get("status") != "ok":
                raise ConnectionError("Puter Bridge não está saudável")

            if not data.get("puterInitialized"):
                raise ConnectionError("Puter.js não está inicializado no servidor")

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Não foi possível conectar ao Puter Bridge em {self.base_url}. "
                "Certifique-se de que o servidor está rodando (npm start)"
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro ao verificar Puter Bridge: {e}")

    def chat(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-5.4-nano",
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia prompt ou mensagens para o modelo de IA.

        Args:
            prompt: Texto do prompt (obrigatório se messages não for fornecido)
            messages: Lista de mensagens no formato chat (opcional)
            model: Nome do modelo a usar (padrão: gpt-5.4-nano)
            stream: Se True, retorna iterator para streaming (padrão: False)
            temperature: Controle de aleatoriedade 0-2 (opcional)
            max_tokens: Limite de tokens na resposta (opcional)
            tools: Definições de ferramentas para function calling (opcional)

        Returns:
            Dict com resposta da IA ou Iterator se stream=True

        Raises:
            ValueError: Se nem prompt nem messages forem fornecidos
            requests.RequestException: Se houver erro na comunicação
        """
        if not prompt and not messages:
            raise ValueError("Forneça 'prompt' ou 'messages'")

        payload = {
            "model": model,
            "stream": stream
        }

        if prompt:
            payload["prompt"] = prompt
        if messages:
            payload["messages"] = messages
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools

        if stream:
            return self._chat_stream(payload)
        else:
            return self._chat_normal(payload)

    def _chat_normal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executa chat sem streaming."""
        try:
            response = requests.post(
                f"{self.base_url}/ai/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Requisição ao Puter Bridge excedeu {self.timeout}s"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erro na requisição ao Puter Bridge: {e}")

    def _chat_stream(self, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Executa chat com streaming."""
        try:
            response = requests.post(
                f"{self.base_url}/ai/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = line_str[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Requisição ao Puter Bridge excedeu {self.timeout}s"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erro na requisição ao Puter Bridge: {e}")

    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extrai texto da resposta, tratando diferentes formatos.

        Claude retorna: {"response": {"text": [{"type": "text", "text": "..."}]}}
        ChatGPT retorna: {"response": {"text": "..."}}

        Args:
            response: Resposta do servidor Puter Bridge

        Returns:
            Texto extraído da resposta
        """
        try:
            response_data = response.get("response", {})
            text = response_data.get("text", "")

            # Se text for uma lista (Claude), extrair o texto do primeiro item
            if isinstance(text, list) and len(text) > 0:
                if isinstance(text[0], dict):
                    return text[0].get("text", "")
                return str(text[0])

            # Se text for string (ChatGPT), retornar diretamente
            if isinstance(text, str):
                return text

            # Fallback: tentar extrair de message.content
            message = response_data.get("message", {})
            content = message.get("content", "")
            if isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], dict):
                    return content[0].get("text", "")

            return ""

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair texto da resposta: {e}")

    def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista modelos disponíveis.

        Returns:
            Lista de dicionários com informações dos modelos
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai/models",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erro ao listar modelos: {e}")

    def analyze_with_caching(
        self,
        system_prompt: str,
        user_prompt: str,
        cached_content: str,
        model: str = "gpt-5.4-nano"
    ) -> str:
        """
        Analisa usando formato compatível com outros LLMs do projeto.

        Args:
            system_prompt: Prompt de sistema
            user_prompt: Prompt do usuário
            cached_content: Conteúdo a ser cacheado (não suportado pelo Puter)
            model: Modelo a usar

        Returns:
            Texto da resposta
        """
        # Puter não tem suporte nativo a caching como Claude
        # Concatena tudo em um único prompt
        full_prompt = f"{system_prompt}\n\n{cached_content}\n\n{user_prompt}"

        response = self.chat(
            prompt=full_prompt,
            model=model,
            stream=False
        )

        return self._extract_text_from_response(response)


# Exemplo de uso
if __name__ == "__main__":
    try:
        # Inicializa cliente
        client = PuterClient()

        # Lista modelos disponíveis
        print("📋 Modelos disponíveis:")
        models = client.get_models()
        for model in models:
            print(f"  - {model['id']} ({model['provider']}): {model['description']}")

        print("\n" + "=" * 60)

        # Teste simples
        print("\n💬 Teste simples:")
        response = client.chat(
            prompt="Explique inteligência artificial em 2 frases.",
            model="gpt-5.4-nano"
        )
        print(f"Resposta: {response['response']['text']}")

        print("\n" + "=" * 60)

        # Teste com streaming
        print("\n📡 Teste com streaming:")
        print("Resposta: ", end="", flush=True)
        for chunk in client.chat(
            prompt="Conte uma piada curta sobre programação.",
            model="gpt-5.4-nano",
            stream=True
        ):
            text = chunk.get("text", "")
            print(text, end="", flush=True)
        print("\n")

    except Exception as e:
        print(f"❌ Erro: {e}")
