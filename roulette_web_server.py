#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Servidor Web para Interface da Roleta Brasileira
- Dashboard em tempo real
- API REST para dados
- WebSocket para atualizações em tempo real
- Interface responsiva
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
from roulette_system_complete import PragmaticAPIMonitor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roulette_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Sistema de roleta global
roulette_system = None
web_clients = set()

@app.route('/')
def dashboard():
    """Página principal do dashboard."""
    return render_template('roulette_dashboard.html')

@app.route('/api/status')
def api_status():
    """Status do sistema."""
    if roulette_system:
        return jsonify({
            'status': 'running' if roulette_system.running else 'stopped',
            'total_results': len(roulette_system.results_cache),
            'last_update': datetime.now().isoformat()
        })
    return jsonify({'status': 'not_initialized'})

@app.route('/api/dashboard')
def api_dashboard():
    """Dados completos do dashboard."""
    if roulette_system:
        return jsonify(roulette_system.get_dashboard_data())
    return jsonify({'error': 'Sistema não inicializado'})

@app.route('/api/results')
def api_results():
    """Resultados recentes."""
    limit = request.args.get('limit', 50, type=int)
    if roulette_system:
        results = roulette_system.database.get_recent_results(limit)
        return jsonify([r.to_dict() for r in results])
    return jsonify([])

@app.route('/api/statistics')
def api_statistics():
    """Estatísticas."""
    hours = request.args.get('hours', 24, type=int)
    if roulette_system:
        stats = roulette_system.database.get_statistics(hours)
        return jsonify(stats)
    return jsonify({})

@app.route('/api/notifications')
def api_notifications():
    """Notificações recentes."""
    limit = request.args.get('limit', 20, type=int)
    if roulette_system:
        notifications = roulette_system.notifications.get_recent_notifications(limit)
        return jsonify(notifications)
    return jsonify([])

@socketio.on('connect')
def handle_connect():
    """Cliente conectou ao WebSocket."""
    web_clients.add(request.sid)
    print(f"🌐 Cliente conectado: {request.sid}")
    
    # Enviar dados iniciais
    if roulette_system:
        emit('dashboard_update', roulette_system.get_dashboard_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou do WebSocket."""
    web_clients.discard(request.sid)
    print(f"🌐 Cliente desconectado: {request.sid}")

def broadcast_update(data):
    """Envia atualização para todos os clientes conectados."""
    if web_clients:
        socketio.emit('dashboard_update', data)

def start_roulette_system():
    """Inicia o sistema de roleta em thread separada."""
    global roulette_system
    
    print("🚀 Iniciando sistema de roleta...")
    roulette_system = PragmaticAPIMonitor()
    
    # Modificar o sistema para enviar atualizações via WebSocket
    original_process = roulette_system.process_api_response
    
    def enhanced_process(data):
        """Versão melhorada que envia atualizações via WebSocket."""
        new_results = original_process(data)
        
        if new_results and web_clients:
            # Enviar atualização em tempo real
            dashboard_data = roulette_system.get_dashboard_data()
            broadcast_update(dashboard_data)
        
        return new_results
    
    roulette_system.process_api_response = enhanced_process
    roulette_system.start()
    
    print("✅ Sistema de roleta iniciado!")

if __name__ == '__main__':
    # Iniciar sistema de roleta em thread separada
    roulette_thread = threading.Thread(target=start_roulette_system, daemon=True)
    roulette_thread.start()
    
    # Aguardar um pouco para o sistema inicializar
    time.sleep(2)
    
    print("🌐 Iniciando servidor web...")
    print("📊 Dashboard disponível em: http://localhost:5000")
    print("🔌 WebSocket habilitado para atualizações em tempo real")
    
    # Iniciar servidor web
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
