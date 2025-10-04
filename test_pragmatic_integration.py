#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para integração Pragmatic Play
Testa local e simula ambiente Railway
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.pragmatic_analyzer import PragmaticAnalyzer, initialize_pragmatic_analyzer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestCallback:
    """Callback para testar recebimento de resultados."""
    
    def __init__(self):
        self.results_received = []
        self.start_time = time.time()
    
    def __call__(self, result):
        """Callback chamado quando resultado é recebido."""
        self.results_received.append(result)
        
        # Log do resultado
        logger.info(f"🎲 Resultado recebido: {result['number']} ({result['color']}) - Multiplicador: {result['multiplier']}")
        
        # Mostrar estatísticas a cada 5 resultados
        if len(self.results_received) % 5 == 0:
            self.show_stats()
    
    def show_stats(self):
        """Mostra estatísticas dos resultados."""
        if not self.results_received:
            return
        
        # Contar cores
        colors = {'red': 0, 'black': 0, 'green': 0}
        for result in self.results_received:
            color = result.get('color', 'unknown')
            if color in colors:
                colors[color] += 1
        
        total = len(self.results_received)
        uptime = time.time() - self.start_time
        
        logger.info(f"📊 Estatísticas - Total: {total}, Tempo: {uptime:.1f}s")
        logger.info(f"   🔴 Vermelho: {colors['red']} ({colors['red']/total*100:.1f}%)")
        logger.info(f"   ⚫ Preto: {colors['black']} ({colors['black']/total*100:.1f}%)")
        logger.info(f"   ⚪ Verde: {colors['green']} ({colors['green']/total*100:.1f}%)")


async def test_pragmatic_analyzer():
    """Testa o PragmaticAnalyzer."""
    logger.info("🧪 Iniciando teste do PragmaticAnalyzer...")
    
    # Verificar credenciais
    username = os.getenv('PLAYNABETS_USER')
    password = os.getenv('PLAYNABETS_PASS')
    
    if not username or not password:
        logger.error("❌ Credenciais não configuradas!")
        logger.error("   Configure PLAYNABETS_USER e PLAYNABETS_PASS no .env")
        return False
    
    logger.info(f"✅ Credenciais encontradas: {username[:5]}...@{username.split('@')[1] if '@' in username else 'N/A'}")
    
    # Criar callback de teste
    test_callback = TestCallback()
    
    try:
        # Inicializar analisador
        logger.info("🔧 Inicializando PragmaticAnalyzer...")
        analyzer = await initialize_pragmatic_analyzer(
            username=username,
            password=password,
            callback=test_callback
        )
        
        if not analyzer:
            logger.error("❌ Falha ao inicializar PragmaticAnalyzer")
            return False
        
        logger.info("✅ PragmaticAnalyzer inicializado com sucesso!")
        
        # Iniciar monitoramento
        logger.info("🔄 Iniciando monitoramento...")
        if analyzer.start_monitoring():
            logger.info("✅ Monitoramento iniciado!")
            
            # Manter rodando por 2 minutos para teste
            logger.info("⏱️ Monitorando por 2 minutos...")
            await asyncio.sleep(120)
            
            # Parar monitoramento
            logger.info("🛑 Parando monitoramento...")
            analyzer.stop_monitoring()
            
            # Mostrar estatísticas finais
            logger.info("📊 Estatísticas finais:")
            test_callback.show_stats()
            
        else:
            logger.error("❌ Falha ao iniciar monitoramento")
            return False
        
        # Limpar recursos
        await analyzer.cleanup()
        logger.info("✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_websocket_app():
    """Testa a aplicação WebSocket."""
    logger.info("🧪 Testando aplicação WebSocket...")
    
    try:
        # Importar aplicação
        from backend.websocket_app import ws_app
        
        # Verificar status inicial
        status = ws_app.get_status()
        logger.info(f"📊 Status inicial: {status}")
        
        # Verificar se PragmaticAnalyzer está disponível
        if not status.get('pragmatic_available', False):
            logger.warning("⚠️ PragmaticAnalyzer não está disponível")
            return False
        
        logger.info("✅ Aplicação WebSocket OK!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar aplicação WebSocket: {e}")
        return False


def test_environment():
    """Testa o ambiente de execução."""
    logger.info("🧪 Testando ambiente...")
    
    # Verificar Python
    logger.info(f"🐍 Python: {sys.version}")
    
    # Verificar variáveis de ambiente
    env_vars = [
        'PLAYNABETS_USER',
        'PLAYNABETS_PASS',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASS' in var:
                logger.info(f"✅ {var}: {'*' * len(value)}")
            else:
                logger.info(f"✅ {var}: {value}")
        else:
            logger.warning(f"⚠️ {var}: Não configurado")
    
    # Verificar dependências
    try:
        import playwright
        logger.info("✅ Playwright: Disponível")
    except ImportError:
        logger.error("❌ Playwright não instalado")
        return False
    
    try:
        import websocket
        logger.info("✅ websocket-client: Disponível")
    except ImportError:
        logger.error("❌ websocket-client não instalado")
        return False
    
    try:
        import flask_socketio
        logger.info("✅ Flask-SocketIO: Disponível")
    except ImportError:
        logger.error("❌ Flask-SocketIO não instalado")
        return False
    
    logger.info("✅ Ambiente OK!")
    return True


async def main():
    """Função principal de teste."""
    logger.info("🚀 Iniciando testes de integração Pragmatic Play...")
    logger.info("=" * 60)
    
    # Teste 1: Ambiente
    logger.info("\n1️⃣ Testando ambiente...")
    if not test_environment():
        logger.error("❌ Teste de ambiente falhou!")
        return
    
    # Teste 2: Aplicação WebSocket
    logger.info("\n2️⃣ Testando aplicação WebSocket...")
    if not test_websocket_app():
        logger.error("❌ Teste de aplicação WebSocket falhou!")
        return
    
    # Teste 3: PragmaticAnalyzer (opcional - requer credenciais)
    logger.info("\n3️⃣ Testando PragmaticAnalyzer...")
    logger.info("   ⚠️ Este teste requer credenciais válidas!")
    
    username = os.getenv('PLAYNABETS_USER')
    password = os.getenv('PLAYNABETS_PASS')
    
    if username and password:
        logger.info("   ✅ Credenciais encontradas, executando teste...")
        if await test_pragmatic_analyzer():
            logger.info("✅ Teste do PragmaticAnalyzer bem-sucedido!")
        else:
            logger.error("❌ Teste do PragmaticAnalyzer falhou!")
    else:
        logger.warning("   ⚠️ Credenciais não configuradas, pulando teste")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Testes concluídos!")
    logger.info("\n📋 Próximos passos:")
    logger.info("   1. Configure suas credenciais no .env")
    logger.info("   2. Execute: python backend/websocket_app.py")
    logger.info("   3. Acesse: http://localhost:5000")
    logger.info("   4. Para deploy no Railway: railway up")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
