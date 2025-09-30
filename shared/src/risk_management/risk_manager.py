#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Gestão de Risco e Money Management para Blaze Double
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class RiskMetrics:
    """Métricas de risco"""
    current_drawdown: float
    max_drawdown: float
    consecutive_losses: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    risk_level: RiskLevel
    recommended_bet_size: float
    max_bet_size: float
    stop_loss_triggered: bool
    take_profit_triggered: bool

class RiskManager:
    """Gerenciador de risco e money management"""
    
    def __init__(self, 
                 initial_capital: float = 1000.0,
                 max_risk_per_trade: float = 0.02,  # 2% por trade
                 max_daily_risk: float = 0.10,      # 10% por dia
                 max_drawdown: float = 0.20,        # 20% drawdown máximo
                 stop_loss_consecutive: int = 5,    # Stop após 5 perdas consecutivas
                 take_profit_multiplier: float = 2.0):  # Take profit em 2x o capital inicial
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_daily_risk = max_daily_risk
        self.max_drawdown = max_drawdown
        self.stop_loss_consecutive = stop_loss_consecutive
        self.take_profit_multiplier = take_profit_multiplier
        
        # Estado atual
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.peak_capital = initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown_achieved = 0.0
        
        # Histórico de trades
        self.trade_history = []
        self.daily_history = []
        
        # Controle de sessão
        self.session_start = datetime.now()
        self.last_reset_date = datetime.now().date()
        
        logger.info(f"Risk Manager inicializado - Capital: R$ {initial_capital:.2f}")
    
    def calculate_bet_size(self, 
                          confidence: float, 
                          base_bet: float = None,
                          strategy_risk: float = 1.0) -> float:
        """
        Calcula o tamanho da aposta baseado no risco
        
        Args:
            confidence: Confiança da predição (0-1)
            base_bet: Aposta base (opcional)
            strategy_risk: Multiplicador de risco da estratégia
            
        Returns:
            float: Tamanho da aposta recomendado
        """
        # Verificar se pode apostar
        if not self.can_place_bet():
            return 0.0
        
        # Calcular risco baseado na confiança
        confidence_risk = min(confidence, 0.95)  # Máximo 95% de confiança
        risk_multiplier = confidence_risk * strategy_risk
        
        # Calcular tamanho da aposta
        if base_bet:
            bet_size = base_bet * risk_multiplier
        else:
            # Usar Kelly Criterion simplificado
            current_win_rate = self.get_win_rate()
            if current_win_rate > 0:
                kelly_fraction = (current_win_rate * 2 - 1) * confidence_risk
                kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Limitar a 25%
                bet_size = self.current_capital * kelly_fraction
            else:
                bet_size = self.current_capital * self.max_risk_per_trade * risk_multiplier
        
        # Aplicar limites de risco
        max_bet_per_trade = self.current_capital * self.max_risk_per_trade
        max_bet_daily = self.current_capital * self.max_daily_risk
        
        bet_size = min(bet_size, max_bet_per_trade, max_bet_daily)
        
        # Aplicar redução por drawdown
        if self.current_drawdown > 0.05:  # Se drawdown > 5%
            reduction_factor = 1 - (self.current_drawdown * 2)  # Reduzir até 50%
            bet_size *= max(0.1, reduction_factor)
        
        # Aplicar redução por perdas consecutivas
        if self.consecutive_losses > 0:
            loss_reduction = 1 - (self.consecutive_losses * 0.1)  # Reduzir 10% por perda
            bet_size *= max(0.1, loss_reduction)
        
        return max(0, bet_size)
    
    def can_place_bet(self) -> bool:
        """Verifica se pode fazer uma aposta"""
        # Verificar stop loss por drawdown
        if self.current_drawdown >= self.max_drawdown:
            logger.warning("Stop loss por drawdown atingido")
            return False
        
        # Verificar stop loss por perdas consecutivas
        if self.consecutive_losses >= self.stop_loss_consecutive:
            logger.warning("Stop loss por perdas consecutivas atingido")
            return False
        
        # Verificar take profit
        if self.current_capital >= self.initial_capital * self.take_profit_multiplier:
            logger.info("Take profit atingido")
            return False
        
        # Verificar risco diário
        if abs(self.daily_pnl) >= self.current_capital * self.max_daily_risk:
            logger.warning("Limite de risco diário atingido")
            return False
        
        return True
    
    def record_trade(self, 
                    bet_amount: float, 
                    profit: float, 
                    is_win: bool,
                    confidence: float = 0.5) -> RiskMetrics:
        """
        Registra um trade e atualiza métricas de risco
        
        Args:
            bet_amount: Valor apostado
            profit: Lucro/prejuízo do trade
            is_win: Se o trade foi vencedor
            confidence: Confiança da predição
            
        Returns:
            RiskMetrics: Métricas atualizadas de risco
        """
        # Atualizar capital
        self.current_capital += profit
        self.daily_pnl += profit
        self.total_trades += 1
        
        # Atualizar sequências
        if is_win:
            self.winning_trades += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Atualizar peak e drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
            self.current_drawdown = 0.0
        else:
            self.current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
            self.max_drawdown_achieved = max(self.max_drawdown_achieved, self.current_drawdown)
        
        # Registrar trade
        trade = {
            'timestamp': datetime.now(),
            'bet_amount': bet_amount,
            'profit': profit,
            'is_win': is_win,
            'confidence': confidence,
            'capital_after': self.current_capital,
            'drawdown': self.current_drawdown
        }
        self.trade_history.append(trade)
        
        # Calcular métricas
        metrics = self.get_risk_metrics()
        
        logger.info(f"Trade registrado: {'WIN' if is_win else 'LOSS'} - "
                   f"Lucro: R$ {profit:.2f} - Capital: R$ {self.current_capital:.2f} - "
                   f"Drawdown: {self.current_drawdown:.2%}")
        
        return metrics
    
    def get_risk_metrics(self) -> RiskMetrics:
        """Calcula métricas atuais de risco"""
        win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        
        # Calcular profit factor
        total_profit = sum(t['profit'] for t in self.trade_history if t['is_win'])
        total_loss = abs(sum(t['profit'] for t in self.trade_history if not t['is_win']))
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        # Calcular Sharpe ratio (simplificado)
        if len(self.trade_history) > 1:
            returns = [t['profit'] / self.initial_capital for t in self.trade_history]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Determinar nível de risco
        risk_level = self._determine_risk_level()
        
        # Calcular tamanho de aposta recomendado
        recommended_bet = self.calculate_bet_size(0.7)  # Confiança média
        max_bet = self.current_capital * self.max_risk_per_trade
        
        # Verificar triggers
        stop_loss_triggered = (self.current_drawdown >= self.max_drawdown or 
                              self.consecutive_losses >= self.stop_loss_consecutive)
        take_profit_triggered = (self.current_capital >= 
                               self.initial_capital * self.take_profit_multiplier)
        
        return RiskMetrics(
            current_drawdown=self.current_drawdown,
            max_drawdown=self.max_drawdown_achieved,
            consecutive_losses=self.consecutive_losses,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            risk_level=risk_level,
            recommended_bet_size=recommended_bet,
            max_bet_size=max_bet,
            stop_loss_triggered=stop_loss_triggered,
            take_profit_triggered=take_profit_triggered
        )
    
    def _determine_risk_level(self) -> RiskLevel:
        """Determina o nível de risco atual"""
        win_rate = self.get_win_rate()
        
        if (self.current_drawdown >= 0.15 or 
            self.consecutive_losses >= 4 or 
            win_rate < 0.3):
            return RiskLevel.EXTREME
        elif (self.current_drawdown >= 0.10 or 
              self.consecutive_losses >= 3 or 
              win_rate < 0.4):
            return RiskLevel.HIGH
        elif (self.current_drawdown >= 0.05 or 
              self.consecutive_losses >= 2 or 
              win_rate < 0.5):
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_win_rate(self) -> float:
        """Retorna taxa de acerto atual"""
        return self.winning_trades / self.total_trades if self.total_trades > 0 else 0
    
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        logger.info("Métricas diárias resetadas")
    
    def reset_session(self):
        """Reseta sessão de trading"""
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.current_drawdown = 0.0
        self.peak_capital = self.current_capital
        self.session_start = datetime.now()
        logger.info("Sessão de trading resetada")
    
    def get_daily_summary(self) -> Dict:
        """Retorna resumo do dia"""
        today_trades = [t for t in self.trade_history 
                       if t['timestamp'].date() == datetime.now().date()]
        
        return {
            'date': datetime.now().date().isoformat(),
            'trades_count': len(today_trades),
            'daily_pnl': self.daily_pnl,
            'winning_trades': sum(1 for t in today_trades if t['is_win']),
            'losing_trades': sum(1 for t in today_trades if not t['is_win']),
            'win_rate': (sum(1 for t in today_trades if t['is_win']) / len(today_trades) 
                        if today_trades else 0),
            'current_capital': self.current_capital,
            'drawdown': self.current_drawdown
        }
    
    def export_risk_report(self, filename: str = None) -> str:
        """Exporta relatório de risco"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"risk_report_{timestamp}.json"
        
        metrics = self.get_risk_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.total_trades - self.winning_trades,
            'win_rate': metrics.win_rate,
            'current_drawdown': metrics.current_drawdown,
            'max_drawdown': metrics.max_drawdown,
            'consecutive_losses': metrics.consecutive_losses,
            'profit_factor': metrics.profit_factor,
            'sharpe_ratio': metrics.sharpe_ratio,
            'risk_level': metrics.risk_level.value,
            'recommended_bet_size': metrics.recommended_bet_size,
            'max_bet_size': metrics.max_bet_size,
            'stop_loss_triggered': metrics.stop_loss_triggered,
            'take_profit_triggered': metrics.take_profit_triggered,
            'daily_summary': self.get_daily_summary(),
            'trade_history': self.trade_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Relatório de risco exportado para: {filename}")
        return filename
