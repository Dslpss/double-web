#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Métricas de Performance Avançadas para Blaze Double
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance completas"""
    # Métricas básicas
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Métricas financeiras
    total_profit: float
    total_loss: float
    net_profit: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    roi: float
    
    # Métricas de risco
    max_drawdown: float
    max_drawdown_duration: int
    current_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Métricas de consistência
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    
    # Métricas de timing
    avg_trade_duration: float
    best_month: str
    worst_month: str
    monthly_returns: Dict[str, float]
    
    # Métricas de precisão
    accuracy_by_color: Dict[str, float]
    accuracy_by_confidence: Dict[str, float]
    false_positive_rate: float
    false_negative_rate: float

class PerformanceAnalyzer:
    """Analisador de performance avançado"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.trades = []
        self.daily_returns = []
        self.monthly_returns = {}
        
        logger.info("Performance Analyzer inicializado")
    
    def add_trade(self, 
                  timestamp: datetime,
                  predicted_color: str,
                  actual_color: str,
                  bet_amount: float,
                  profit: float,
                  confidence: float,
                  is_win: bool):
        """Adiciona um trade para análise"""
        trade = {
            'timestamp': timestamp,
            'predicted_color': predicted_color,
            'actual_color': actual_color,
            'bet_amount': bet_amount,
            'profit': profit,
            'confidence': confidence,
            'is_win': is_win
        }
        self.trades.append(trade)
        
        # Adicionar retorno diário
        self._add_daily_return(timestamp, profit)
    
    def _add_daily_return(self, timestamp: datetime, profit: float):
        """Adiciona retorno diário"""
        date = timestamp.date()
        
        if not self.daily_returns or self.daily_returns[-1]['date'] != date:
            self.daily_returns.append({
                'date': date,
                'return': profit
            })
        else:
            self.daily_returns[-1]['return'] += profit
    
    def calculate_metrics(self, initial_capital: float = 1000.0) -> PerformanceMetrics:
        """Calcula todas as métricas de performance"""
        if not self.trades:
            return self._empty_metrics()
        
        # Converter para DataFrame para facilitar cálculos
        df = pd.DataFrame(self.trades)
        
        # Métricas básicas
        total_trades = len(df)
        winning_trades = df['is_win'].sum()
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Métricas financeiras
        total_profit = df[df['is_win']]['profit'].sum()
        total_loss = abs(df[~df['is_win']]['profit'].sum())
        net_profit = df['profit'].sum()
        gross_profit = total_profit
        gross_loss = total_loss
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        roi = (net_profit / initial_capital) * 100 if initial_capital > 0 else 0
        
        # Métricas de risco
        max_drawdown, max_drawdown_duration = self._calculate_max_drawdown(initial_capital)
        current_drawdown = self._calculate_current_drawdown(initial_capital)
        sharpe_ratio = self._calculate_sharpe_ratio()
        sortino_ratio = self._calculate_sortino_ratio()
        calmar_ratio = self._calculate_calmar_ratio(roi, max_drawdown)
        
        # Métricas de consistência
        winning_trades_df = df[df['is_win']]
        losing_trades_df = df[~df['is_win']]
        
        avg_win = winning_trades_df['profit'].mean() if len(winning_trades_df) > 0 else 0
        avg_loss = losing_trades_df['profit'].mean() if len(losing_trades_df) > 0 else 0
        largest_win = winning_trades_df['profit'].max() if len(winning_trades_df) > 0 else 0
        largest_loss = losing_trades_df['profit'].min() if len(losing_trades_df) > 0 else 0
        
        consecutive_wins, consecutive_losses = self._calculate_consecutive_sequences()
        
        # Métricas de timing
        avg_trade_duration = self._calculate_avg_trade_duration()
        monthly_returns = self._calculate_monthly_returns(initial_capital)
        best_month, worst_month = self._get_best_worst_months(monthly_returns)
        
        # Métricas de precisão
        accuracy_by_color = self._calculate_accuracy_by_color()
        accuracy_by_confidence = self._calculate_accuracy_by_confidence()
        false_positive_rate, false_negative_rate = self._calculate_false_rates()
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_profit=total_profit,
            total_loss=total_loss,
            net_profit=net_profit,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            roi=roi,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            current_drawdown=current_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            avg_trade_duration=avg_trade_duration,
            best_month=best_month,
            worst_month=worst_month,
            monthly_returns=monthly_returns,
            accuracy_by_color=accuracy_by_color,
            accuracy_by_confidence=accuracy_by_confidence,
            false_positive_rate=false_positive_rate,
            false_negative_rate=false_negative_rate
        )
    
    def _calculate_max_drawdown(self, initial_capital: float) -> Tuple[float, int]:
        """Calcula drawdown máximo e duração"""
        if not self.daily_returns:
            return 0.0, 0
        
        # Calcular capital acumulado
        capital = initial_capital
        peak_capital = initial_capital
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_duration = 0
        
        for daily_return in self.daily_returns:
            capital += daily_return['return']
            
            if capital > peak_capital:
                peak_capital = capital
                current_dd_duration = 0
            else:
                current_dd_duration += 1
                drawdown = (peak_capital - capital) / peak_capital
                max_dd = max(max_dd, drawdown)
                max_dd_duration = max(max_dd_duration, current_dd_duration)
        
        return max_dd, max_dd_duration
    
    def _calculate_current_drawdown(self, initial_capital: float) -> float:
        """Calcula drawdown atual"""
        if not self.daily_returns:
            return 0.0
        
        # Calcular capital atual
        current_capital = initial_capital + sum(dr['return'] for dr in self.daily_returns)
        
        # Calcular pico
        capital = initial_capital
        peak_capital = initial_capital
        
        for daily_return in self.daily_returns:
            capital += daily_return['return']
            peak_capital = max(peak_capital, capital)
        
        if peak_capital == 0:
            return 0.0
        
        return (peak_capital - current_capital) / peak_capital
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calcula Sharpe ratio"""
        if not self.daily_returns:
            return 0.0
        
        returns = [dr['return'] for dr in self.daily_returns]
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_return
    
    def _calculate_sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calcula Sortino ratio (foca apenas em downside risk)"""
        if not self.daily_returns:
            return 0.0
        
        returns = [dr['return'] for dr in self.daily_returns]
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        downside_returns = [r for r in returns if r < risk_free_rate]
        
        if not downside_returns:
            return float('inf')
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / downside_std
    
    def _calculate_calmar_ratio(self, roi: float, max_drawdown: float) -> float:
        """Calcula Calmar ratio (ROI / Max Drawdown)"""
        if max_drawdown == 0:
            return float('inf')
        
        return roi / (max_drawdown * 100)
    
    def _calculate_consecutive_sequences(self) -> Tuple[int, int]:
        """Calcula sequências consecutivas de vitórias e derrotas"""
        if not self.trades:
            return 0, 0
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in self.trades:
            if trade['is_win']:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return max_wins, max_losses
    
    def _calculate_avg_trade_duration(self) -> float:
        """Calcula duração média entre trades (em horas)"""
        if len(self.trades) < 2:
            return 0.0
        
        durations = []
        for i in range(1, len(self.trades)):
            duration = (self.trades[i]['timestamp'] - self.trades[i-1]['timestamp']).total_seconds() / 3600
            durations.append(duration)
        
        return np.mean(durations) if durations else 0.0
    
    def _calculate_monthly_returns(self, initial_capital: float) -> Dict[str, float]:
        """Calcula retornos mensais"""
        monthly_returns = {}
        
        if not self.daily_returns:
            return monthly_returns
        
        # Agrupar por mês
        monthly_data = {}
        for dr in self.daily_returns:
            month_key = dr['date'].strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += dr['return']
        
        # Calcular retornos percentuais
        for month, total_return in monthly_data.items():
            monthly_returns[month] = (total_return / initial_capital) * 100
        
        return monthly_returns
    
    def _get_best_worst_months(self, monthly_returns: Dict[str, float]) -> Tuple[str, str]:
        """Retorna melhor e pior mês"""
        if not monthly_returns:
            return "", ""
        
        best_month = max(monthly_returns.items(), key=lambda x: x[1])[0]
        worst_month = min(monthly_returns.items(), key=lambda x: x[1])[0]
        
        return best_month, worst_month
    
    def _calculate_accuracy_by_color(self) -> Dict[str, float]:
        """Calcula precisão por cor predita"""
        if not self.trades:
            return {}
        
        color_stats = {}
        
        for trade in self.trades:
            predicted = trade['predicted_color']
            if predicted not in color_stats:
                color_stats[predicted] = {'total': 0, 'correct': 0}
            
            color_stats[predicted]['total'] += 1
            if trade['is_win']:
                color_stats[predicted]['correct'] += 1
        
        accuracy = {}
        for color, stats in color_stats.items():
            accuracy[color] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        return accuracy
    
    def _calculate_accuracy_by_confidence(self) -> Dict[str, float]:
        """Calcula precisão por faixa de confiança"""
        if not self.trades:
            return {}
        
        confidence_ranges = {
            '0.0-0.5': (0.0, 0.5),
            '0.5-0.7': (0.5, 0.7),
            '0.7-0.8': (0.7, 0.8),
            '0.8-0.9': (0.8, 0.9),
            '0.9-1.0': (0.9, 1.0)
        }
        
        range_stats = {}
        
        for trade in self.trades:
            confidence = trade['confidence']
            
            for range_name, (min_conf, max_conf) in confidence_ranges.items():
                if min_conf <= confidence < max_conf:
                    if range_name not in range_stats:
                        range_stats[range_name] = {'total': 0, 'correct': 0}
                    
                    range_stats[range_name]['total'] += 1
                    if trade['is_win']:
                        range_stats[range_name]['correct'] += 1
                    break
        
        accuracy = {}
        for range_name, stats in range_stats.items():
            accuracy[range_name] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        return accuracy
    
    def _calculate_false_rates(self) -> Tuple[float, float]:
        """Calcula taxas de falso positivo e falso negativo"""
        if not self.trades:
            return 0.0, 0.0
        
        false_positives = 0  # Predisse cor, mas errou
        false_negatives = 0  # Não predisse cor, mas deveria ter acertado
        total_predictions = len(self.trades)
        
        for trade in self.trades:
            if not trade['is_win']:
                false_positives += 1
        
        false_positive_rate = false_positives / total_predictions if total_predictions > 0 else 0
        false_negative_rate = 0.0  # Não aplicável neste contexto
        
        return false_positive_rate, false_negative_rate
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Retorna métricas vazias"""
        return PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_profit=0.0,
            total_loss=0.0,
            net_profit=0.0,
            gross_profit=0.0,
            gross_loss=0.0,
            profit_factor=0.0,
            roi=0.0,
            max_drawdown=0.0,
            max_drawdown_duration=0,
            current_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            consecutive_wins=0,
            consecutive_losses=0,
            avg_trade_duration=0.0,
            best_month="",
            worst_month="",
            monthly_returns={},
            accuracy_by_color={},
            accuracy_by_confidence={},
            false_positive_rate=0.0,
            false_negative_rate=0.0
        )
    
    def generate_performance_report(self, initial_capital: float = 1000.0) -> str:
        """Gera relatório detalhado de performance"""
        metrics = self.calculate_metrics(initial_capital)
        
        report = f"""
