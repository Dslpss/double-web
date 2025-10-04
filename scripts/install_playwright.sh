#!/bin/bash

# Script para instalar Playwright com dependências
# Necessário para Railway e outros ambientes de produção

echo "🎭 Instalando Playwright e dependências..."

# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install chromium

# Instalar dependências do sistema (necessário para Railway)
playwright install-deps chromium

echo "✅ Playwright instalado com sucesso!"
echo "🔧 Navegador Chromium configurado"
echo "🚀 Pronto para usar no Railway!"
