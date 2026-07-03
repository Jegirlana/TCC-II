#!/usr/bin/env node
/**
 * Script de autenticação do Puter.js
 * Executa o processo de login via navegador e salva o token no .env
 */

import { getAuthToken } from "@heyputer/puter.js/src/init.cjs";
import { writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function authenticate() {
  console.log("🔐 Iniciando autenticação do Puter.js...");
  console.log("📱 Uma janela do navegador será aberta para login.");
  console.log("");

  try {
    const authToken = await getAuthToken();

    if (!authToken) {
      console.error("❌ Falha ao obter token de autenticação");
      process.exit(1);
    }

    // Salva o token no arquivo .env
    const envPath = join(__dirname, ".env");
    const envContent = `PUTER_AUTH_TOKEN=${authToken}\n`;

    writeFileSync(envPath, envContent);

    console.log("");
    console.log("✅ Autenticação bem-sucedida!");
    console.log(`📝 Token salvo em: ${envPath}`);
    console.log("");
    console.log("🚀 Agora você pode executar: npm start");

  } catch (error) {
    console.error("❌ Erro durante autenticação:", error.message);
    process.exit(1);
  }
}

authenticate();
