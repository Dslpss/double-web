#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard Principal - Escolha entre Double e Roleta Brasileira
Sistema integrado com ambas as funcionalidades
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import threading
import time
from datetime import datetime
import os
import sys

# Importar sistemas
try:
    from roulette_system_complete import PragmaticAPIMonitor
except ImportError:
    PragmaticAPIMonitor = None

try:
    from pragmatic_roulette_api_monitor import PragmaticRouletteAPIMonitor
except ImportError:
    PragmaticRouletteAPIMonitor = None

try:
    sys.path.append('shared/src')
    from api.blaze_official_api import BlazeOfficialAPI
except ImportError:
    BlazeOfficialAPI = None

try:
    from jimyobot_game_monitor import JimyoBotGameMonitor
except ImportError:
    JimyoBotGameMonitor = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'main_dashboard_secret_key_2024'

# Sistemas globais
roulette_system = None
pragmatic_roulette_system = None
blaze_system = None
jimyobot_system = None
active_systems = {
    'roulette': False,
    'pragmatic_roulette': False,
    'double': False,
    'jimyobot': False
}

# Inicializar sistemas se disponíveis
if PragmaticAPIMonitor:
    roulette_system = PragmaticAPIMonitor()
if PragmaticRouletteAPIMonitor:
    pragmatic_roulette_system = PragmaticRouletteAPIMonitor()
if BlazeOfficialAPI:
    blaze_system = BlazeOfficialAPI() # Placeholder, assuming BlazeMonitor would be similar
if JimyoBotGameMonitor:
    jimyobot_system = JimyoBotGameMonitor()

@app.route('/')
def main_dashboard():
    """Página principal de escolha."""
    return render_template('main_dashboard.html')

@app.route('/double')
def double_dashboard():
    """Redireciona para dashboard do Double."""
    # Redireciona para o sistema Double que deve estar rodando na porta 5001
    return redirect('http://localhost:5001', code=302)

@app.route('/roulette')
def roulette_dashboard():
    """Dashboard da Roleta Brasileira (Pragmatic Play)."""
    return render_template('pragmatic_roulette_dashboard.html')

@app.route('/jimyobot')
def jimyobot_dashboard():
    """Dashboard do JimyoBot."""
    return render_template('jimyobot_dashboard.html')

@app.route('/api/systems/status')
def systems_status():
    """Status de todos os sistemas."""
    return jsonify({
        'roulette': {
            'active': active_systems['pragmatic_roulette'],
            'available': PragmaticRouletteAPIMonitor is not None,
            'results_count': len(pragmatic_roulette_system.results_cache) if pragmatic_roulette_system else 0
        },
        'double': {
            'active': active_systems['double'],
            'available': BlazeOfficialAPI is not None,
            'results_count': 0  # TODO: Implementar contador do Blaze
        },
        'jimyobot': {
            'active': active_systems['jimyobot'],
            'available': JimyoBotGameMonitor is not None,
            'games_count': len(jimyobot_system.games_cache) if jimyobot_system else 0
        }
    })

@app.route('/api/systems/start/<system>')
def start_system(system):
    """Inicia um sistema específico."""
    global roulette_system, pragmatic_roulette_system, blaze_system, active_systems
    
    if system == 'roulette' and PragmaticRouletteAPIMonitor:
        if not active_systems['pragmatic_roulette']:
            pragmatic_roulette_system = PragmaticRouletteAPIMonitor()
            pragmatic_roulette_system.start()
            active_systems['pragmatic_roulette'] = True
            return jsonify({'status': 'started', 'system': 'roulette'})
        return jsonify({'status': 'already_running', 'system': 'roulette'})
    
    elif system == 'double' and BlazeOfficialAPI:
        if not active_systems['double']:
            blaze_system = BlazeOfficialAPI()
            active_systems['double'] = True
            return jsonify({'status': 'started', 'system': 'double'})
        return jsonify({'status': 'already_running', 'system': 'double'})
    
    elif system == 'jimyobot' and JimyoBotGameMonitor:
        if not active_systems['jimyobot']:
            # Iniciar JimyoBot em thread separada
            def start_jimyobot():
                import asyncio
                asyncio.run(jimyobot_system.start())
            
            threading.Thread(target=start_jimyobot, daemon=True).start()
            active_systems['jimyobot'] = True
            return jsonify({'status': 'started', 'system': 'jimyobot'})
        return jsonify({'status': 'already_running', 'system': 'jimyobot'})
    
    return jsonify({'status': 'error', 'message': 'Sistema não disponível'})

