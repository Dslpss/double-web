#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de banco de dados usando localStorage (simulado para backend)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class LocalStorageDB:
    """Banco de dados usando arquivo JSON (simula localStorage)"""
    
    def __init__(self, db_file: str = "blaze_data.json"):
        self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Carrega dados do arquivo JSON"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
                return self._get_default_data()
        return self._get_default_data()
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Retorna estrutura padrão dos dados"""
        return {
            'results': [],
            'patterns': [],
            'predictions': [],
            'analysis': [],
            'settings': {
                'min_confidence': 0.6,
                'max_history': 1000,
                'pattern_types': ['sequence', 'alternation', 'hot_numbers', 'cold_numbers']
            },
            'statistics': {
                'total_results': 0,
                'total_patterns': 0,
                'accuracy': 0.0,
                'last_updated': None
            }
        }
    
    def _save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            self.data['statistics']['last_updated'] = datetime.now().isoformat()
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def add_result(self, result: Dict[str, Any]) -> bool:
        """Adiciona um resultado"""
        try:
            result['id'] = f"result_{int(datetime.now().timestamp() * 1000)}"
            result['timestamp'] = datetime.now().isoformat()
            
            self.data['results'].append(result)
            
            # Manter apenas os últimos N resultados
            max_results = self.data['settings']['max_history']
            if len(self.data['results']) > max_results:
                self.data['results'] = self.data['results'][-max_results:]
            
            self.data['statistics']['total_results'] = len(self.data['results'])
            self._save_data()
            return True
        except Exception as e:
            print(f"Erro ao adicionar resultado: {e}")
            return False
    
    def add_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Adiciona um padrão detectado"""
        try:
            pattern['id'] = f"pattern_{int(datetime.now().timestamp() * 1000)}"
            pattern['timestamp'] = datetime.now().isoformat()
            
            self.data['patterns'].append(pattern)
            
            # Manter apenas os últimos 100 padrões
            if len(self.data['patterns']) > 100:
                self.data['patterns'] = self.data['patterns'][-100:]
            
            self.data['statistics']['total_patterns'] = len(self.data['patterns'])
            self._save_data()
            return True
        except Exception as e:
            print(f"Erro ao adicionar padrão: {e}")
            return False
    
    def add_prediction(self, prediction: Dict[str, Any]) -> bool:
        """Adiciona uma predição"""
        try:
            prediction['id'] = f"pred_{int(datetime.now().timestamp() * 1000)}"
            prediction['timestamp'] = datetime.now().isoformat()
            
            self.data['predictions'].append(prediction)
            
            # Manter apenas as últimas 200 predições
            if len(self.data['predictions']) > 200:
                self.data['predictions'] = self.data['predictions'][-200:]
            
            self._save_data()
            return True
        except Exception as e:
            print(f"Erro ao adicionar predição: {e}")
            return False
    
    def get_recent_results(self, count: int = 20) -> List[Dict[str, Any]]:  # Era 50
        """Retorna resultados recentes"""
        return self.data['results'][-count:] if self.data['results'] else []
    
    def get_recent_patterns(self, count: int = 20) -> List[Dict[str, Any]]:
        """Retorna padrões recentes"""
        return self.data['patterns'][-count:] if self.data['patterns'] else []
    
    def get_recent_predictions(self, count: int = 20) -> List[Dict[str, Any]]:
        """Retorna predições recentes"""
        return self.data['predictions'][-count:] if self.data['predictions'] else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas"""
        return self.data['statistics'].copy()
    
    def get_settings(self) -> Dict[str, Any]:
        """Retorna configurações"""
        return self.data['settings'].copy()
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Atualiza configurações"""
        try:
            self.data['settings'].update(new_settings)
            self._save_data()
            return True
        except Exception as e:
            print(f"Erro ao atualizar configurações: {e}")
            return False
    
    def clear_data(self, data_type: str = 'all') -> bool:
        """Limpa dados"""
        try:
            if data_type == 'all':
                self.data = self._get_default_data()
            elif data_type == 'results':
                self.data['results'] = []
            elif data_type == 'patterns':
                self.data['patterns'] = []
            elif data_type == 'predictions':
                self.data['predictions'] = []
            
            self._save_data()
            return True
        except Exception as e:
            print(f"Erro ao limpar dados: {e}")
            return False
    
    def search_patterns(self, pattern_type: str = None, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Busca padrões por tipo e confiança"""
        patterns = self.data['patterns']
        
        if pattern_type:
            patterns = [p for p in patterns if p.get('pattern_type') == pattern_type]
        
        if min_confidence > 0:
            patterns = [p for p in patterns if p.get('confidence', 0) >= min_confidence]
        
        return patterns
    
    def get_pattern_accuracy(self, pattern_type: str = None) -> float:
        """Calcula precisão dos padrões"""
        patterns = self.search_patterns(pattern_type)
        
        if not patterns:
            return 0.0
        
        correct = sum(1 for p in patterns if p.get('was_correct', False))
        total = len(patterns)
        
        return correct / total if total > 0 else 0.0
    
    def export_data(self, file_path: str = None) -> str:
        """Exporta dados para arquivo"""
        if not file_path:
            file_path = f"blaze_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return file_path
        except Exception as e:
            print(f"Erro ao exportar dados: {e}")
            return None
    
    def import_data(self, file_path: str) -> bool:
        """Importa dados de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Validar estrutura
            if 'results' in imported_data and 'patterns' in imported_data:
                self.data = imported_data
                self._save_data()
                return True
            else:
                print("Arquivo inválido: estrutura de dados incorreta")
                return False
        except Exception as e:
            print(f"Erro ao importar dados: {e}")
            return False

# Instância global
local_db = LocalStorageDB()
