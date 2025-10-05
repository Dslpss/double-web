"""
Endpoint para receber JSESSIONID via webhook no Railway
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

# Adicionar ao app.py
@app.route('/api/jsessionid/update', methods=['POST'])
def update_jsessionid():
    """
    Endpoint para receber JSESSIONID de sistemas externos
    """
    try:
        # Verificar autorização
        auth_header = request.headers.get('Authorization')
        expected_secret = os.environ.get('JSESSIONID_WEBHOOK_SECRET', 'default_secret')
        
        if not auth_header or auth_header != f'Bearer {expected_secret}':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        jsessionid = data.get('jsessionid')
        
        if not jsessionid:
            return jsonify({'error': 'JSESSIONID required'}), 400
        
        # Salvar JSESSIONID
        from railway_jsessionid_manager import RailwayJSessionManager
        manager = RailwayJSessionManager()
        manager.save_jsessionid_to_cache(jsessionid)
        
        # Atualizar cliente de estatísticas se disponível
        if statistics_enhanced_available:
            from integrators.pragmatic_statistics_enhanced import PragmaticStatisticsClientEnhanced
            # Atualizar instância global se existir
            # Você pode manter uma instância global do cliente
        
        return jsonify({
            'success': True,
            'message': 'JSESSIONID updated successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/jsessionid/status', methods=['GET'])
def jsessionid_status():
    """
    Endpoint para verificar status do JSESSIONID
    """
    try:
        from railway_jsessionid_manager import RailwayJSessionManager
        manager = RailwayJSessionManager()
        
        # Tentar obter JSESSIONID
        jsessionid = manager.get_best_jsessionid()
        
        return jsonify({
            'has_jsessionid': jsessionid is not None,
            'jsessionid_preview': jsessionid[:20] + '...' if jsessionid else None,
            'cache_exists': os.path.exists(manager.storage_file),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500