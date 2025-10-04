#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplica√ß√£o WebSocket simplificada para Pragmatic Play
Sem eventlet para evitar problemas de SSL
"""

import asyncio
import os
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# Importar o analisador Pragmatic Play
try:
    from shared.pragmatic_analyzer import PragmaticAnalyzer, initialize_pragmatic_analyzer
    PRAGMATIC_AVAILABLE = True
except ImportError as e:
    print(f"‚ö†Ô∏è PragmaticAnalyzer n√£o dispon√≠vel: {e}")
    PRAGMATIC_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pragmatic-play-secret-key')
CORS(app)

# Inicializar SocketIO sem eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Vari√°veis globais
pragmatic_analyzer = None
results_history = []
clients_connected = 0

def pragmatic_result_callback(result):
    """Callback para receber resultados do PragmaticAnalyzer."""
    global results_history
    
    # Adicionar timestamp
    result['received_at'] = datetime.now().isoformat()
    result['id'] = f"pragmatic_{int(time.time() * 1000)}"
    
    # Adicionar ao hist√≥rico
    results_history.append(result)
    
    # Manter apenas √∫ltimos 100 resultados
    if len(results_history) > 100:
        results_history = results_history[-100:]
    
    # Emitir para clientes conectados via SocketIO
    socketio.emit('pragmatic_result', {
        'result': result,
        'timestamp': datetime.now().isoformat()
    }, room='pragmatic_room')
    
    logger.info(f"Ìæ≤ Resultado Pragmatic Play: {result['number']} ({result['color']}) - Multiplicador: {result['multiplier']}")

# ===== ROTAS FLASK =====

@app.route('/')
def index():
    """P√°gina inicial."""
    return render_template('pragmatic_websocket.html')

@app.route('/api/status')
def api_status():
    """Status da aplica√ß√£o."""
    try:
        global pragmatic_analyzer
        
        if not PRAGMATIC_AVAILABLE:
            return jsonify({
                'available': False,
                'connected': False,
                'monitoring': False,
                'error': 'PragmaticAnalyzer n√£o est√° dispon√≠vel'
            })
        
        if pragmatic_analyzer is None:
            return jsonify({
                'available': True,
                'connected': False,
                'monitoring': False,
                'error': 'PragmaticAnalyzer n√£o inicializado'
            })
        
        status = pragmatic_analyzer.get_status()
        
        return jsonify({
            'available': True,
            'connected': status.get('connected', False),
            'monitoring': status.get('monitoring', False),
            'has_session': status.get('has_session', False),
            'playwright_available': status.get('playwright_available', False),
            'last_result_time': status.get('last_result_time', 0),
            'reconnect_attempts': status.get('reconnect_attempts', 0),
            'clients_connected': clients_connected,
            'total_results': len(results_history)
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'connected': False,
            'monitoring': False,
            'error': str(e)
        }), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    """Inicia monitoramento Pragmatic Play."""
    try:
        global pragmatic_analyzer
        
        if not PRAGMATIC_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'PragmaticAnalyzer n√£o est√° dispon√≠vel'
            }), 400
        
        # Inicializar se necess√°rio
        if pragmatic_analyzer is None:
            username = os.getenv('PLAYNABETS_USER')
            password = os.getenv('PLAYNABETS_PASS')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'error': 'Credenciais n√£o configuradas (PLAYNABETS_USER e PLAYNABETS_PASS)'
                }), 400
            
            pragmatic_analyzer = PragmaticAnalyzer(
                username=username,
                password=password,
                callback=pragmatic_result_callback
            )
        
        # Iniciar monitoramento em thread separada
        def start_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Fazer login e conectar
                success = loop.run_until_complete(pragmatic_analyzer.login_and_get_session())
                if success:
                    pragmatic_analyzer.connect_websocket()
                    pragmatic_analyzer.start_monitoring()
                    logger.info("‚úÖ Monitoramento Pragmatic Play iniciado!")
                else:
                    logger.error("‚ùå Falha ao iniciar monitoramento Pragmatic Play")
            except Exception as e:
                logger.error(f"‚ùå Erro na inicializa√ß√£o ass√≠ncrona: {e}")
            finally:
                loop.close()
        
        # Executar em thread separada
        thread = threading.Thread(target=start_async, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Inicializa√ß√£o Pragmatic Play iniciada'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Para monitoramento Pragmatic Play."""
    try:
        global pragmatic_analyzer
        
        if pragmatic_analyzer:
            pragmatic_analyzer.stop_monitoring()
            logger.info("Ìªë Monitoramento Pragmatic Play parado")
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento Pragmatic Play parado'
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

# ===== EVENTOS SOCKETIO =====

@socketio.on('connect')
def handle_connect():
    """Cliente conectado."""
    global clients_connected
    clients_connected += 1
    logger.info(f"Ì¥å Cliente conectado: {request.sid} (Total: {clients_connected})")
    emit('status', {'message': 'Conectado ao servidor Pragmatic Play'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado."""
    global clients_connected
    clients_connected = max(0, clients_connected - 1)
    logger.info(f"Ì¥å Cliente desconectado: {request.sid} (Total: {clients_connected})")

@socketio.on('join_room')
def handle_join_room(data):
    """Cliente entrou na sala."""
    room = data.get('room', 'pragmatic_room')
    join_room(room)
    emit('status', {'message': f'Entrou na sala: {room}'})
    logger.info(f"Ìø† Cliente {request.sid} entrou na sala: {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
    """Cliente saiu da sala."""
    room = data.get('room', 'pragmatic_room')
    leave_room(room)
    emit('status', {'message': f'Saiu da sala: {room}'})
    logger.info(f"Ìø† Cliente {request.sid} saiu da sala: {room}")

@socketio.on('get_status')
def handle_get_status():
    """Cliente solicitou status."""
    try:
        global pragmatic_analyzer
        
        if not PRAGMATIC_AVAILABLE:
            emit('status_response', {
                'available': False,
                'error': 'PragmaticAnalyzer n√£o est√° dispon√≠vel'
            })
            return
        
        if pragmatic_analyzer is None:
            emit('status_response', {
                'available': True,
                'connected': False,
                'monitoring': False,
                'error': 'PragmaticAnalyzer n√£o inicializado'
            })
            return
        
        status = pragmatic_analyzer.get_status()
        
        emit('status_response', {
            'available': True,
            'connected': status.get('connected', False),
            'monitoring': status.get('monitoring', False),
            'has_session': status.get('has_session', False),
            'playwright_available': status.get('playwright_available', False),
            'last_result_time': status.get('last_result_time', 0),
            'reconnect_attempts': status.get('reconnect_attempts', 0),
            'clients_connected': clients_connected,
            'total_results': len(results_history)
        })
        
    except Exception as e:
        emit('status_response', {
            'available': False,
            'error': str(e)
        })

if __name__ == '__main__':
    logger.info("Ì∫Ä Iniciando servidor Pragmatic Play WebSocket...")
    logger.info(f"Ì≥ã PragmaticAnalyzer dispon√≠vel: {PRAGMATIC_AVAILABLE}")
    
    # Verificar credenciais
    username = os.getenv('PLAYNABETS_USER')
    password = os.getenv('PLAYNABETS_PASS')
    
    if username and password:
        logger.info("‚úÖ Credenciais configuradas")
    else:
        logger.warning("‚ö†Ô∏è Credenciais n√£o configuradas (PLAYNABETS_USER e PLAYNABETS_PASS)")
    
    # Executar servidor
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
