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
    print("��� Iniciando Blaze Web Backend (Versao Polling)...")
    
    # Inicializar analyzer
    print("��� Inicializando analyzer...")
    analyzer_ready = init_analyzer()
    
    # Inicializar integrador PlayNabets
    if analyzer_ready:
        print("��� Inicializando integrador PlayNabets...")
        playnabets_ready = init_playnabets_integrator(analyzer)
        
        if playnabets_ready:
            # Iniciar conexão PlayNabets automaticamente
            print("��� Iniciando conexão automática com PlayNabets...")
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
