#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integrador de Métricas para o Dashboard de Performance
Conecta o dashboard com o sistema de métricas existente
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class MetricsIntegrator:
    """Integra métricas do sistema com o dashboard"""
    
    def __init__(self, analyzer=None, risk_manager=None, performance_analyzer=None):
        self.analyzer = analyzer
        self.risk_manager = risk_manager
        self.performance_analyzer = performance_analyzer
        
        # Cache de métricas
        self._cached_metrics = {}
        self._last_update = None
        
        logger.info("Metrics Integrator inicializado")
    
    def get_current_metrics(self) -> Dict:
        """Obtém métricas atuais do sistema"""
        try:
            current_time = datetime.now()
            
            # Se já atualizamos recentemente, retornar cache
            if (self._last_update and 
                (current_time - self._last_update).seconds < 5):
                return self._cached_metrics
            
            # Obter métricas do sistema
            metrics = self._collect_metrics()
            
            # Atualizar cache
            self._cached_metrics = metrics
            self._last_update = current_time
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return self._get_default_metrics()
    
    def _collect_metrics(self) -> Dict:
        """Coleta métricas de todas as fontes"""
        metrics = {}
        
        # Métricas básicas do analyzer
        if self.analyzer:
            metrics.update(self._get_analyzer_metrics())
        
        # Métricas de risco
        if self.risk_manager:
            metrics.update(self._get_risk_metrics())
        
        # Métricas de performance
        if self.performance_analyzer:
            metrics.update(self._get_performance_metrics())
        
        # Métricas calculadas
        metrics.update(self._calculate_derived_metrics(metrics))
        
        return metrics
    
    def _get_analyzer_metrics(self) -> Dict:
        """Obtém métricas do analyzer"""
        try:
            if not self.analyzer:
                return {}
            
            # Obter dados históricos
            results = getattr(self.analyzer, 'results', [])
            if not results:
                return {
                    'win_rate': 0.0,
                    'total_trades': 0,
                    'current_capital': 1000.0
                }
            
            # Calcular métricas básicas
            total_trades = len(results)
            wins = sum(1 for r in results if r.get('prediction_correct', False))
            win_rate = wins / total_trades if total_trades > 0 else 0.0
            
            # Calcular capital atual (simulado)
            initial_capital = 1000.0
            current_capital = initial_capital
            
            for result in results:
                if result.get('prediction_correct', False):
                    # Ganho de 10% por acerto
                    current_capital *= 1.1
                else:
                    # Perda de 5% por erro
                    current_capital *= 0.95
            
            return {
                'win_rate': win_rate,
                'total_trades': total_trades,
                'current_capital': current_capital
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas do analyzer: {e}")
            return {}
    
    def _get_risk_metrics(self) -> Dict:
        """Obtém métricas de risco"""
        try:
            if not self.risk_manager:
                return {}
            
            return {
                'drawdown': self.risk_manager.get_max_drawdown(),
                'sharpe_ratio': self.risk_manager.get_sharpe_ratio(),
                'profit_factor': self.risk_manager.get_profit_factor()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de risco: {e}")
            return {}
    
    def _get_performance_metrics(self) -> Dict:
        """Obtém métricas de performance"""
        try:
            if not self.performance_analyzer:
                return {}
            
            # Obter métricas do performance analyzer
            metrics = self.performance_analyzer.calculate_metrics()
            
            return {
                'roi': metrics.get('roi', 0.0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0.0),
                'sortino_ratio': metrics.get('sortino_ratio', 0.0),
                'calmar_ratio': metrics.get('calmar_ratio', 0.0),
                'max_drawdown': metrics.get('max_drawdown', 0.0),
                'profit_factor': metrics.get('profit_factor', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas de performance: {e}")
            return {}
    
    def _calculate_derived_metrics(self, base_metrics: Dict) -> Dict:
        """Calcula métricas derivadas"""
        try:
            derived = {}
            
            # ROI baseado no capital
            current_capital = base_metrics.get('current_capital', 1000.0)
            initial_capital = 1000.0
            roi = ((current_capital - initial_capital) / initial_capital) * 100
            derived['roi'] = roi
            
            # Lucro/Prejuízo
            derived['profit_loss'] = current_capital - initial_capital
            
            # Ganho médio por trade
            total_trades = base_metrics.get('total_trades', 0)
            if total_trades > 0:
                derived['avg_win'] = (current_capital - initial_capital) / total_trades
            else:
                derived['avg_win'] = 0.0
            
            # Status de performance
            if roi > 10:
                derived['performance_status'] = 'Excelente'
            elif roi > 5:
                derived['performance_status'] = 'Bom'
            elif roi > 0:
                derived['performance_status'] = 'Positivo'
            else:
                derived['performance_status'] = 'Negativo'
            
            return derived
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas derivadas: {e}")
            return {}
    
    def _get_default_metrics(self) -> Dict:
        """Retorna métricas padrão quando há erro"""
        return {
            'win_rate': 0.0,
            'roi': 0.0,
            'drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'profit_factor': 0.0,
            'total_trades': 0,
            'current_capital': 1000.0,
            'profit_loss': 0.0,
            'avg_win': 0.0,
            'performance_status': 'Indisponível'
        }
    
    def get_historical_data(self, days: int = 7) -> List[Dict]:
        """Obtém dados históricos para gráficos"""
        try:
            if not self.analyzer:
                return []
            
            results = getattr(self.analyzer, 'results', [])
            if not results:
                return []
            
            # Simular dados históricos baseados nos resultados
            historical = []
            current_capital = 1000.0
            
            for i, result in enumerate(results):
                if result.get('prediction_correct', False):
                    current_capital *= 1.1
                else:
                    current_capital *= 0.95
                
                historical.append({
                    'timestamp': datetime.now(),
                    'capital': current_capital,
                    'win_rate': (i + 1) / len(results) if i > 0 else 0.0,
                    'roi': ((current_capital - 1000.0) / 1000.0) * 100
                })
            
            return historical[-days*24:]  # Últimos N dias
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {e}")
            return []
    
    def get_trade_distribution(self) -> Dict:
        """Obtém distribuição de trades"""
        try:
            if not self.analyzer:
                return {'wins': 0, 'losses': 0, 'total': 0}
            
            results = getattr(self.analyzer, 'results', [])
            if not results:
                return {'wins': 0, 'losses': 0, 'total': 0}
            
            wins = sum(1 for r in results if r.get('prediction_correct', False))
            losses = len(results) - wins
            
            return {
                'wins': wins,
                'losses': losses,
                'total': len(results)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter distribuição de trades: {e}")
            return {'wins': 0, 'losses': 0, 'total': 0}
    
    def get_performance_trend(self) -> str:
        """Obtém tendência de performance"""
        try:
            metrics = self.get_current_metrics()
            roi = metrics.get('roi', 0.0)
            
            if roi > 5:
                return 'Crescendo'
            elif roi > 0:
                return 'Estável'
            else:
                return 'Declinando'
                
        except Exception as e:
            logger.error(f"Erro ao obter tendência: {e}")
            return 'Indisponível'
