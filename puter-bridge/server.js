#!/usr/bin/env node
/**
 * Servidor HTTP Bridge para Puter.js
 * Expõe API REST para consumo pelo cliente Python
 */

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { init } from "@heyputer/puter.js/src/init.cjs";

// Carrega variáveis de ambiente
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());
app.use(express.json({ limit: "10mb" }));

// Inicializa Puter.js
let puter = null;

try {
  const authToken = process.env.PUTER_AUTH_TOKEN;

  if (!authToken) {
    console.error("❌ PUTER_AUTH_TOKEN não encontrado no .env");
    console.error("   Execute: npm run auth");
    process.exit(1);
  }

  puter = init(authToken);
  console.log("✅ Puter.js inicializado com sucesso");
} catch (error) {
  console.error("❌ Erro ao inicializar Puter.js:", error.message);
  process.exit(1);
}

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "puter-bridge",
    version: "1.0.0",
    puterInitialized: !!puter
  });
});

// Endpoint principal: Chat com IA
app.post("/ai/chat", async (req, res) => {
  try {
    const {
      prompt,
      messages,
      model = "gpt-5.4-nano",
      stream = false,
      max_tokens,
      temperature,
      tools
    } = req.body;

    if (!prompt && !messages) {
      return res.status(400).json({
        error: "Parâmetro 'prompt' ou 'messages' é obrigatório"
      });
    }

    // Monta opções
    const options = {
      model,
      stream
    };

    if (max_tokens) options.max_tokens = max_tokens;
    if (temperature !== undefined) options.temperature = temperature;
    if (tools) options.tools = tools;

    console.log(`📤 Requisição recebida - Modelo: ${model}, Stream: ${stream}`);

    // Faz chamada ao Puter.js
    const input = messages || prompt;

    if (stream) {
      // Streaming response
      res.setHeader("Content-Type", "text/event-stream");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");

      const response = await puter.ai.chat(input, options);

      for await (const chunk of response) {
        const data = {
          text: chunk?.text || "",
          message: chunk?.message || null,
          finish_reason: chunk?.finish_reason || null
        };
        res.write(`data: ${JSON.stringify(data)}\n\n`);
      }

      res.write("data: [DONE]\n\n");
      res.end();

    } else {
      // Resposta única
      const response = await puter.ai.chat(input, options);

      res.json({
        success: true,
        model: model,
        response: {
          text: response?.text || response?.message?.content || "",
          message: response?.message || null,
          usage: response?.usage || null,
          finish_reason: response?.finish_reason || null
        }
      });
    }

    console.log(`✅ Resposta enviada com sucesso`);

  } catch (error) {
    console.error("❌ Erro ao processar chat:", error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      stack: process.env.NODE_ENV === "development" ? error.stack : undefined
    });
  }
});

// Lista modelos disponíveis
app.get("/ai/models", (req, res) => {
  res.json({
    success: true,
    models: [
      {
        id: "gpt-5.4-nano",
        provider: "openai",
        description: "GPT-5.4 Nano - Rápido e eficiente",
        context_window: 1000000
      },
      {
        id: "gpt-5.3-chat",
        provider: "openai",
        description: "GPT-5.3 Chat - Menos alucinações",
        context_window: 128000
      },
      {
        id: "claude-sonnet-4",
        provider: "anthropic",
        description: "Claude Sonnet 4",
        context_window: 200000
      },
      {
        id: "gemini-2.5-flash-lite",
        provider: "google",
        description: "Gemini 2.5 Flash Lite",
        context_window: 1000000
      }
    ]
  });
});

// Tratamento de erros
app.use((err, req, res, next) => {
  console.error("❌ Erro não tratado:", err);
  res.status(500).json({
    success: false,
    error: "Erro interno do servidor",
    message: err.message
  });
});

// Inicia servidor
app.listen(PORT, () => {
  console.log("");
  console.log("🚀 Puter Bridge Server iniciado!");
  console.log(`📡 Servidor rodando em: http://localhost:${PORT}`);
  console.log(`🔍 Health check: http://localhost:${PORT}/health`);
  console.log(`💬 Chat endpoint: POST http://localhost:${PORT}/ai/chat`);
  console.log("");
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("⏹️  Encerrando servidor...");
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("⏹️  Encerrando servidor...");
  process.exit(0);
});
