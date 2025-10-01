#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
App Flask simples para teste do Railway
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'OK',
        'message': 'Blaze Web está funcionando!',
        'environment': os.environ.get('FLASK_ENV', 'development')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)