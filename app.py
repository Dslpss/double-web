#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backend Web com Polling para o Blaze Double Analyzer
Versão que simula WebSocket usando polling HTTP
"""

# CRÍTICO: Configurar matplotlib ANTES de qualquer import
import matplotlib
matplotlib.use('Agg')  # Usar backend sem GUI para Railway
import matplotlib.pyplot as plt
plt.ioff()  # Desabilitar modo interativo

import sys
import os
import json
import time
import random
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# IMPORTANTE: Carregar variáveis de ambiente ANTES de importar módulos que precisam delas
from dotenv import load_dotenv
load_dotenv()  # Carregar variáveis do .env

# Importar sistema de notificações
try:
    from shared.src.notifications.pattern_notifier import notify_pattern, notify_result, get_notifier
    from shared.src.database.local_storage_db import local_db
    NOTIFICATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: Sistema de notificações não disponível: {e}")
    NOTIFICATIONS_AVAILABLE = False
    def notify_pattern(*args, **kwargs): return False
    def notify_result(*args, **kwargs): pass
    def get_notifier(): return None
    local_db = None

try:
    from shared.blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
    analyzer_available = True
    print("✅ BlazeAnalyzerEnhanced importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar BlazeAnalyzerEnhanced: {e}")
    import traceback
    traceback.print_exc()
    analyzer_available = False

# Importar módulos de autenticação e PlayNabets
try:
    from auth import require_auth, login, logout, register, get_user_info
    auth_available = True
except ImportError as e:
    print(f"Aviso: Módulo de autenticação não disponível: {e}")
    auth_available = False

try:
    from playnabets_integrator import PlayNabetsIntegrator
    playnabets_available = True
except ImportError as e:
    print(f"Aviso: Módulo PlayNabets não disponível: {e}")
    playnabets_available = False

try:
    from integrators.pragmatic_brazilian_roulette import PragmaticBrazilianRoulette
    roulette_available = True
except ImportError as e:
    print(f"Aviso: Módulo Roleta Brasileira não disponível: {e}")
    roulette_available = False

# Inicializar Flask
app = Flask(__name__, template_folder='templates')
CORS(app)

# Variáveis globais
analyzer = None
playnabets_integrator = None
roulette_integrator = None
ws_connected = False
ws_thread = None
last_results = []
last_analysis = {}
clients = set()  # Para rastrear clientes conectados
web_notifications = []  # Para armazenar notificações para o frontend

def web_notification_callback(notification_data):
    """Callback para receber notificações do sistema de notificações"""
    global web_notifications
    print(f"🔔 Callback web recebeu notificação: {notification_data.get('type')} - {notification_data.get('pattern_type', 'N/A')}")
    web_notifications.append(notification_data)
    # Manter apenas as últimas 50 notificações
    if len(web_notifications) > 50:
        web_notifications = web_notifications[-50:]
    print(f"📊 Total de notificações web: {len(web_notifications)} (padrões: {len([n for n in web_notifications if n.get('type') == 'pattern_detected'])})")

def init_analyzer(clear_session_data=True):
    """Inicializa o analyzer."""
    global analyzer
    try:
        print(f"🔍 Tentando inicializar analyzer - analyzer_available: {analyzer_available}")
        if analyzer_available:
            print("Tentando inicializar BlazeAnalyzerEnhanced...")
            analyzer = BlazeAnalyzerEnhanced(use_official_api=False)
            print("✅ Analyzer inicializado com sucesso!")
            
            # Limpar dados da sessão anterior se solicitado
            if clear_session_data:
                print("Limpando dados da sessao anterior...")
                # Limpar listas globais
                last_results.clear()
                last_analysis.clear()
                web_notifications.clear()
                print("Dados da sessao limpos com sucesso!")
            
            # Configurar callback para notificações web
            if NOTIFICATIONS_AVAILABLE:
                notifier = get_notifier()
                if notifier:
                    print("Configurando callback de notificacoes web...")
                    notifier.set_web_callback(web_notification_callback)
                    print("Callback de notificacoes web configurado!")
                    print(f"Notificador - Enabled: {notifier.enabled}, Min Confidence: {notifier.min_confidence}")
                    
                    # Garantir que o notificador está habilitado
                    if not notifier.enabled:
                        notifier.set_enabled(True)
                        print("Notificador habilitado automaticamente!")
                else:
                    print("Notificador nao disponivel!")
            else:
                print("Sistema de notificacoes nao disponivel!")
            
            return True
        else:
            print("Analyzer nao disponivel")
            return False
    except Exception as e:
        print(f"Erro ao inicializar analyzer: {e}")
        return False

def clear_session_data():
    """Limpa dados da sessão atual."""
    global last_results, last_analysis, web_notifications
    
    try:
        # Limpar listas globais
        last_results.clear()
        last_analysis.clear()
        web_notifications.clear()
        
        # Limpar dados do analyzer se disponível
        if analyzer:
            # Limpar dados manuais e da API
            analyzer.manual_data.clear()
            analyzer.data.clear()
            
            # Resetar sistemas de análise se disponíveis
            if hasattr(analyzer, 'dual_pattern_detector'):
                analyzer.dual_pattern_detector.reset()
            
            if hasattr(analyzer, 'adaptive_integrator'):
                analyzer.adaptive_integrator.reset()
            
            print("Dados da sessão limpos com sucesso!")
        else:
            print("Analyzer não disponível para limpeza")
            
    except Exception as e:
        print(f"Erro ao limpar dados da sessão: {e}")

def init_playnabets_integrator(analyzer_instance):
    """Inicializa o integrador PlayNabets."""
    global playnabets_integrator
    try:
        print(f"🔍 Tentando inicializar PlayNabetsIntegrator - playnabets_available: {playnabets_available}")
        print(f"🔍 Analyzer instance: {analyzer_instance is not None}")
        if playnabets_available and analyzer_instance:
            print("Tentando inicializar PlayNabetsIntegrator...")
            playnabets_integrator = PlayNabetsIntegrator(analyzer_instance)
            print("✅ Integrador PlayNabets inicializado com sucesso!")
            return True
        else:
            print(f"⚠️ PlayNabets não disponível - playnabets_available: {playnabets_available}, analyzer_instance: {analyzer_instance is not None}")
            return False
    except Exception as e:
        print(f"❌ Erro ao inicializar integrador PlayNabets: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_websocket_connection():
    """Inicia conexão WebSocket com PlayNabets."""
    global ws_connected, ws_thread
    
    if ws_connected:
        print("[AVISO] Conexão WebSocket já está ativa")
        return
    
    def ws_worker():
        global ws_connected, last_results, last_analysis
        try:
            print("Iniciando conexão PlayNabets...")
            ws_connected = True
            
            if playnabets_integrator:
                playnabets_integrator.start()
                
                # Loop para processar dados
                while ws_connected and playnabets_integrator.running:
                    try:
                        # Verificar status da conexão
                        status = playnabets_integrator.get_status()
                        
                        # Se não está conectado há muito tempo, tentar reconectar
                        if not status['connected'] and status.get('time_since_last_heartbeat', 0) > 60:
                            print("Conexão perdida há mais de 60s. Tentando reconectar...")
                            playnabets_integrator.stop()
                            time.sleep(2)
                            playnabets_integrator.start()
                        
                        # Obter último resultado
                        if hasattr(playnabets_integrator, 'last_result') and playnabets_integrator.last_result:
                            result = playnabets_integrator.last_result
                            
                            # Verificar se é um resultado novo
                            if not last_results or result != last_results[-1]:
                                # Adicionar à lista de resultados
                                last_results.append(result)
                                if len(last_results) > 100:  # Manter apenas últimos 100
                                    last_results = last_results[-100:]
                                
                                print(f"📊 Novo resultado: {result.get('number', 'N/A')} ({result.get('color', 'N/A')})")
                                
                                # Atualizar análise
                                if analyzer:
                                    try:
                                        analysis = analyzer.analyze_comprehensive()
                                        if analysis:
                                            last_analysis = analysis
                                    except Exception as e:
                                        print(f"Erro na análise: {e}")
                        
                        time.sleep(2)  # Atualizar a cada 2 segundos
                        
                    except Exception as e:
                        print(f"Erro no loop WebSocket: {e}")
                        time.sleep(5)
                        
            else:
                print("Integrador PlayNabets não disponível")
                
        except Exception as e:
            print(f"Erro na conexão WebSocket: {e}")
        finally:
            ws_connected = False
            print("Conexão WebSocket finalizada")
    
    ws_thread = threading.Thread(target=ws_worker, name="WebSocketWorker")
    ws_thread.start()
    print("Thread WebSocket iniciada")

def stop_websocket_connection():
    """Para a conexão WebSocket."""
    global ws_connected, ws_thread
    print("Parando conexão WebSocket...")
    ws_connected = False
    
    if playnabets_integrator:
        playnabets_integrator.stop()
    
    # Aguardar thread terminar
    if ws_thread and ws_thread.is_alive():
        print("Aguardando thread WebSocket terminar...")
        ws_thread.join(timeout=10)
        if ws_thread.is_alive():
            print("Thread WebSocket não terminou em 10s")
    
    print("Conexão WebSocket parada")

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
def index():
    """Página principal - Seleção de jogos."""
    return render_template('home.html')

@app.route('/double')
def double():
    """Página do Double (antigo index)."""
    return render_template('polling_index.html')

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

@app.route('/roulette')
def roulette():
    """Roleta Brasileira Pragmatic Play."""
    return render_template('roulette.html')

# ===== API ENDPOINTS =====

@app.route('/api/status')
def get_status():
    """Status do sistema."""
    status = {
        'analyzer_ready': analyzer is not None,
        'analyzer_available': analyzer_available,
        'playnabets_connected': ws_connected,
        'playnabets_available': playnabets_available,
        'auth_available': auth_available,
        'notifications_available': NOTIFICATIONS_AVAILABLE,
        'timestamp': int(time.time())
    }
    
    # Adicionar status detalhado do PlayNabets
    if playnabets_integrator:
        playnabets_status = playnabets_integrator.get_status()
        status.update({
            'playnabets_status': playnabets_status,
            'last_result': playnabets_status.get('last_result'),
            'reconnect_attempts': playnabets_status.get('reconnect_attempts', 0),
            'max_reconnect_attempts': playnabets_status.get('max_reconnect_attempts', 10),
            'time_since_last_heartbeat': playnabets_status.get('time_since_last_heartbeat')
        })
    else:
        status['playnabets_error'] = 'PlayNabets integrator not initialized'
    
    # Adicionar estatísticas de resultados
    status.update({
        'total_results': len(last_results),
        'last_analysis_available': bool(last_analysis),
        'web_notifications_count': len(web_notifications)
    })
    
    return jsonify(status)

@app.route('/api/results')
def get_results():
    """Obtém resultados recentes da sessão atual."""
    try:
        # Usar apenas os resultados da sessão atual (last_results)
        # Não usar dados históricos do analyzer
        results = []
        
        # Converter last_results para formato JSON serializável
        for item in last_results:
            if isinstance(item, dict):
                results.append({
                    'id': item.get('id', f'result_{len(results)}'),
                    'roll': item.get('roll', item.get('number', 0)),
                    'number': item.get('roll', item.get('number', 0)),
                    'color': item.get('color', 'unknown'),
                    'timestamp': item.get('timestamp', int(time.time()))
                })
        
        # Ordenar por timestamp (mais recentes primeiro)
        results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'session_only': True,  # Indica que são apenas dados da sessão
            'timestamp': int(time.time())
        })
        
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
            
            # Adicionar à lista de resultados
            result = {
                'number': number,
                'color': color or ('white' if number == 0 else 'red' if 1 <= number <= 7 else 'black'),
                'timestamp': int(time.time())
            }
            
            # Usar a lista global de resultados
            global last_results
            last_results.append(result)
            if len(last_results) > 100:
                last_results = last_results[-100:]
            
            # Resultado adicionado com sucesso (notificações de padrão são feitas automaticamente)
            
            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'error': 'Analyzer não disponível'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== POLLING ENDPOINTS (SIMULAM WEBSOCKET) =====

@app.route('/api/poll/results')
def poll_results():
    """Polling para resultados (simula WebSocket)."""
    try:
        # Retornar últimos resultados
        return jsonify({
            'results': last_results[-20:],  # Últimos 20 resultados
            'timestamp': int(time.time())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/poll/analysis')
def poll_analysis():
    """Polling para análise (simula WebSocket)."""
    try:
        return jsonify(last_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/poll/status')
def poll_status():
    """Polling para status (simula WebSocket)."""
    try:
        return jsonify({
            'connected': ws_connected,
            'analyzer_ready': analyzer is not None,
            'timestamp': int(time.time())
        })
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

@app.route('/api/playnabets/reconnect', methods=['POST'])
def playnabets_reconnect():
    """Força reconexão PlayNabets."""
    try:
        if not playnabets_integrator:
            return jsonify({'error': 'Integrador PlayNabets não disponível'}), 500
        
        print("🔄 Forçando reconexão PlayNabets...")
        
        # Parar conexão atual
        stop_websocket_connection()
        time.sleep(2)
        
        # Reiniciar conexão
        start_websocket_connection()
        
        return jsonify({
            'success': True,
            'message': 'Reconexão PlayNabets iniciada'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CONFIGURAÇÕES PLAYNABETS =====

@app.route('/api/playnabets/config', methods=['GET'])
def get_playnabets_config():
    """Obtém configurações do PlayNabets."""
    try:
        # Configurações padrão
        default_config = {
            'confidence_threshold': 0.7,
            'alerts_enabled': True
        }
        
        # Aqui você pode carregar configurações do banco de dados ou arquivo
        # Por enquanto, retornamos as configurações padrão
        return jsonify({
            'success': True,
            'config': default_config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playnabets/config', methods=['POST'])
def save_playnabets_config():
    """Salva configurações do PlayNabets."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados de configuração não fornecidos'}), 400
        
        # Validar dados
        confidence_threshold = data.get('confidence_threshold', 0.7)
        alerts_enabled = data.get('alerts_enabled', True)
        
        # Validar confiabilidade (0.1 a 1.0)
        if not (0.1 <= confidence_threshold <= 1.0):
            return jsonify({'error': 'Taxa de confiabilidade deve estar entre 10% e 100%'}), 400
        
        # Aqui você pode salvar as configurações no banco de dados
        # Por enquanto, apenas validamos e retornamos sucesso
        
        print(f"💾 Configurações PlayNabets salvas:")
        print(f"   - Taxa de confiabilidade: {confidence_threshold:.1%}")
        print(f"   - Alertas habilitados: {alerts_enabled}")
        
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso',
            'config': {
                'confidence_threshold': confidence_threshold,
                'alerts_enabled': alerts_enabled
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== NOTIFICAÇÕES =====

@app.route('/api/notifications/status', methods=['GET'])
def notifications_status():
    """Status do sistema de notificações."""
    try:
        if not NOTIFICATIONS_AVAILABLE:
            return jsonify({
                'available': False,
                'message': 'Sistema de notificações não disponível'
            })
        
        notifier = get_notifier()
        if notifier:
            stats = notifier.get_stats()
            return jsonify({
                'available': True,
                'enabled': notifier.enabled,
                'min_confidence': notifier.min_confidence,
                'stats': stats
            })
        else:
            return jsonify({
                'available': True,
                'enabled': False,
                'message': 'Notificador não inicializado'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/config', methods=['POST'])
def notifications_config():
    """Configura sistema de notificações."""
    try:
        if not NOTIFICATIONS_AVAILABLE:
            return jsonify({'error': 'Sistema de notificações não disponível'}), 500
        
        data = request.get_json()
        notifier = get_notifier()
        
        if not notifier:
            return jsonify({'error': 'Notificador não disponível'}), 500
        
        # Atualizar configurações
        if 'enabled' in data:
            notifier.set_enabled(bool(data['enabled']))
        
        if 'min_confidence' in data:
            confidence = float(data['min_confidence'])
            notifier.set_min_confidence(confidence)
        
        return jsonify({
            'success': True,
            'enabled': notifier.enabled,
            'min_confidence': notifier.min_confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/clear', methods=['POST'])
def notifications_clear():
    """Limpa a tela de notificações."""
    try:
        if not NOTIFICATIONS_AVAILABLE:
            return jsonify({'error': 'Sistema de notificações não disponível'}), 500
        
        notifier = get_notifier()
        if notifier:
            notifier.clear_screen()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Notificador não disponível'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/web')
def get_web_notifications():
    """Obtém notificações para o frontend."""
    try:
        global web_notifications
        
        # Retornar todas as notificações (padrões e resultados)
        # O frontend decide qual exibir
        return jsonify({
            'notifications': web_notifications[-20:],  # Últimas 20 notificações
            'total': len(web_notifications),
            'timestamp': int(time.time())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/cooldown/status', methods=['GET'])
def get_cooldown_status():
    """Status dos cooldowns ativos"""
    try:
        if not NOTIFICATIONS_AVAILABLE:
            return jsonify({'error': 'Sistema de notificações não disponível'}), 500
        
        notifier = get_notifier()
        if notifier:
            status = notifier.get_cooldown_status()
            return jsonify({
                'success': True,
                'cooldown_status': status
            })
        else:
            return jsonify({'error': 'Notificador não disponível'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/cooldown/clear', methods=['POST'])
def clear_cooldown():
    """Limpa cooldowns de padrões"""
    try:
        if not NOTIFICATIONS_AVAILABLE:
            return jsonify({'error': 'Sistema de notificações não disponível'}), 500
        
        data = request.get_json() or {}
        pattern_type = data.get('pattern_type')  # None para limpar todos
        
        notifier = get_notifier()
        if notifier:
            success = notifier.clear_cooldown(pattern_type)
            return jsonify({
                'success': success,
                'message': f'Cooldown {"limpo" if success else "não encontrado"}',
                'pattern_type': pattern_type
            })
        else:
            return jsonify({'error': 'Notificador não disponível'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/web/clear', methods=['POST'])
def clear_web_notifications():
    """Limpa notificações web."""
    try:
        global web_notifications
        web_notifications = []
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ROLETA BRASILEIRA (PRAGMATIC PLAY) =====

@app.route('/api/roulette/status')
def roulette_status():
    """Status do integrador da Roleta Brasileira."""
    try:
        global roulette_integrator
        
        print("\n🔍 [ROULETTE STATUS] Verificando status do integrador...")
        
        # Verificar se módulo está disponível
        if not roulette_available:
            error_msg = "Módulo PragmaticBrazilianRoulette não está disponível"
            print(f"❌ {error_msg}")
            return jsonify({
                'available': False,
                'connected': False,
                'monitoring': False,
                'error': error_msg,
                'details': 'Verifique se o arquivo integrators/pragmatic_brazilian_roulette.py existe'
            })
        
        print("✅ Módulo disponível")
        
        # Verificar credenciais
        pragmatic_username = os.getenv('PLAYNABETS_USER')
        pragmatic_password = os.getenv('PLAYNABETS_PASS')
        has_credentials = bool(pragmatic_username and pragmatic_password)
        
        print(f"� Credenciais: {'✅ Configuradas' if has_credentials else '❌ NÃO configuradas'}")
        
        # Verificar estado do integrador
        if roulette_integrator is None:
            print("⚠️ Integrador não está inicializado")
            
            # Verificar se auto-start está habilitado
            auto_start_enabled = os.getenv('ROULETTE_AUTO_START', 'false').lower() == 'true'
            print(f"🔧 Auto-start: {'✅ Habilitado' if auto_start_enabled else '❌ Desabilitado'}")
            
            # Tentar inicializar automaticamente se tiver credenciais E auto-start habilitado
            if has_credentials and auto_start_enabled:
                print("🔄 Tentando inicializar automaticamente...")
                success = init_roulette_integrator()
                
                if success and roulette_integrator is not None:
                    print("✅ Integrador inicializado automaticamente com sucesso!")
                    
                    # Verificar se realmente conectou
                    is_connected = roulette_integrator.jsessionid is not None
                    
                    return jsonify({
                        'available': True,
                        'connected': is_connected,
                        'monitoring': is_connected,
                        'has_credentials': has_credentials,
                        'session_id': bool(roulette_integrator.jsessionid),
                        'auto_started': True,
                        'message': 'Integrador inicializado automaticamente'
                    })
                else:
                    print("❌ Falha ao inicializar automaticamente")
                    
                    # Se auto-start falhar, não retornar erro - permitir uso manual
                    return jsonify({
                        'available': True,
                        'connected': False,
                        'monitoring': False,
                        'has_credentials': has_credentials,
                        'auto_start_failed': True,
                        'auto_start_enabled': True,
                        'message': 'Auto-start falhou. Clique em "Iniciar Monitoramento" para tentar manualmente.'
                    })
            
            # Auto-start desabilitado ou sem credenciais
            message = 'Integrador não inicializado.'
            if not has_credentials:
                message += ' Configure as credenciais (PLAYNABETS_USER e PLAYNABETS_PASS).'
            elif not auto_start_enabled:
                message += ' Clique em "Iniciar Monitoramento" ou habilite ROULETTE_AUTO_START=true.'
            
            return jsonify({
                'available': True,
                'connected': False,
                'monitoring': False,
                'has_credentials': has_credentials,
                'auto_start_enabled': auto_start_enabled,
                'message': message
            })
        
        # Verificar se está conectado
        is_connected = roulette_integrator.jsessionid is not None
        
        print(f"📡 Status: {'✅ Conectado' if is_connected else '❌ Desconectado'}")
        print(f"   JSESSIONID: {roulette_integrator.jsessionid[:30] if roulette_integrator.jsessionid else 'None'}...")
        
        return jsonify({
            'available': True,
            'connected': is_connected,
            'monitoring': is_connected,
            'has_credentials': has_credentials,
            'session_id': bool(roulette_integrator.jsessionid),
            'last_update': roulette_integrator.last_update_time.isoformat() if hasattr(roulette_integrator, 'last_update_time') and roulette_integrator.last_update_time else None
        })
    except Exception as e:
        error_msg = f"Erro ao verificar status: {str(e)}"
        print(f"❌ [ROULETTE STATUS] {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'available': False,
            'connected': False,
            'monitoring': False,
            'error': error_msg
        }), 500

def init_roulette_integrator():
    """Inicializa o integrador da Roleta Brasileira."""
    global roulette_integrator
    
    if roulette_integrator is not None:
        print("ℹ️ Integrador já está inicializado")
        return True
    
    if not roulette_available:
        error_msg = "Módulo da Roleta não disponível - verifique a importação do PragmaticBrazilianRoulette"
        print(f"⚠️ {error_msg}")
        raise Exception(error_msg)
    
    try:
        print("🔧 Inicializando integrador da Roleta Brasileira...")
        
        # Carregar credenciais do .env
        pragmatic_username = os.getenv('PLAYNABETS_USER')
        pragmatic_password = os.getenv('PLAYNABETS_PASS')
        
        print(f"🔍 Verificando credenciais...")
        print(f"   Username: {'✅ Configurado' if pragmatic_username else '❌ NÃO configurado'}")
        print(f"   Password: {'✅ Configurado' if pragmatic_password else '❌ NÃO configurado'}")
        
        if not pragmatic_username or not pragmatic_password:
            error_msg = "Credenciais da Roleta não configuradas (PLAYNABETS_USER e PLAYNABETS_PASS)"
            print(f"⚠️ {error_msg}")
            raise Exception(error_msg)
        
        print(f"🎰 Criando instância do PragmaticBrazilianRoulette...")
        roulette_integrator = PragmaticBrazilianRoulette(
            username=pragmatic_username,
            password=pragmatic_password
        )
        
        # Fazer login
        print("🔐 Fazendo login na Roleta Brasileira...")
        login_success = roulette_integrator.login()
        
        if not login_success:
            error_msg = "Falha ao fazer login na Roleta Brasileira - credenciais inválidas ou erro de conexão"
            print(f"❌ {error_msg}")
            roulette_integrator = None
            return False  # Retorna False em vez de lançar exceção
        
        print("✅ Integrador da Roleta Brasileira inicializado com sucesso")
        print(f"   JSESSIONID: {'✅ Obtido' if roulette_integrator.jsessionid else '❌ Não obtido'}")
        return True
        
    except Exception as e:
        error_msg = f"Erro ao inicializar integrador da Roleta: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        roulette_integrator = None
        return False  # Retorna False em vez de lançar exceção

@app.route('/api/roulette/start', methods=['POST'])
def roulette_start():
    """Inicia monitoramento da Roleta Brasileira."""
    try:
        print("\n" + "="*60)
        print("🎰 [ROULETTE START] Requisição recebida")
        print("="*60)
        
        # Verificar se módulo está disponível
        if not roulette_available:
            error_msg = "Módulo PragmaticBrazilianRoulette não está disponível. Verifique a instalação."
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'details': 'Módulo não importado corretamente no app.py'
            }), 500
        
        # Inicializar integrador se necessário
        print("🔄 Chamando init_roulette_integrator()...")
        success = init_roulette_integrator()
        
        if success:
            print("✅ Integrador inicializado com sucesso")
            print("="*60 + "\n")
            
            return jsonify({
                'success': True,
                'message': 'Monitoramento da Roleta Brasileira iniciado',
                'connected': True,
                'monitoring': True
            })
        else:
            print("❌ Falha ao inicializar integrador")
            print("="*60 + "\n")
            
            return jsonify({
                'success': False,
                'error': 'Falha ao inicializar integrador da Roleta Brasileira',
                'details': 'Verifique as credenciais (PLAYNABETS_USER e PLAYNABETS_PASS) e os logs do servidor'
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ [ROULETTE START] ERRO INESPERADO: {error_msg}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'details': 'Erro inesperado. Verifique os logs do servidor'
        }), 500

@app.route('/api/roulette/stop', methods=['POST'])
def roulette_stop():
    """Para monitoramento da Roleta Brasileira."""
    try:
        global roulette_integrator
        
        if roulette_integrator is None:
            return jsonify({
                'success': True,
                'message': 'Integrador não estava ativo'
            })
        
        # Parar monitoramento (se houver método stop_monitoring)
        if hasattr(roulette_integrator, 'monitoring') and roulette_integrator.monitoring:
            if hasattr(roulette_integrator, 'stop_monitoring'):
                roulette_integrator.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento da Roleta Brasileira parado',
            'connected': roulette_integrator.jsessionid is not None,
            'monitoring': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/roulette/results')
def roulette_results():
    """Últimos resultados da Roleta Brasileira."""
    try:
        global roulette_integrator
        
        if roulette_integrator is None:
            return jsonify({
                'success': False,
                'results': [],
                'message': 'Integrador não inicializado'
            })
        
        # Buscar resultados do histórico
        results = roulette_integrator.get_history(num_games=20)
        
        # Verificar se results não é None
        if results is None:
            results = []
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'timestamp': int(time.time())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/roulette/analysis')
def roulette_analysis():
    """Análise de padrões da Roleta Brasileira."""
    try:
        global roulette_integrator
        
        if roulette_integrator is None:
            return jsonify({
                'success': False,
                'analysis': {},
                'message': 'Integrador não inicializado'
            })
        
        # Buscar resultados para análise
        results = roulette_integrator.get_history(num_games=100)
        
        # Verificar se results não é None
        if results is None:
            results = []
        
        if not results:
            return jsonify({
                'success': True,
                'analysis': {
                    'total_spins': 0,
                    'message': 'Nenhum resultado disponível ainda'
                }
            })
        
        # Análise básica
        analysis = {
            'total_spins': len(results),
            'numbers': {},
            'colors': {'red': 0, 'black': 0, 'green': 0},
            'dozens': {'first': 0, 'second': 0, 'third': 0},
            'even_odd': {'even': 0, 'odd': 0},
            'high_low': {'high': 0, 'low': 0},
            'recent_numbers': [r.get('number') for r in results[:10]]  # Últimos 10 números
        }
        
        for result in results:
            number = result.get('number', 0)
            color = result.get('color', '').lower()
            
            # Contar números
            analysis['numbers'][str(number)] = analysis['numbers'].get(str(number), 0) + 1
            
            # Contar cores (usar a cor já fornecida pelo resultado)
            if color in ['red', 'black', 'green']:
                analysis['colors'][color] += 1
            
            # Contar dúzias
            if 1 <= number <= 12:
                analysis['dozens']['first'] += 1
            elif 13 <= number <= 24:
                analysis['dozens']['second'] += 1
            elif 25 <= number <= 36:
                analysis['dozens']['third'] += 1
            
            # Par/Ímpar (ignorar zero)
            if number > 0:
                if number % 2 == 0:
                    analysis['even_odd']['even'] += 1
                else:
                    analysis['even_odd']['odd'] += 1
                
                # Alto/Baixo
                if number <= 18:
                    analysis['high_low']['low'] += 1
                else:
                    analysis['high_low']['high'] += 1
        
        # Encontrar números quentes (mais frequentes)
        sorted_numbers = sorted(analysis['numbers'].items(), key=lambda x: x[1], reverse=True)
        analysis['hot_numbers'] = sorted_numbers[:5]
        
        # Encontrar números frios (menos frequentes)
        analysis['cold_numbers'] = sorted_numbers[-5:]
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': int(time.time())
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== ANÁLISE AVANÇADA DE PADRÕES (FASE 2) =====

# Inicializar analisador avançado
roulette_advanced_analyzer = None
try:
    from analyzers.roulette_analyzer import RouletteAdvancedAnalyzer
    roulette_advanced_analyzer = RouletteAdvancedAnalyzer()
    print("✅ Analisador avançado de roleta inicializado")
except ImportError as e:
    print(f"⚠️ Analisador avançado não disponível: {e}")

@app.route('/api/roulette/patterns/basic')
def roulette_basic_patterns():
    """
    Retorna análise básica de padrões (cache de 5 segundos)
    Essa rota serve dados para o detector JavaScript
    """
    try:
        # Inicializar integrador automaticamente se necessário
        if not init_roulette_integrator():
            return jsonify({
                'success': False,
                'patterns': [],
                'message': 'Integrador não disponível'
            })
        
        # Buscar últimos 100 resultados
        results = roulette_integrator.get_history(num_games=100)
        
        # Verificar se results não é None
        if results is None:
            results = []
        
        if not results:
            return jsonify({
                'success': True,
                'patterns': [],
                'results': [],
                'message': 'Nenhum resultado disponível'
            })
        
        # Retornar resultados formatados para o JavaScript
        formatted_results = []
        for r in results:
            formatted_results.append({
                'number': r.get('number'),
                'color': r.get('color', '').lower(),
                'timestamp': r.get('timestamp', int(time.time()))
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'count': len(formatted_results),
            'timestamp': int(time.time())
        }), 200, {
            'Cache-Control': 'public, max-age=5'  # Cache de 5 segundos
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/roulette/patterns/advanced')
def roulette_advanced_patterns():
    """
    Retorna análise avançada de padrões usando Python (cache de 30 segundos)
    Inclui: setores, bias, clusters espaciais, tendências temporais
    """
    try:
        # Inicializar integrador automaticamente se necessário
        if not init_roulette_integrator():
            return jsonify({
                'success': False,
                'patterns': [],
                'message': 'Integrador não disponível'
            })
        
        if roulette_advanced_analyzer is None:
            return jsonify({
                'success': False,
                'patterns': [],
                'message': 'Analisador avançado não disponível'
            })
        
        # Buscar resultados para análise (pelo menos 100 para detecção de bias)
        results = roulette_integrator.get_history(num_games=150)
        
        if not results:
            return jsonify({
                'success': True,
                'patterns': [],
                'message': 'Nenhum resultado disponível'
            })
        
        # Formatar resultados
        formatted_results = []
        for r in results:
            formatted_results.append({
                'number': r.get('number'),
                'color': r.get('color', '').lower(),
                'timestamp': r.get('timestamp', int(time.time()))
            })
        
        # Executar análise avançada
        print("🔬 Executando análise avançada...")
        patterns = roulette_advanced_analyzer.analyze_all_advanced_patterns(formatted_results)
        if patterns is None:
            patterns = []
        print(f"✅ {len(patterns)} padrões detectados")
        
        # Obter estatísticas gerais
        print("📊 Obtendo estatísticas...")
        stats = roulette_advanced_analyzer.get_comprehensive_stats(formatted_results)
        print("✅ Estatísticas obtidas")
        
        # Testar serialização de cada componente
        print("🧪 Testando serialização...")
        try:
            json.dumps(patterns)
            print("✅ Padrões serializáveis")
        except Exception as e:
            print(f"❌ Erro na serialização de padrões: {e}")
            return jsonify({'success': False, 'error': f'Erro padrões: {e}'}), 500
        
        try:
            json.dumps(stats)
            print("✅ Estatísticas serializáveis")
        except Exception as e:
            print(f"❌ Erro na serialização de estatísticas: {e}")
            return jsonify({'success': False, 'error': f'Erro estatísticas: {e}'}), 500
        
        print("🚀 Retornando resposta...")
        return jsonify({
            'success': True,
            'patterns': patterns,
            'statistics': stats,
            'total_results': len(formatted_results),
            'timestamp': int(time.time())
        }), 200, {
            'Cache-Control': 'public, max-age=30'  # Cache de 30 segundos
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/roulette/patterns/all')
def roulette_all_patterns():
    """
    Retorna TODOS os padrões (básicos + avançados) consolidados
    """
    try:
        # Esta rota combina os resultados das duas análises
        # Frontend pode usar esta única rota para obter tudo
        
        basic_data = roulette_basic_patterns()
        basic_json = basic_data[0].get_json()
        
        advanced_data = roulette_advanced_patterns()
        advanced_json = advanced_data[0].get_json()
        
        if not basic_json.get('success') or not advanced_json.get('success'):
            return jsonify({
                'success': False,
                'message': 'Erro ao obter padrões'
            })
        
        # Consolidar
        all_patterns = advanced_json.get('patterns', [])
        
        return jsonify({
            'success': True,
            'results': basic_json.get('results', []),
            'patterns': {
                'basic': [],  # Detectados no frontend com JavaScript
                'advanced': all_patterns
            },
            'statistics': advanced_json.get('statistics', {}),
            'timestamp': int(time.time())
        }), 200, {
            'Cache-Control': 'public, max-age=10'  # Cache intermediário
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== BANCO DE DADOS LOCAL =====

@app.route('/api/db/stats', methods=['GET'])
def get_db_stats():
    """Estatísticas do banco de dados local."""
    try:
        if not local_db:
            return jsonify({'error': 'Banco de dados local não disponível'}), 500
        
        stats = local_db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/patterns', methods=['GET'])
def get_db_patterns():
    """Padrões salvos no banco local."""
    try:
        if not local_db:
            return jsonify({'error': 'Banco de dados local não disponível'}), 500
        
        count = request.args.get('count', 20, type=int)
        patterns = local_db.get_recent_patterns(count)
        return jsonify({'patterns': patterns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/results', methods=['GET'])
def get_db_results():
    """Resultados salvos no banco local."""
    try:
        if not local_db:
            return jsonify({'error': 'Banco de dados local não disponível'}), 500
        
        count = request.args.get('count', 50, type=int)
        results = local_db.get_recent_results(count)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/clear', methods=['POST'])
def clear_db():
    """Limpa banco de dados local."""
    try:
        if not local_db:
            return jsonify({'error': 'Banco de dados local não disponível'}), 500
        
        data_type = request.json.get('type', 'all') if request.json else 'all'
        success = local_db.clear_data(data_type)
        
        if success:
            return jsonify({'success': True, 'message': f'Dados {data_type} limpos'})
        else:
            return jsonify({'error': 'Erro ao limpar dados'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db/export', methods=['POST'])
def export_db():
    """Exporta banco de dados local."""
    try:
        if not local_db:
            return jsonify({'error': 'Banco de dados local não disponível'}), 500
        
        file_path = local_db.export_data()
        if file_path:
            return jsonify({'success': True, 'file_path': file_path})
        else:
            return jsonify({'error': 'Erro ao exportar dados'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/pattern_status', methods=['GET'])
def debug_pattern_status():
    """Endpoint de debug para verificar status da detecção de padrões."""
    try:
        status = {
            'analyzer_available': analyzer is not None,
            'manual_data_count': len(analyzer.manual_data) if analyzer else 0,
            'api_data_count': len(analyzer.data) if analyzer else 0,
            'total_web_notifications': len(web_notifications),
            'pattern_notifications': len([n for n in web_notifications if n.get('type') == 'pattern_detected']),
            'notifier_enabled': False,
            'notifier_min_confidence': 0.6,
            'web_callback_configured': False
        }
        
        # Verificar notificador
        try:
            from shared.src.notifications.pattern_notifier import get_notifier
            notifier = get_notifier()
            if notifier:
                status['notifier_enabled'] = notifier.enabled
                status['notifier_min_confidence'] = notifier.min_confidence
                status['notifier_history_count'] = len(notifier.notifications_history)
                status['web_callback_configured'] = notifier.web_callback is not None
        except Exception as e:
            status['notifier_error'] = str(e)
        
        # Obter últimos resultados
        if analyzer and analyzer.manual_data:
            status['last_5_results'] = [
                {'number': r.get('roll', r.get('number', 0)), 'color': r.get('color', 'unknown')}
                for r in analyzer.manual_data[-5:]
            ]
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/force_pattern_detection', methods=['POST'])
def force_pattern_detection():
    """Força detecção de padrões e envia notificação de teste."""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não disponível'}), 500
        
        # Forçar análise
        analyzer.analyze_comprehensive()
        
        # Enviar notificação de teste
        from shared.src.notifications.pattern_notifier import get_notifier
        notifier = get_notifier()
        if notifier and notifier.web_callback:
            test_notification = {
                'type': 'pattern_detected',
                'pattern_type': 'Teste Manual',
                'detected_number': 999,
                'predicted_color': 'red',
                'confidence': 0.8,
                'reasoning': 'Notificação de teste enviada manualmente',
                'timestamp': '2025-09-30T16:30:00',
                'pattern_id': 'test_manual'
            }
            notifier.web_callback(test_notification)
            return jsonify({'success': True, 'message': 'Notificação de teste enviada'})
        else:
            return jsonify({'error': 'Notificador ou callback não disponível'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/force_analysis', methods=['POST'])
def force_analysis():
    """Força nova análise completa do sistema."""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não disponível'}), 500
        
        # Limpar notificações antigas
        global web_notifications
        web_notifications = []
        
        # Forçar análise completa
        analysis = analyzer.analyze_comprehensive()
        
        # Forçar detecção de padrões
        if hasattr(analyzer, '_detect_and_notify_patterns'):
            analyzer._detect_and_notify_patterns()
        
        return jsonify({
            'success': True, 
            'message': 'Análise forçada executada',
            'analysis_available': analysis is not None,
            'notifications_cleared': True
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/reset_system', methods=['POST'])
def reset_system():
    """Reseta o sistema após detecção de padrão."""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não disponível'}), 500
        
        # Obter parâmetros da requisição
        data = request.get_json() or {}
        keep_context = data.get('keep_context', True)  # Padrão: manter contexto
        
        # Limpar notificações web
        global web_notifications
        web_notifications = []
        
        # Resetar sistema no analyzer
        if hasattr(analyzer, '_reset_system_after_pattern'):
            analyzer._reset_system_after_pattern(keep_context=keep_context)
        
        return jsonify({
            'success': True, 
            'message': f'Sistema resetado {"com contexto" if keep_context else "completamente"}',
            'notifications_cleared': True,
            'keep_context': keep_context
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """Limpa todos os dados da sessão atual."""
    try:
        print("🧹 Limpeza de sessão solicitada via API...")
        clear_session_data()
        
        return jsonify({
            'success': True,
            'message': 'Sessão limpa com sucesso',
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/status', methods=['GET'])
def session_status():
    """Status da sessão atual."""
    try:
        status = {
            'total_results': len(last_results),
            'last_analysis_available': bool(last_analysis),
            'web_notifications_count': len(web_notifications),
            'analyzer_manual_data': len(analyzer.manual_data) if analyzer else 0,
            'analyzer_api_data': len(analyzer.data) if analyzer else 0,
            'session_start_time': int(time.time()),
            'playnabets_connected': ws_connected
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnostics')
def get_diagnostics():
    """Diagnóstico completo do sistema para debug."""
    try:
        import sys
        import os
        
        diagnostics = {
            'system': {
                'python_version': sys.version,
                'platform': sys.platform,
                'cwd': os.getcwd(),
                'python_path': sys.path[:5],  # Primeiros 5 paths
            },
            'modules': {
                'analyzer_available': analyzer_available,
                'playnabets_available': playnabets_available,
                'auth_available': auth_available,
                'notifications_available': NOTIFICATIONS_AVAILABLE,
            },
            'instances': {
                'analyzer_initialized': analyzer is not None,
                'playnabets_initialized': playnabets_integrator is not None,
            },
            'environment': {
                'PORT': os.environ.get('PORT', 'Not set'),
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not set'),
                'SECRET_KEY': 'Set' if os.environ.get('SECRET_KEY') else 'Not set',
            },
            'files': {
                'config_py_exists': os.path.exists('config.py'),
                'playnabets_integrator_exists': os.path.exists('playnabets_integrator.py'),
                'auth_py_exists': os.path.exists('auth.py'),
                'shared_dir_exists': os.path.exists('shared'),
                'blaze_analyzer_exists': os.path.exists('shared/blaze_analyzer_enhanced.py'),
                'src_init_exists': os.path.exists('shared/src/__init__.py'),
            },
            'errors': []
        }
        
        # Tentar importar módulos e capturar erros
        try:
            import config
            diagnostics['modules']['config_import'] = 'Success'
        except Exception as e:
            diagnostics['modules']['config_import'] = f'Error: {str(e)}'
            diagnostics['errors'].append(f'Config import: {str(e)}')
        
        try:
            from playnabets_integrator import PlayNabetsIntegrator
            diagnostics['modules']['playnabets_import'] = 'Success'
        except Exception as e:
            diagnostics['modules']['playnabets_import'] = f'Error: {str(e)}'
            diagnostics['errors'].append(f'PlayNabets import: {str(e)}')
        
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
            from shared.blaze_analyzer_enhanced import BlazeAnalyzerEnhanced
            diagnostics['modules']['analyzer_import'] = 'Success'
        except Exception as e:
            diagnostics['modules']['analyzer_import'] = f'Error: {str(e)}'
            diagnostics['errors'].append(f'Analyzer import: {str(e)}')
        
        return jsonify(diagnostics)
        
    except Exception as e:
        return jsonify({'error': f'Diagnostics failed: {str(e)}'}), 500

# 🆕 ENDPOINTS PARA SISTEMA ADAPTATIVO

@app.route('/api/pattern_performance', methods=['GET'])
def get_pattern_performance():
    """Retorna estatísticas de performance de padrões"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 503
        
        stats = analyzer.get_pattern_performance_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction_mode', methods=['GET', 'POST'])
def prediction_mode():
    """Obtém ou define o modo de predição"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 503
        
        if request.method == 'GET':
            # Retornar modo atual
            return jsonify({
                'success': True,
                'mode': analyzer.prediction_mode,
                'options': ['opposite', 'continue'],
                'description': {
                    'opposite': 'Apostar na cor oposta (regressão à média)',
                    'continue': 'Continuar na mesma cor (hot hand)'
                }
            })
        
        elif request.method == 'POST':
            # Alterar modo
            data = request.get_json() or {}
            new_mode = data.get('mode', '').lower()
            
            if new_mode not in ['opposite', 'continue']:
                return jsonify({
                    'error': 'Modo inválido. Use "opposite" ou "continue"'
                }), 400
            
            success = analyzer.set_prediction_mode(new_mode)
            
            return jsonify({
                'success': success,
                'mode': analyzer.prediction_mode,
                'message': f'Modo alterado para: {new_mode}'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_pattern_result', methods=['POST'])
def update_pattern_result():
    """Atualiza resultado de uma predição de padrão"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 503
        
        data = request.get_json() or {}
        pattern_id = data.get('pattern_id')
        was_correct = data.get('was_correct')
        
        if not pattern_id or was_correct is None:
            return jsonify({
                'error': 'pattern_id e was_correct são obrigatórios'
            }), 400
        
        analyzer.update_pattern_performance(pattern_id, bool(was_correct))
        
        # Retornar estatísticas atualizadas
        stats = analyzer.get_pattern_performance_stats()
        
        return jsonify({
            'success': True,
            'message': 'Performance atualizada',
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adaptive_settings', methods=['GET'])
def get_adaptive_settings():
    """Retorna configurações adaptativas atuais"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer não inicializado'}), 503
        
        return jsonify({
            'success': True,
            'settings': {
                'thresholds': analyzer.adaptive_thresholds,
                'performance': analyzer.pattern_performance,
                'prediction_mode': analyzer.prediction_mode,
                'signal_history_size': len(analyzer.signal_history)
            },
            'description': {
                'thresholds': 'Confiança mínima adaptativa por tipo de padrão',
                'performance': 'Taxa de acerto histórica por tipo',
                'prediction_mode': 'Modo atual de predição (opposite/continue)',
                'signal_history_size': 'Número de sinais no histórico'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ROTAS DA ROLETA BRASILEIRA (REMOVIDAS - DUPLICATAS) =====
# As rotas da roleta foram movidas para a seção principal acima para evitar duplicação

if __name__ == '__main__':
    print("🚀 Iniciando Blaze Web Backend (Versao Polling)...")
    
    # Inicializar analyzer
    print("📊 Inicializando analyzer...")
    analyzer_ready = init_analyzer()
    
    # Inicializar integrador PlayNabets
    if analyzer_ready:
        print("🔌 Inicializando integrador PlayNabets...")
        playnabets_ready = init_playnabets_integrator(analyzer)
        
        if playnabets_ready:
            # Iniciar conexão PlayNabets automaticamente
            print("🌐 Iniciando conexão automática com PlayNabets...")
            start_websocket_connection()
        else:
            print("⚠️ PlayNabets não pôde ser inicializado")
    else:
        print("⚠️ Analyzer não disponível - PlayNabets não será inicializado")
    
    print("Sistema pronto!")
    print("Servidor iniciando em http://localhost:5000")
    print("Polling ativo para atualizacoes em tempo real")
    print("Conexão PlayNabets iniciada automaticamente")
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

# Importar PragmaticAnalyzer (nova solução)
try:
    from shared.pragmatic_analyzer import PragmaticAnalyzer, initialize_pragmatic_analyzer
    pragmatic_analyzer_available = True
    print("PragmaticAnalyzer importado com sucesso")
except ImportError as e:
    print(f"PragmaticAnalyzer nao disponivel: {e}")
    pragmatic_analyzer_available = False
pragmatic_analyzer = None  # Nova integracao Pragmatic Play

@app.route('/api/pragmatic/status')
def pragmatic_status():
    """Status do PragmaticAnalyzer."""
    try:
        global pragmatic_analyzer
        
        if not pragmatic_analyzer_available:
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
            'reconnect_attempts': status.get('reconnect_attempts', 0)
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'connected': False,
            'monitoring': False,
            'error': str(e)
        }), 500

@app.route('/api/pragmatic/start', methods=['POST'])
def pragmatic_start():
    """Inicia monitoramento Pragmatic Play."""
    try:
        global pragmatic_analyzer
        
        if not pragmatic_analyzer_available:
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
                    'error': 'Credenciais nao configuradas'
                }), 400
            
            pragmatic_analyzer = PragmaticAnalyzer(
                username=username,
                password=password,
                callback=lambda result: print(f"Resultado: {result}")
            )
        
        # Iniciar monitoramento em thread separada
        def start_async():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                success = loop.run_until_complete(pragmatic_analyzer.login_and_get_session())
                if success:
                    pragmatic_analyzer.connect_websocket()
                    pragmatic_analyzer.start_monitoring()
                    print("Monitoramento Pragmatic Play iniciado!")
                else:
                    print("Falha ao iniciar monitoramento Pragmatic Play")
            except Exception as e:
                print(f"Erro na inicializacao assincrona: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=start_async, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Inicializacao Pragmatic Play iniciada'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pragmatic/stop', methods=['POST'])
def pragmatic_stop():
    """Para monitoramento Pragmatic Play."""
    try:
        global pragmatic_analyzer
        
        if pragmatic_analyzer:
            pragmatic_analyzer.stop_monitoring()
            print("Monitoramento Pragmatic Play parado")
        
        return jsonify({
            'success': True,
            'message': 'Monitoramento Pragmatic Play parado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/pragmatic')
def pragmatic_interface():
    """Interface Pragmatic Play."""
    return render_template('pragmatic_websocket.html')
