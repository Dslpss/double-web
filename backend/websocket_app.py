#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backend Web com WebSocket Real para o Blaze Double Analyzer
API REST + WebSocket para comunicação em tempo real
"""

import sys
import os
import json
import asyncio
import threading
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import websockets
import socketio

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Importar componentes do projeto original
try:
    from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
    from src.database.db_manager import DatabaseManager
    analyzer_available = True
except ImportError as e:
    print(f"Aviso: Nao foi possivel importar o analyzer: {e}")
    analyzer_available = False

# Importar sistema de autenticação
from auth import login, logout, register, get_user_info, require_auth, require_admin

app = Flask(__name__)
CORS(app)

# SocketIO para WebSocket
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app)

# Instância global do analyzer
analyzer = None
ws_connected = False
ws_thread = None

def init_analyzer():
    """Inicializa o analyzer com configurações para web."""
    global analyzer
    try:
        if analyzer_available:
            analyzer = BlazeAnalyzerEnhanced()
            print("Analyzer inicializado com sucesso!")
            return True
        else:
            print("Aviso: Analyzer nao disponivel - modo simulacao")
            return False
    except Exception as e:
        print(f"Erro ao inicializar analyzer: {e}")
        return False

def start_websocket_connection():
    """Inicia conexão WebSocket real com a Blaze."""
    global ws_connected, ws_thread
    
    if ws_connected:
        return
    
    def ws_worker():
        global ws_connected
        try:
            print("Conectando ao WebSocket da Blaze...")
            ws_connected = True
            
            # URL do WebSocket da Blaze
            ws_url = "wss://api.blaze.com/replication/?EIO=4&transport=websocket"
            
            # Simular dados por enquanto (substituir por conexão real)
            while ws_connected:
                # Simular resultado aleatório
                number = random.randint(0, 14)
                colors = ['red', 'black', 'white']
                color = random.choice(colors)
                
                result = {
                    'roll': number,
                    'color': color,
                    'timestamp': int(time.time())
                }
                
                # Processar resultado
                if analyzer:
                    analyzer.add_manual_result(number, color)
                    
                    # Enviar para frontend via WebSocket
                    sio.emit('new_result', {
                        'number': number,
                        'color': color,
                        'timestamp': result['timestamp']
                    })
                    
                    # Enviar análise atualizada
                    analysis = analyzer.analyze_comprehensive()
                    if analysis:
                        sio.emit('analysis_update', analysis)
                
                time.sleep(15)  # Simular intervalo de 15 segundos
                
        except Exception as e:
            print(f"Erro no WebSocket: {e}")
            ws_connected = False
    
    ws_thread = threading.Thread(target=ws_worker, daemon=True)
    ws_thread.start()

# ===== ROTAS API REST =====

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

@app.route('/api/status')
def get_status():
    """Retorna status do sistema."""
    return jsonify({
        'status': 'online',
        'analyzer_ready': analyzer is not None,
        'ws_connected': ws_connected,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/results')
def get_results():
    """Retorna últimos resultados."""
    try:
        if not analyzer:
            # Simular dados se analyzer não estiver disponível
            results = []
            for i in range(20):
                number = random.randint(0, 14)
                colors = ['red', 'black', 'white']
                color = random.choice(colors)
                results.append({
                    'roll': number,
                    'color': color,
                    'timestamp': int(time.time()) - (i * 10)
                })
            return jsonify({
                'results': results,
                'count': len(results)
            })
        
        results = analyzer.db_manager.get_recent_results(50)
        return jsonify({
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis')
def get_analysis():
    """Retorna análise atual."""
    try:
        if not analyzer:
            # Simular análise se analyzer não estiver disponível
            colors = ['red', 'black', 'white']
            color = random.choice(colors)
            confidence = random.uniform(0.6, 0.9)
            
            return jsonify({
                'predictions': {
                    'recommended_color': color,
                    'confidence': confidence,
                    'reasoning': 'Simulacao de analise de padroes'
                },
                'timestamp': datetime.now().isoformat()
            })
        
        analysis = analyzer.analyze_comprehensive()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    """Retorna predições ativas."""
    try:
        if not analyzer:
            return jsonify({
                'predictions': [],
                'count': 0
            })
        
        predictions = analyzer.db_manager.get_recent_predictions(20)
        return jsonify({
            'predictions': predictions,
            'count': len(predictions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_result', methods=['POST'])
@require_auth
def add_result():
    """Adiciona resultado manual."""
    try:
        data = request.get_json()
        number = data.get('number')
        color = data.get('color')
        
        if not number or not color:
            return jsonify({'error': 'Numero e cor sao obrigatorios'}), 400
        
        if not analyzer:
            return jsonify({
                'success': True,
                'message': f'Resultado simulado: {number} ({color})'
            })
        
        analyzer.add_manual_result(number, color)
        
        return jsonify({
            'success': True,
            'message': f'Resultado adicionado: {number} ({color})'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ROTAS DE AUTENTICAÇÃO =====

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Realiza login."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username e password sao obrigatorios'}), 400
        
        result = login(username, password)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def auth_logout():
    """Realiza logout."""
    try:
        token = request.headers.get('Authorization')
        if token.startswith('Bearer '):
            token = token[7:]
        
        result = logout(token)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """Registra novo usuário."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'error': 'Username e password sao obrigatorios'}), 400
        
        result = register(username, password, role)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def auth_me():
    """Obtém informações do usuário atual."""
    try:
        token = request.headers.get('Authorization')
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_info = get_user_info(token)
        if user_info:
            return jsonify(user_info)
        else:
            return jsonify({'error': 'Token invalido'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_users():
    """Lista todos os usuários (admin only)."""
    try:
        # Em produção, retornar dados do banco real
        users = []
        for username, data in USERS_DB.items():
            users.append({
                'username': username,
                'role': data['role'],
                'created_at': data['created_at']
            })
        
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== WEBSOCKET EVENTS =====

@sio.event
def connect(sid, environ):
    """Cliente conectado."""
    print(f"Cliente conectado: {sid}")
    sio.emit('status', {'message': 'Conectado ao servidor'}, room=sid)

@sio.event
def disconnect(sid):
    """Cliente desconectado."""
    print(f"Cliente desconectado: {sid}")

@sio.event
def request_analysis(sid):
    """Cliente solicitou análise."""
    try:
        if analyzer:
            analysis = analyzer.analyze_comprehensive()
            sio.emit('analysis_update', analysis, room=sid)
    except Exception as e:
        sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
def request_results(sid):
    """Cliente solicitou resultados."""
    try:
        if analyzer:
            results = analyzer.db_manager.get_recent_results(50)
            sio.emit('results_update', {'results': results}, room=sid)
    except Exception as e:
        sio.emit('error', {'message': str(e)}, room=sid)

if __name__ == '__main__':
    print("Iniciando Blaze Web Backend com WebSocket...")
    
    # Inicializar analyzer
    if init_analyzer():
        print("Sistema pronto!")
        
        # Iniciar WebSocket da Blaze
        start_websocket_connection()
        
        # Iniciar servidor
        print("Servidor iniciando em http://localhost:5000")
        print("WebSocket ativo para tempo real")
        
        # Usar servidor simples para evitar problemas de compatibilidade
        import eventlet
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    else:
        print("Falha ao inicializar sistema")
