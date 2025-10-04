#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pragmatic-play-secret-key')
CORS(app)

# Importar o analisador Pragmatic Play
try:
    from shared.pragmatic_analyzer import PragmaticAnalyzer
    PRAGMATIC_AVAILABLE = True
    logger.info("PragmaticAnalyzer importado com sucesso")
except ImportError as e:
    logger.warning(f"PragmaticAnalyzer nao disponivel: {e}")
    PRAGMATIC_AVAILABLE = False

# Variaveis globais
pragmatic_analyzer = None
results_history = []

@app.route('/')
def index():
    """Pagina inicial."""
    return jsonify({
        'message': 'Servidor Pragmatic Play ativo',
        'pragmatic_available': PRAGMATIC_AVAILABLE
    })

@app.route('/api/status')
def api_status():
    """Status da aplicacao."""
    try:
        global pragmatic_analyzer
        
        if not PRAGMATIC_AVAILABLE:
            return jsonify({
                'available': False,
                'connected': False,
                'monitoring': False,
                'error': 'PragmaticAnalyzer nao esta disponivel'
            })
        
        if pragmatic_analyzer is None:
            return jsonify({
                'available': True,
                'connected': False,
                'monitoring': False,
                'error': 'PragmaticAnalyzer nao inicializado'
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
                'error': 'PragmaticAnalyzer nao esta disponivel'
            }), 400
        
        # Inicializar se necessario
        if pragmatic_analyzer is None:
            username = os.getenv('PLAYNABETS_USER')
            password = os.getenv('PLAYNABETS_PASS')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'error': 'Credenciais nao configuradas (PLAYNABETS_USER e PLAYNABETS_PASS)'
                }), 400
            
            def result_callback(result):
                results_history.append(result)
                logger.info(f"Resultado: {result}")
            
            pragmatic_analyzer = PragmaticAnalyzer(
                username=username,
                password=password,
                callback=result_callback
            )
        
        return jsonify({
            'success': True,
            'message': 'PragmaticAnalyzer inicializado'
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
            logger.info("Monitoramento Pragmatic Play parado")
        
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

if __name__ == '__main__':
    logger.info("Iniciando servidor Pragmatic Play...")
    logger.info(f"PragmaticAnalyzer disponivel: {PRAGMATIC_AVAILABLE}")
    
    # Verificar credenciais
    username = os.getenv('PLAYNABETS_USER')
    password = os.getenv('PLAYNABETS_PASS')
    
    if username and password:
        logger.info("Credenciais configuradas")
    else:
        logger.warning("Credenciais nao configuradas (PLAYNABETS_USER e PLAYNABETS_PASS)")
    
    # Executar servidor
    app.run(host='0.0.0.0', port=5000, debug=True)
