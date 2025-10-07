#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplicação WebSocket para Pragmatic Play
Integração com Flask-SocketIO para emitir resultados em tempo real
"""

import asyncio
import os
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import eventlet

# Importar o analisador Pragmatic Play
try:
    from shared.pragmatic_analyzer import PragmaticAnalyzer, initialize_pragmatic_analyzer
    PRAGMATIC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PragmaticAnalyzer não disponível: {e}")
    PRAGMATIC_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar eventlet com configurações específicas para Windows
eventlet.monkey_patch(
    socket=True,
    select=True,
    thread=True,
    time=True,
    os=True
)

# Criar aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pragmatic_play_secret_key')

# Configurar CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_interval=30,
    ping_timeout=10,
    logger=True,
    engineio_logger=True
)

# Estado global
pragmatic_analyzer = None
is_running = False
results_history = []
last_status_check = 0


class PragmaticWebSocketApp:
    """Aplicação WebSocket para Pragmatic Play."""
    
    def __init__(self):
        self.analyzer = None
        self.is_monitoring = False
        self.results_count = 0
        self.start_time = None
    
    async def initialize_analyzer(self, username: str, password: str) -> bool:
        """Inicializa o analisador Pragmatic Play."""
        global pragmatic_analyzer
        
        try:
            logger.info("🔧 Inicializando PragmaticAnalyzer...")
            
            self.analyzer = await initialize_pragmatic_analyzer(
                username=username,
                password=password,
                callback=self._on_result_received
            )
            
            if self.analyzer:
                pragmatic_analyzer = self.analyzer
                logger.info("✅ PragmaticAnalyzer inicializado com sucesso!")
                return True
            else:
                logger.error("❌ Falha ao inicializar PragmaticAnalyzer")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar analisador: {e}")
            return False
    
    def _on_result_received(self, result: Dict):
        """Callback chamado quando um resultado é recebido."""
        try:
            # Adicionar timestamp
            result['received_at'] = datetime.now().isoformat()
            result['id'] = f"pragmatic_{int(time.time() * 1000)}"
            
            # Adicionar ao histórico
            global results_history
            results_history.append(result)
            
            # Manter apenas últimos 100 resultados
            if len(results_history) > 100:
                results_history = results_history[-100:]
            
            # Emitir para todos os clientes conectados
            socketio.emit('new_result', result, namespace='/')
            
            # Emitir para sala específica se necessário
            socketio.emit('roulette_result', result, namespace='/', room='roulette_room')
            
            self.results_count += 1
            logger.info(f"📡 Resultado emitido: {result['number']} ({result['color']}) - Total: {self.results_count}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado: {e}")
    
    def start_monitoring(self) -> bool:
        """Inicia monitoramento."""
        if not self.analyzer:
            logger.error("❌ Analisador não inicializado")
            return False
        
        try:
            if self.analyzer.start_monitoring():
                self.is_monitoring = True
                self.start_time = time.time()
                logger.info("✅ Monitoramento iniciado")
                return True
            else:
                logger.error("❌ Falha ao iniciar monitoramento")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar monitoramento: {e}")
            return False
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        if self.analyzer:
            self.analyzer.stop_monitoring()
            self.is_monitoring = False
            logger.info("🛑 Monitoramento parado")
    
    async def cleanup(self):
        """Limpa recursos."""
        if self.analyzer:
            await self.analyzer.cleanup()
            self.analyzer = None
        logger.info("🧹 Recursos limpos")
    
    def get_status(self) -> Dict:
        """Retorna status da aplicação."""
        analyzer_status = {}
        if self.analyzer:
            analyzer_status = self.analyzer.get_status()
        
        return {
            'app_running': is_running,
            'monitoring': self.is_monitoring,
            'results_count': self.results_count,
            'start_time': self.start_time,
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'analyzer': analyzer_status,
            'pragmatic_available': PRAGMATIC_AVAILABLE
        }


# Instância global da aplicação
ws_app = PragmaticWebSocketApp()


# ===== ROTAS FLASK =====

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """API de status."""
    try:
        status = ws_app.get_status()
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/results')
def api_results():
    """API de resultados."""
    try:
        from flask import request
        limit = int(request.args.get('limit', 20))
        recent_results = results_history[-limit:] if results_history else []
        
        return jsonify({
            'success': True,
            'results': recent_results,
            'count': len(recent_results),
            'total': len(results_history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/start', methods=['POST'])
def api_start():
    """API para iniciar monitoramento."""
    try:
        from flask import request
        data = request.get_json() or {}
        
        username = data.get('username') or os.getenv('PLAYNABETS_USER')
        password = data.get('password') or os.getenv('PLAYNABETS_PASS')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Credenciais não fornecidas'
            }), 400
        
        # Inicializar em thread separada para não bloquear
        def start_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Inicializar analisador
                success = loop.run_until_complete(ws_app.initialize_analyzer(username, password))
                if success:
                    # Iniciar monitoramento
                    ws_app.start_monitoring()
                    logger.info("✅ Monitoramento iniciado via API")
                else:
                    logger.error("❌ Falha ao inicializar via API")
            except Exception as e:
                logger.error(f"❌ Erro na inicialização assíncrona: {e}")
            finally:
                loop.close()
        
        # Executar em thread separada
        thread = threading.Thread(target=start_async, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Inicialização iniciada'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stop', methods=['POST'])
def api_stop():
    """API para parar monitoramento."""
    try:
        ws_app.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento parado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== EVENTOS SOCKETIO =====

@socketio.on('connect')
def handle_connect():
    """Cliente conectado."""
    from flask import request
    logger.info(f"🔌 Cliente conectado: {request.sid}")
    emit('status', {'message': 'Conectado ao servidor Pragmatic Play'})


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado."""
    from flask import request
    logger.info(f"🔌 Cliente desconectado: {request.sid}")