=== RELATÓRIO DE PERFORMANCE AVANÇADA ===

=== MÉTRICAS BÁSICAS ===
Total de Trades: {metrics.total_trades}
Trades Vencedores: {metrics.winning_trades}
Trades Perdedores: {metrics.losing_trades}
Taxa de Acerto: {metrics.win_rate:.2%}

=== MÉTRICAS FINANCEIRAS ===
Lucro Total: R$ {metrics.total_profit:.2f}
Perda Total: R$ {metrics.total_loss:.2f}
Lucro Líquido: R$ {metrics.net_profit:.2f}
ROI: {metrics.roi:.2f}%
Profit Factor: {metrics.profit_factor:.2f}

=== MÉTRICAS DE RISCO ===
Drawdown Máximo: {metrics.max_drawdown:.2%}
Duração do Drawdown: {metrics.max_drawdown_duration} dias
Drawdown Atual: {metrics.current_drawdown:.2%}
Sharpe Ratio: {metrics.sharpe_ratio:.2f}
Sortino Ratio: {metrics.sortino_ratio:.2f}
Calmar Ratio: {metrics.calmar_ratio:.2f}

=== MÉTRICAS DE CONSISTÊNCIA ===
Maior Ganho: R$ {metrics.largest_win:.2f}
Maior Perda: R$ {metrics.largest_loss:.2f}
Ganho Médio: R$ {metrics.avg_win:.2f}
Perda Média: R$ {metrics.avg_loss:.2f}
Maior Sequência de Vitórias: {metrics.consecutive_wins}
Maior Sequência de Derrotas: {metrics.consecutive_losses}

