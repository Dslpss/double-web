#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backend Web Simples para o Blaze Double Analyzer
API REST sem WebSocket (versão simplificada)
"""

import sys
import os
import json
import time
import random
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Adicionar o diretório shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Importar componentes do projeto original
try:
    from blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
    from src.database.db_manager import DatabaseManager
    analyzer_available = True
except ImportError as e:
    print(f"⚠️  Aviso: Não foi possível importar o analyzer: {e}")
    analyzer_available = False

# Importar sistema de autenticação
from auth import login, logout, register, get_user_info, require_auth, require_admin

# Importar integrador PlayNabets
from playnabets_integrator import init_playnabets_integrator, start_playnabets_connection, stop_playnabets_connection, get_playnabets_status

app = Flask(__name__)
CORS(app)

# Instância global do analyzer
analyzer = None

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

@app.route('/playnabets')
def playnabets():
    """Controle PlayNabets."""
    return render_template('playnabets.html')

@app.route('/api/status')
def get_status():
    """Retorna status do sistema."""
    return jsonify({
        'status': 'online',
        'analyzer_ready': analyzer is not None,
        'ws_connected': False,  # Sem WebSocket nesta versão
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
                    'reasoning': 'Simulação de análise de padrões'
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
def add_result():
    """Adiciona resultado manual."""
    try:
        data = request.get_json()
        number = data.get('number')
        color = data.get('color')
        
        if not number or not color:
            return jsonify({'error': 'Número e cor são obrigatórios'}), 400
        
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

# ===== ROTAS PLAYNABETS =====

@app.route('/api/playnabets/status', methods=['GET'])
def playnabets_status():
    """Retorna status da conexão PlayNabets."""
    try:
        status = get_playnabets_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playnabets/start', methods=['POST'])
@require_auth
def playnabets_start():
    """Inicia conexão com PlayNabets."""
    try:
        start_playnabets_connection()
        return jsonify({
            'success': True,
            'message': 'Conexão PlayNabets iniciada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playnabets/stop', methods=['POST'])
@require_auth
def playnabets_stop():
    """Para conexão com PlayNabets."""
    try:
        stop_playnabets_connection()
        return jsonify({
            'success': True,
            'message': 'Conexão PlayNabets parada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Iniciando Blaze Web Backend (Versao Simples)...")
    
    # Inicializar analyzer
    analyzer_ready = init_analyzer()
    
    # Inicializar integrador PlayNabets
    if analyzer_ready:
        init_playnabets_integrator(analyzer)
        print("Integrador PlayNabets inicializado!")
    else:
        print("Aviso: Integrador PlayNabets nao inicializado - analyzer nao disponivel")
    
    print("Sistema pronto!")
    print("Servidor iniciando em http://localhost:5000")
    print("Nota: Esta versao nao possui WebSocket - use a API REST")
    print("Para conectar com PlayNabets, use: POST /api/playnabets/start")
    
    # Iniciar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