@socketio.on('join_roulette')
def handle_join_roulette():
    """Cliente entrou na sala da roleta."""
    join_room('roulette_room')
    emit('status', {'message': 'Entrou na sala da roleta'})
    
    # Enviar últimos resultados
    if results_history:
        recent_results = results_history[-10:]
        emit('recent_results', {'results': recent_results})


@socketio.on('leave_roulette')
def handle_leave_roulette():
    """Cliente saiu da sala da roleta."""
    leave_room('roulette_room')
    emit('status', {'message': 'Saiu da sala da roleta'})


@socketio.on('get_status')
def handle_get_status():
    """Cliente solicitou status."""
    status = ws_app.get_status()
    emit('status_update', status)


@socketio.on('get_results')
def handle_get_results(data=None):
    """Cliente solicitou resultados."""
    limit = 20
    if data and 'limit' in data:
        limit = int(data['limit'])
    
    recent_results = results_history[-limit:] if results_history else []
    emit('results_data', {
        'results': recent_results,
        'count': len(recent_results),
        'total': len(results_history)
    })


# ===== FUNÇÕES DE INICIALIZAÇÃO =====

def initialize_app():
    """Inicializa a aplicação."""
    global is_running
    
    try:
        logger.info("🚀 Inicializando aplicação WebSocket...")
        
        # Verificar se Playwright está disponível
        if not PRAGMATIC_AVAILABLE:
            logger.warning("⚠️ PragmaticAnalyzer não está disponível")
            logger.warning("⚠️ Instale com: pip install playwright && playwright install chromium")
        
        # Verificar credenciais
        username = os.getenv('PLAYNABETS_USER')
        password = os.getenv('PLAYNABETS_PASS')
        
        if username and password:
            logger.info("✅ Credenciais encontradas no .env")
            
            # Auto-inicializar se configurado
            auto_start = os.getenv('PRAGMATIC_AUTO_START', 'false').lower() == 'true'
            if auto_start:
                logger.info("🔄 Auto-inicialização ativada")
                
                def auto_init():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        success = loop.run_until_complete(ws_app.initialize_analyzer(username, password))
                        if success:
                            ws_app.start_monitoring()
                            logger.info("✅ Auto-inicialização bem-sucedida")
                        else:
                            logger.error("❌ Falha na auto-inicialização")
                    except Exception as e:
                        logger.error(f"❌ Erro na auto-inicialização: {e}")
                    finally:
                        loop.close()
                
                # Executar em thread separada
                thread = threading.Thread(target=auto_init, daemon=True)
                thread.start()
        else:
            logger.warning("⚠️ Credenciais não configuradas (PLAYNABETS_USER, PLAYNABETS_PASS)")
        
        is_running = True
        logger.info("✅ Aplicação inicializada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        is_running = False


def cleanup_app():
    """Limpa recursos da aplicação."""
    global is_running
    
    try:
        logger.info("🧹 Limpando recursos da aplicação...")
        
        ws_app.stop_monitoring()
        
        # Limpar recursos assincronamente
        def cleanup_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(ws_app.cleanup())
            except Exception as e:
                logger.error(f"❌ Erro na limpeza: {e}")
            finally:
                loop.close()
        
        # Executar limpeza em thread separada
        thread = threading.Thread(target=cleanup_async, daemon=True)
        thread.start()
        thread.join(timeout=5)
        
        is_running = False
        logger.info("✅ Recursos limpos")
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {e}")


# ===== HANDLERS DE SINAL =====

import signal
import sys

def signal_handler(signum, frame):
    """Handler para sinais do sistema."""
    logger.info(f"🛑 Recebido sinal {signum}, finalizando...")
    cleanup_app()
    sys.exit(0)

# Registrar handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ===== MAIN =====

if __name__ == '__main__':
    try:
        # Inicializar aplicação
        initialize_app()
        
        # Obter configurações
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV', 'production') == 'development'
        
        logger.info(f"🌐 Iniciando servidor em {host}:{port}")
        logger.info(f"🔧 Modo debug: {debug}")
        
        # Executar servidor
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,  # Sempre desabilitar debug em produção
            use_reloader=False,  # Desabilitar reloader para evitar problemas com threads
            log_output=True,
            allow_unsafe_werkzeug=True  # Permitir execução em produção
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        logger.error(f"❌ Tipo do erro: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
    finally:
        cleanup_app()
