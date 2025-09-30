#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Autenticação para Blaze Web
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session

# Simulação de banco de usuários (em produção usar banco real)
# IMPORTANTE: Altere essas senhas padrão em produção!
USERS_DB = {
    'admin': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),  # ALTERE EM PRODUÇÃO!
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    },
    'user': {
        'password': hashlib.sha256('user123'.encode()).hexdigest(),  # ALTERE EM PRODUÇÃO!
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
}

# Sessões ativas
ACTIVE_SESSIONS = {}

def hash_password(password):
    """Hash da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verifica senha."""
    return hash_password(password) == hashed

def generate_token():
    """Gera token de sessão."""
    return secrets.token_urlsafe(32)

def create_session(username):
    """Cria nova sessão."""
    token = generate_token()
    session_data = {
        'username': username,
        'role': USERS_DB[username]['role'],
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
    }
    ACTIVE_SESSIONS[token] = session_data
    return token

def validate_token(token):
    """Valida token de sessão."""
    if token not in ACTIVE_SESSIONS:
        return None
    
    session_data = ACTIVE_SESSIONS[token]
    expires_at = datetime.fromisoformat(session_data['expires_at'])
    
    if datetime.now() > expires_at:
        del ACTIVE_SESSIONS[token]
        return None
    
    return session_data

def require_auth(f):
    """Decorator para rotas que requerem autenticação."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        session_data = validate_token(token)
        if not session_data:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        request.user = session_data
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator para rotas que requerem admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token de autorização necessário'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        session_data = validate_token(token)
        if not session_data:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        if session_data['role'] != 'admin':
            return jsonify({'error': 'Acesso negado - requer privilégios de admin'}), 403
        
        request.user = session_data
        return f(*args, **kwargs)
    
    return decorated_function

def login(username, password):
    """Realiza login."""
    if username not in USERS_DB:
        return {'success': False, 'error': 'Usuário não encontrado'}
    
    if not verify_password(password, USERS_DB[username]['password']):
        return {'success': False, 'error': 'Senha incorreta'}
    
    token = create_session(username)
    return {
        'success': True,
        'token': token,
        'user': {
            'username': username,
            'role': USERS_DB[username]['role']
        }
    }

def logout(token):
    """Realiza logout."""
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
        return {'success': True}
    return {'success': False, 'error': 'Token não encontrado'}

def register(username, password, role='user'):
    """Registra novo usuário."""
    if username in USERS_DB:
        return {'success': False, 'error': 'Usuário já existe'}
    
    if len(password) < 6:
        return {'success': False, 'error': 'Senha deve ter pelo menos 6 caracteres'}
    
    USERS_DB[username] = {
        'password': hash_password(password),
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    
    return {'success': True, 'message': 'Usuário registrado com sucesso'}

def get_user_info(token):
    """Obtém informações do usuário."""
    session_data = validate_token(token)
    if not session_data:
        return None
    
    return {
        'username': session_data['username'],
        'role': session_data['role'],
        'created_at': session_data['created_at']
    }
