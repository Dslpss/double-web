#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste simples para verificar se a integração está funcionando
"""

import os
import sys
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todos os imports estão funcionando."""
    logger.info("🧪 Testando imports...")
    
    try:
        # Testar Playwright
        from playwright.async_api import async_playwright
        logger.info("✅ Playwright importado com sucesso")
        
        # Testar WebSocket
        import websocket
        logger.info("✅ websocket-client importado com sucesso")
        
        # Testar Flask-SocketIO
        from flask_socketio import SocketIO
        logger.info("✅ Flask-SocketIO importado com sucesso")
        
        # Testar nosso analisador
        from shared.pragmatic_analyzer import PragmaticAnalyzer
        logger.info("✅ PragmaticAnalyzer importado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar: {e}")
        return False

async def test_playwright():
    """Testa se Playwright está funcionando."""
    logger.info("🧪 Testando Playwright...")
    
    try:
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Testar navegação simples
        await page.goto("https://www.google.com")
        title = await page.title()
        
        await browser.close()
        await playwright.stop()
        
        logger.info(f"✅ Playwright funcionando! Título da página: {title}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no Playwright: {e}")
        return False

def test_websocket():
    """Testa se WebSocket está funcionando."""
    logger.info("🧪 Testando WebSocket...")
    
    try:
        import websocket
        
        # Testar criação de WebSocket
        ws = websocket.WebSocket()
        logger.info("✅ WebSocket criado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}")
        return False

def test_analyzer():
    """Testa se o analisador pode ser criado."""
    logger.info("🧪 Testando PragmaticAnalyzer...")
    
    try:
        from shared.pragmatic_analyzer import PragmaticAnalyzer
        
        # Criar instância
        analyzer = PragmaticAnalyzer("test@example.com", "testpass")
        logger.info("✅ PragmaticAnalyzer criado com sucesso")
        
        # Testar status
        status = analyzer.get_status()
        logger.info(f"✅ Status do analisador: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no PragmaticAnalyzer: {e}")
        return False

async def main():
    """Função principal de teste."""
    logger.info("🚀 Iniciando testes simples...")
    logger.info("=" * 50)
    
    # Teste 1: Imports
    if not test_imports():
        logger.error("❌ Teste de imports falhou!")
        return
    
    # Teste 2: Playwright
    if not await test_playwright():
        logger.error("❌ Teste do Playwright falhou!")
        return
    
    # Teste 3: WebSocket
    if not test_websocket():
        logger.error("❌ Teste do WebSocket falhou!")
        return
    
    # Teste 4: Analisador
    if not test_analyzer():
        logger.error("❌ Teste do PragmaticAnalyzer falhou!")
        return
    
    logger.info("=" * 50)
    logger.info("🎉 Todos os testes passaram!")
    logger.info("\n📋 Próximos passos:")
    logger.info("   1. Configure suas credenciais no .env")
    logger.info("   2. Execute: python backend/websocket_app.py")
    logger.info("   3. Acesse: http://localhost:5000")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
