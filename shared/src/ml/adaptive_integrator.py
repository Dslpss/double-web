#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador do Sistema de Aprendizado Adaptativo com o BlazeAnalyzerEnhanced.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
import time

from .adaptive_pattern_learner import AdaptivePatternLearner, PatternType
from ..database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class AdaptiveIntegrator:
    """
    Integra o sistema de aprendizado adaptativo com o analisador principal.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o integrador.
        
        Args:
            config: Configurações do integrador
        """
        self.config = config or {}
        
        # Componentes
        self.pattern_learner = AdaptivePatternLearner(self.config.get('learner_config', {}))
        self.db_manager = DatabaseManager("data/blaze_enhanced.db")
        
        # Configurações
        self.auto_learning = self.config.get('auto_learning', True)
        self.learning_interval = self.config.get('learning_interval', 30)  # segundos
        self.min_data_for_learning = self.config.get('min_data_for_learning', 10)  # Era 50
        
        # Estado
        self.is_learning_active = False
        self.learning_thread = None
        self.last_learning_time = None
        
        # Cache
        self.prediction_cache = {}
        self.cache_ttl = timedelta(minutes=2)
        
        logger.info("AdaptiveIntegrator inicializado")
    
    def start_adaptive_learning(self) -> bool:
        """
        Inicia o aprendizado adaptativo em background.
        
        Returns:
            True se iniciou com sucesso
        """
        try:
            if self.is_learning_active:
                logger.warning("Aprendizado adaptativo já está ativo")
                return True
            
            # Carregar padrões existentes
            self._load_existing_patterns()
            
            # Iniciar thread de aprendizado
            self.learning_thread = threading.Thread(
                target=self._learning_loop,
                daemon=True,
                name="AdaptiveLearning"
            )
            self.learning_thread.start()
            
            self.is_learning_active = True
            logger.info("Aprendizado adaptativo iniciado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar aprendizado adaptativo: {e}")
            return False
    
    def stop_adaptive_learning(self) -> bool:
        """
        Para o aprendizado adaptativo.
        
        Returns:
            True se parou com sucesso
        """
        try:
            if not self.is_learning_active:
                logger.warning("Aprendizado adaptativo não está ativo")
                return True
            
            self.is_learning_active = False
            
            if self.learning_thread and self.learning_thread.is_alive():
                self.learning_thread.join(timeout=5)
            
            # Salvar padrões aprendidos
            self._save_learned_patterns()
            
            logger.info("Aprendizado adaptativo parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar aprendizado adaptativo: {e}")
            return False
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """
        Adiciona um resultado para aprendizado.
        
        Args:
            result: Resultado do jogo
        """
        try:
            # Validar resultado
            if not self._validate_result(result):
                return
            
            # Adicionar timestamp se não existir
            if 'timestamp' not in result:
                result['timestamp'] = datetime.now().isoformat()
            
            # Adicionar ao sistema de aprendizado
            self.pattern_learner.add_result(result)
            
            logger.debug(f"Resultado adicionado ao aprendizado: {result.get('roll')} ({result.get('color')})")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar resultado: {e}")
    
    def get_adaptive_prediction(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Obtém uma predição do sistema de aprendizado adaptativo.
        
        Args:
            context: Contexto adicional para a predição
            
        Returns:
            Dict com predição adaptativa
        """
        try:
            # Verificar cache
            cache_key = self._get_cache_key(context)
            if cache_key in self.prediction_cache:
                cached_pred = self.prediction_cache[cache_key]
                if datetime.now() - cached_pred['timestamp'] < self.cache_ttl:
                    return cached_pred['prediction']
            
            # Obter predição do sistema de aprendizado
            prediction = self.pattern_learner.predict_next(context)
            
            # Adicionar informações adicionais
            prediction.update({
                'source': 'adaptive_learning',
                'learning_stats': self.pattern_learner.get_learning_stats(),
                'is_learning_active': self.is_learning_active
            })
            
            # Cache da predição
            self.prediction_cache[cache_key] = {
                'prediction': prediction,
                'timestamp': datetime.now()
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao obter predição adaptativa: {e}")
            return self._get_default_prediction()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Obtém insights do sistema de aprendizado.
        
        Returns:
            Dict com insights do aprendizado
        """
        try:
            stats = self.pattern_learner.get_learning_stats()
            
            # Obter padrões mais confiáveis
            top_patterns = self._get_top_patterns()
            
            # Obter tendências recentes
            recent_trends = self._analyze_recent_trends()
            
            return {
                'learning_stats': stats,
                'top_patterns': top_patterns,
                'recent_trends': recent_trends,
                'learning_status': {
                    'is_active': self.is_learning_active,
                    'last_learning': self.last_learning_time.isoformat() if self.last_learning_time else None,
                    'total_data_points': len(self.pattern_learner.data_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter insights: {e}")
            return {}
    
    def _learning_loop(self) -> None:
        """Loop principal do aprendizado adaptativo."""
        logger.info("Loop de aprendizado adaptativo iniciado")
        
        while self.is_learning_active:
            try:
                # Obter novos dados do banco
                new_data = self._get_new_data_from_db()
                
                if new_data:
                    # Processar novos dados
                    for result in new_data:
                        self.pattern_learner.add_result(result)
                    
                    logger.info(f"Processados {len(new_data)} novos resultados")
                
                # Atualizar timestamp
                self.last_learning_time = datetime.now()
                
                # Aguardar próximo ciclo
                time.sleep(self.learning_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de aprendizado: {e}")
                time.sleep(self.learning_interval)
        
        logger.info("Loop de aprendizado adaptativo finalizado")
    
    def _get_new_data_from_db(self) -> List[Dict[str, Any]]:
        """Obtém novos dados do banco de dados."""
        try:
            # Obter resultados recentes (últimos 10 minutos)
            since_time = datetime.now() - timedelta(minutes=10)
            
            query = """
            SELECT roll, color, timestamp, created_at 
            FROM results 
            WHERE created_at > ? 
            ORDER BY created_at DESC 
            LIMIT 100
            """
            
            results = self.db_manager.execute_query(query, (since_time.isoformat(),))
            
            # Converter para formato esperado
            data = []
            for row in results:
                data.append({
                    'roll': row[0],
                    'color': row[1],
                    'timestamp': row[2] or row[3]
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do banco: {e}")
            return []
    
    def _load_existing_patterns(self) -> None:
        """Carrega padrões existentes do arquivo."""
        try:
            pattern_file = "data/learned_patterns.pkl"
            if self.pattern_learner.load_learned_patterns(pattern_file):
                logger.info("Padrões existentes carregados")
            else:
                logger.info("Nenhum padrão existente encontrado")
                
        except Exception as e:
            logger.error(f"Erro ao carregar padrões existentes: {e}")
    
    def _save_learned_patterns(self) -> None:
        """Salva padrões aprendidos em arquivo."""
        try:
            pattern_file = "data/learned_patterns.pkl"
            if self.pattern_learner.save_learned_patterns(pattern_file):
                logger.info("Padrões aprendidos salvos")
            else:
                logger.error("Erro ao salvar padrões aprendidos")
                
        except Exception as e:
            logger.error(f"Erro ao salvar padrões: {e}")
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Valida se o resultado é válido."""
        required_fields = ['roll', 'color']
        return all(field in result for field in required_fields)
    
    def _get_cache_key(self, context: Dict[str, Any] = None) -> str:
        """Gera chave de cache para predição."""
        if not context:
            return "default"
        
        # Usar dados recentes para gerar chave
        recent_data = list(self.pattern_learner.data_history)[-5:]
        key_data = [f"{r.get('roll')}:{r.get('color')}" for r in recent_data]
        return "_".join(key_data)
    
    def _get_top_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtém os padrões com maior confiança."""
        patterns = list(self.pattern_learner.learned_patterns.values())
        patterns.sort(key=lambda p: p.confidence * p.success_rate, reverse=True)
        
        top_patterns = []
        for pattern in patterns[:limit]:
            top_patterns.append({
                'pattern_id': pattern.pattern_id,
                'pattern_type': pattern.pattern_type.value,
                'confidence': pattern.confidence,
                'success_rate': pattern.success_rate,
                'frequency': pattern.frequency,
                'total_predictions': pattern.total_predictions,
                'last_seen': pattern.last_seen.isoformat()
            })
        
        return top_patterns
    
    def _analyze_recent_trends(self) -> Dict[str, Any]:
        """Analisa tendências recentes."""
        try:
            if len(self.pattern_learner.data_history) < 20:
                return {}
            
            recent_data = list(self.pattern_learner.data_history)[-20:]
            colors = [r.get('color') for r in recent_data]
            
            # Contar cores recentes
            color_counts = {}
            for color in ['red', 'black', 'white']:
                color_counts[color] = colors.count(color)
            
            # Calcular tendências
            total = len(colors)
            trends = {}
            for color, count in color_counts.items():
                trends[color] = {
                    'count': count,
                    'percentage': count / total,
                    'trend': 'increasing' if count > total / 3 else 'stable'
                }
            
            return {
                'recent_colors': colors[-10:],  # Últimas 10 cores
                'color_distribution': trends,
                'analysis_period': 'last_20_results'
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendências: {e}")
            return {}
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Retorna predição padrão em caso de erro."""
        return {
            'predicted_color': 'red',
            'confidence': 0.33,
            'pattern_id': 'default',
            'patterns_used': [],
            'reasoning': 'Erro no sistema de aprendizado',
            'source': 'adaptive_learning',
            'timestamp': datetime.now().isoformat()
        }
