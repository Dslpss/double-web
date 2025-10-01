#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backend Web para o Blaze Double Analyzer
API REST + WebSocket para comunicação em tempo real
"""

import sys
import os
import json
import threading
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Importar componentes do projeto original
from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
from src.database.db_manager import DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blaze_web_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Instância global do analyzer
analyzer = None
ws_connected = False
ws_thread = None

def init_analyzer():
    """Inicializa o analyzer com configurações para web."""
    global analyzer
    try:
        analyzer = BlazeAnalyzerEnhanced()
        print("✅ Analyzer inicializado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar analyzer: {e}")
        return False

def start_websocket_connection():
    """Inicia simulação de dados (substituir por conexão real da Blaze)."""
    global ws_connected, ws_thread
    
    if ws_connected:
        return
    
    def ws_worker():
        global ws_connected
        try:
            print("🔌 Iniciando simulação de dados...")
            ws_connected = True
            
            # Simular dados por enquanto (substituir por conexão real da Blaze)
            while ws_connected:
                # Simular resultado aleatório
                number = random.randint(0, 14)
                
                # Determinar cor baseada no número (mapeamento correto)
                if number == 0:
                    color = 'white'
                elif 1 <= number <= 7:
                    color = 'red'
                elif 8 <= number <= 14:
                    color = 'black'
                
                result = {
                    'roll': number,
                    'color': color,
                    'timestamp': int(time.time())
                }
                
                # Processar resultado
                if analyzer:
                    analyzer.add_manual_result(number, color)
                    
                    # Enviar para frontend via WebSocket
                    socketio.emit('new_result', {
                        'number': number,
                        'color': color,
                        'timestamp': result['timestamp']
                    })
                    
                    # Enviar análise atualizada
                    analysis = analyzer.analyze_comprehensive()
                    if analysis:
                        socketio.emit('analysis_update', analysis)
                
                time.sleep(10)  # Simular intervalo de 10 segundos
                
        except Exception as e:
            print(f"❌ Erro na simulação: {e}")
            ws_connected = False
    
    ws_thread = threading.Thread(target=ws_worker, daemon=True)
    ws_thread.start()

# ===== ROTAS API REST =====

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

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
            return jsonify({'error': 'Analyzer não inicializado'}), 500
        
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
            return jsonify({'error': 'Analyzer não inicializado'}), 500
        
        analysis = analyzer.analyze_comprehensive()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    """Retorna predições ativas."""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 500
        
        predictions = analyzer.db_manager.get_recent_predictions(20)
        return jsonify({
            'predictions': predictions,
            'count': len(predictions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_result', methods=['POST'])
def add_result():
    """Adiciona resultado manual."""
    try:
        data = request.get_json()
        number = data.get('number')
        color = data.get('color')
        
        if not number or not color:
            return jsonify({'error': 'Número e cor são obrigatórios'}), 400
        
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 500
        
        analyzer.add_manual_result(number, color)
        
        return jsonify({
            'success': True,
            'message': f'Resultado adicionado: {number} ({color})'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== WEBSOCKET EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Cliente conectado."""
    print(f"🔌 Cliente conectado: {request.sid}")
    emit('status', {'message': 'Conectado ao servidor'})

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
            emit('analysis_update', analysis)
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('request_results')
def handle_request_results():
    """Cliente solicitou resultados."""
    try:
        if analyzer:
            results = analyzer.db_manager.get_recent_results(50)
            emit('results_update', {'results': results})
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🚀 Iniciando Blaze Web Backend...")
    
    # Inicializar analyzer
    if init_analyzer():
        print("✅ Sistema pronto!")
        
        # Iniciar simulação de dados
        start_websocket_connection()
        
        # Iniciar servidor
        print("🌐 Servidor iniciando em http://localhost:5000")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Falha ao inicializar sistema")