=== MÉTRICAS DE TIMING ===
Duração Média entre Trades: {metrics.avg_trade_duration:.1f} horas
Melhor Mês: {metrics.best_month}
Pior Mês: {metrics.worst_month}

=== MÉTRICAS DE PRECISÃO ===
Precisão por Cor:
{chr(10).join([f"  {color}: {acc:.2%}" for color, acc in metrics.accuracy_by_color.items()])}

Precisão por Confiança:
{chr(10).join([f"  {conf_range}: {acc:.2%}" for conf_range, acc in metrics.accuracy_by_confidence.items()])}

Taxa de Falso Positivo: {metrics.false_positive_rate:.2%}
        """
        
        return report
    
    def export_metrics(self, filename: str = None) -> str:
        """Exporta métricas para arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_metrics_{timestamp}.json"
        
        metrics = self.calculate_metrics()
        
        # Converter para formato serializável
        metrics_dict = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'total_profit': metrics.total_profit,
            'total_loss': metrics.total_loss,
            'net_profit': metrics.net_profit,
            'gross_profit': metrics.gross_profit,
            'gross_loss': metrics.gross_loss,
            'profit_factor': metrics.profit_factor,
            'roi': metrics.roi,
            'max_drawdown': metrics.max_drawdown,
            'max_drawdown_duration': metrics.max_drawdown_duration,
            'current_drawdown': metrics.current_drawdown,
            'sharpe_ratio': metrics.sharpe_ratio,
            'sortino_ratio': metrics.sortino_ratio,
            'calmar_ratio': metrics.calmar_ratio,
            'avg_win': metrics.avg_win,
            'avg_loss': metrics.avg_loss,
            'largest_win': metrics.largest_win,
            'largest_loss': metrics.largest_loss,
            'consecutive_wins': metrics.consecutive_wins,
            'consecutive_losses': metrics.consecutive_losses,
            'avg_trade_duration': metrics.avg_trade_duration,
            'best_month': metrics.best_month,
            'worst_month': metrics.worst_month,
            'monthly_returns': metrics.monthly_returns,
            'accuracy_by_color': metrics.accuracy_by_color,
            'accuracy_by_confidence': metrics.accuracy_by_confidence,
            'false_positive_rate': metrics.false_positive_rate,
            'false_negative_rate': metrics.false_negative_rate
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metrics_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Métricas exportadas para: {filename}")
        return filename