@app.route('/api/systems/stop/<system>')
def stop_system(system):
    """Para um sistema específico."""
    global roulette_system, pragmatic_roulette_system, blaze_system, active_systems
    
    if system == 'roulette':
        if active_systems['pragmatic_roulette'] and pragmatic_roulette_system:
            pragmatic_roulette_system.stop()
            active_systems['pragmatic_roulette'] = False
            return jsonify({'status': 'stopped', 'system': 'roulette'})
    
    elif system == 'double':
        if active_systems['double']:
            active_systems['double'] = False
            return jsonify({'status': 'stopped', 'system': 'double'})
    
    elif system == 'jimyobot':
        if active_systems['jimyobot'] and jimyobot_system:
            jimyobot_system.stop()
            active_systems['jimyobot'] = False
            return jsonify({'status': 'stopped', 'system': 'jimyobot'})
    
    return jsonify({'status': 'not_running', 'system': system})

# Rotas da Roleta (proxy)
@app.route('/api/dashboard')
def api_dashboard():
    """API do dashboard da roleta."""
    if pragmatic_roulette_system:
        return jsonify(pragmatic_roulette_system.get_dashboard_data())
    return jsonify({'error': 'Sistema da roleta não iniciado'})

@app.route('/api/roulette/dashboard')
def roulette_api_dashboard():
    """Dados do dashboard da roleta."""
    if pragmatic_roulette_system:
        return jsonify(pragmatic_roulette_system.get_dashboard_data())
    return jsonify({'error': 'Sistema da roleta não iniciado'})

@app.route('/api/roulette/results')
def roulette_api_results():
    """Resultados recentes da roleta."""
    limit = request.args.get('limit', 50, type=int)
    if pragmatic_roulette_system:
        results = pragmatic_roulette_system.database.get_recent_results(limit)
        return jsonify([r.to_dict() for r in results])
    return jsonify([])

@app.route('/api/roulette/statistics')
def roulette_api_statistics():
    """Estatísticas da roleta."""
    hours = request.args.get('hours', 24, type=int)
    if pragmatic_roulette_system:
        stats = pragmatic_roulette_system.database.get_statistics(hours)
        return jsonify(stats)
    return jsonify({})

@app.route('/api/jimyobot/dashboard')
def jimyobot_api_dashboard():
    """Dados do dashboard do JimyoBot."""
    if jimyobot_system:
        return jsonify(jimyobot_system.get_dashboard_data())
    return jsonify({'error': 'Sistema JimyoBot não iniciado'})

# Rotas do Double (proxy)
@app.route('/api/double/results')
def double_api_results():
    """Resultados recentes do Double."""
    if blaze_system:
        try:
            results = blaze_system.get_roulette_games(limit=50)
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify([])

# Rota adicional para status em tempo real via polling
@app.route('/api/live/status')
def live_status():
    """Status em tempo real via polling (substitui WebSocket)."""
    return jsonify({
        'roulette': {
            'active': active_systems['pragmatic_roulette'],
            'results_count': len(pragmatic_roulette_system.results_cache) if pragmatic_roulette_system else 0
        },
        'double': {
            'active': active_systems['double'],
            'results_count': 0
        },
        'timestamp': datetime.now().isoformat()
    })

# Mock Socket.IO para evitar erros 404
@app.route('/socket.io/')
def socket_io_mock():
    """Mock do Socket.IO para evitar erros 404."""
    return jsonify({'error': 'Socket.IO não disponível - usando polling HTTP'}), 404

if __name__ == '__main__':
    print("🚀 Dashboard Principal Iniciado!")
    print("📊 Acesse: http://localhost:5000")
    print("🎲 Escolha entre Double (Blaze) ou Roleta Brasileira (Pragmatic Play)")
    print("💡 Para usar o Double, inicie também: python app.py")
    
    # Iniciar servidor Flask simples
    app.run(host='0.0.0.0', port=5000, debug=False)
