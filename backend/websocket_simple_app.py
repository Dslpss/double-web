#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backend Web com WebSocket para o Blaze Double Analyzer
Versão com Socket.IO para atualizações em tempo real
"""

import sys
import os
import json
import time
import random
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
    analyzer_available = True
except ImportError as e:
    print(f"⚠️  Aviso: Não foi possível importar o analyzer: {e}")
    analyzer_available = False

# Importar módulos de autenticação e PlayNabets
try:
    from auth import require_auth, login, logout, register, get_user_info
    auth_available = True
except ImportError as e:
    print(f"⚠️  Aviso: Módulo de autenticação não disponível: {e}")
    auth_available = False

try:
    from playnabets_integrator import PlayNabetsIntegrator
    playnabets_available = True
except ImportError as e:
    print(f"⚠️  Aviso: Módulo PlayNabets não disponível: {e}")
    playnabets_available = False

# Inicializar Flask e SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'blaze_analyzer_secret_key_2024'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variáveis globais
analyzer = None
playnabets_integrator = None
ws_connected = False
ws_thread = None

def init_analyzer():
    """Inicializa o analyzer."""
    global analyzer
    try:
        if analyzer_available:
            analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
            print("✅ Analyzer inicializado com sucesso!")
            return True
        else:
            print("❌ Analyzer não disponível")
            return False
    except Exception as e:
        print(f"❌ Erro ao inicializar analyzer: {e}")
        return False

def init_playnabets_integrator(analyzer_instance):
    """Inicializa o integrador PlayNabets."""
    global playnabets_integrator
    try:
        if playnabets_available and analyzer_instance:
            playnabets_integrator = PlayNabetsIntegrator(analyzer_instance)
            print("✅ Integrador PlayNabets inicializado!")
            return True
        else:
            print("❌ Integrador PlayNabets não disponível")
            return False
    except Exception as e:
        print(f"❌ Erro ao inicializar integrador PlayNabets: {e}")
        return False

def start_websocket_connection():
    """Inicia conexão WebSocket com PlayNabets."""
    global ws_connected, ws_thread
    
    if ws_connected:
        return
    
    def ws_worker():
        global ws_connected
        try:
            print("🔌 Iniciando conexão PlayNabets...")
            ws_connected = True
            
            if playnabets_integrator:
                playnabets_integrator.start()
                
                # Loop para enviar dados para o frontend
                while ws_connected and playnabets_integrator.running:
                    try:
                        # Obter último resultado
                        if hasattr(playnabets_integrator, 'last_result') and playnabets_integrator.last_result:
                            result = playnabets_integrator.last_result
                            
                            # Enviar para frontend via SocketIO
                            socketio.emit('new_result', {
                                'number': result.get('number'),
                                'color': result.get('color'),
                                'timestamp': result.get('timestamp', int(time.time()))
                            })
                            
                            # Enviar análise atualizada
                            if analyzer:
                                analysis = analyzer.analyze_comprehensive()
                                if analysis:
                                    socketio.emit('analysis_update', analysis)
                        
                        time.sleep(2)  # Atualizar a cada 2 segundos
                        
                    except Exception as e:
                        print(f"❌ Erro no loop WebSocket: {e}")
                        time.sleep(5)
                        
            else:
                print("❌ Integrador PlayNabets não disponível")
                
        except Exception as e:
            print(f"❌ Erro na conexão WebSocket: {e}")
        finally:
            ws_connected = False
    
    ws_thread = threading.Thread(target=ws_worker, daemon=True)
    ws_thread.start()

def stop_websocket_connection():
    """Para a conexão WebSocket."""
    global ws_connected
    ws_connected = False
    
    if playnabets_integrator:
        playnabets_integrator.stop()

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login."""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard avançado."""
    return render_template('dashboard.html')

@app.route('/playnabets')
def playnabets():
    """Controle PlayNabets."""
    return render_template('playnabets.html')

# ===== API ENDPOINTS =====

@app.route('/api/status')
def get_status():
    """Status do sistema."""
    return jsonify({
        'analyzer_ready': analyzer is not None,
        'playnabets_connected': ws_connected,
        'timestamp': int(time.time())
    })

@app.route('/api/results')
def get_results():
    """Obtém resultados recentes."""
    try:
        if analyzer:
            # Combinar dados manuais e da API
            all_data = analyzer.manual_data + analyzer.data
            
            # Converter para formato JSON serializável
            results = []
            for item in all_data[-50:]:  # Últimos 50 resultados
                if isinstance(item, dict):
                    results.append({
                        'id': item.get('id', 'unknown'),
                        'number': item.get('roll', item.get('number', 0)),
                        'color': item.get('color', 'unknown'),
                        'timestamp': item.get('timestamp', int(time.time()))
                    })
            
            return jsonify({
                'results': results,
                'total': len(results),
                'timestamp': int(time.time())
            })
        else:
            return jsonify({'results': [], 'total': 0, 'error': 'Analyzer não disponível'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis')
def get_analysis():
    """Obtém análise atual."""
    try:
        if analyzer:
            analysis = analyzer.analyze_comprehensive()
            return jsonify(analysis or {})
        else:
            return jsonify({'error': 'Analyzer não disponível'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    """Obtém predições recentes."""
    try:
        if analyzer and hasattr(analyzer, 'db_manager'):
            predictions = analyzer.db_manager.get_recent_predictions(20)
            return jsonify({'predictions': predictions})
        else:
            return jsonify({'predictions': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_result', methods=['POST'])
def add_result():
    """Adiciona resultado manual."""
    try:
        data = request.get_json()
        number = data.get('number')
        color = data.get('color')
        
        if number is None:
            return jsonify({'error': 'Número é obrigatório'}), 400
        
        if analyzer:
            analyzer.add_manual_result(number, color)
            
            # Enviar atualização via WebSocket
            result = {
                'number': number,
                'color': color or ('white' if number == 0 else 'red' if 1 <= number <= 7 else 'black'),
                'timestamp': int(time.time())
            }
            socketio.emit('new_result', result)
            
            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'error': 'Analyzer não disponível'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== AUTENTICAÇÃO =====

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Login de usuário."""
    try:
        if not auth_available:
            return jsonify({'error': 'Sistema de autenticação não disponível'}), 500
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        token = login(username, password)
        if token:
            return jsonify({'success': True, 'token': token})
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout de usuário."""
    try:
        if not auth_available:
            return jsonify({'error': 'Sistema de autenticação não disponível'}), 500
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if logout(token):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Token inválido'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """Registro de usuário."""
    try:
        if not auth_available:
            return jsonify({'error': 'Sistema de autenticação não disponível'}), 500
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        if register(username, password, role):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Usuário já existe'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    """Informações do usuário atual."""
    try:
        if not auth_available:
            return jsonify({'error': 'Sistema de autenticação não disponível'}), 500
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_info = get_user_info(token)
        
        if user_info:
            return jsonify({'success': True, 'user': user_info})
        else:
            return jsonify({'error': 'Token inválido'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== PLAYNABETS CONTROL =====

@app.route('/api/playnabets/status', methods=['GET'])
def playnabets_status():
    """Status da conexão PlayNabets."""
    try:
        if playnabets_integrator:
            status = playnabets_integrator.get_status()
            return jsonify(status)
        else:
            return jsonify({
                'connected': False,
                'running': False,
                'last_result': None,
                'ws_url': 'wss://play.soline.bet:5903/Game'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playnabets/start', methods=['POST'])
def playnabets_start():
    """Inicia conexão PlayNabets."""
    try:
        if not playnabets_integrator:
            return jsonify({'error': 'Integrador PlayNabets não disponível'}), 500
        
        if playnabets_integrator.running:
            return jsonify({'error': 'Conexão já está ativa'}), 400
        
        start_websocket_connection()
        return jsonify({
            'success': True,
            'message': 'Conexão PlayNabets iniciada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playnabets/stop', methods=['POST'])
def playnabets_stop():
    """Para conexão PlayNabets."""
    try:
        if not playnabets_integrator:
            return jsonify({'error': 'Integrador PlayNabets não disponível'}), 500
        
        stop_websocket_connection()
        return jsonify({
            'success': True,
            'message': 'Conexão PlayNabets parada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Cliente conectado."""
    print(f"🔌 Cliente conectado: {request.sid}")
    emit('connected', {'message': 'Conectado ao servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado."""
    print(f"🔌 Cliente desconectado: {request.sid}")

@socketio.on('request_analysis')
def handle_request_analysis():
    """Cliente solicitou análise."""
    try:
        if analyzer:
            analysis = analyzer.analyze_comprehensive()
            emit('analysis_update', analysis or {})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('request_results')
def handle_request_results():
    """Cliente solicitou resultados."""
    try:
        if analyzer:
            all_data = analyzer.manual_data + analyzer.data
            results = []
            for item in all_data[-50:]:
                if isinstance(item, dict):
                    results.append({
                        'id': item.get('id', 'unknown'),
                        'number': item.get('roll', item.get('number', 0)),
                        'color': item.get('color', 'unknown'),
                        'timestamp': item.get('timestamp', int(time.time()))
                    })
            emit('results_update', {'results': results})
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🚀 Iniciando Blaze Web Backend (Versão WebSocket)...")
    
    # Inicializar analyzer
    analyzer_ready = init_analyzer()
    
    # Inicializar integrador PlayNabets
    if analyzer_ready:
        init_playnabets_integrator(analyzer)
        print("✅ Integrador PlayNabets inicializado!")
    else:
        print("⚠️  Aviso: Integrador PlayNabets não inicializado - analyzer não disponível")
    
    print("✅ Sistema pronto!")
    print("🌐 Servidor iniciando em http://localhost:5000")
    print("🔌 WebSocket ativo para atualizações em tempo real")
    print("🎯 Para conectar com PlayNabets, use: POST /api/playnabets/start")
    
    # Iniciar servidor com SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
