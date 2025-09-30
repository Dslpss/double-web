#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Backtesting para validação de estratégias do Blaze Double
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Resultado de um backtest"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    net_profit: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    roi: float
    trades: List[Dict]

class BacktestEngine:
    """Engine principal para backtesting de estratégias"""
    
    def __init__(self, initial_capital: float = 1000.0):
        """
        Inicializa o engine de backtesting
        
        Args:
            initial_capital (float): Capital inicial para backtesting
        """
        self.initial_capital = initial_capital
        self.results = []
        
        logger.info(f"Backtest Engine inicializado com capital inicial: R$ {initial_capital}")
    
    def run_backtest(self, 
                    strategy, 
                    data: List[Dict], 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    bet_amount: float = 1.0,
                    max_bets: int = 1000) -> BacktestResult:
        """
        Executa backtest de uma estratégia
        
        Args:
            strategy: Estratégia a ser testada
            data: Dados históricos
            start_date: Data de início (opcional)
            end_date: Data de fim (opcional)
            bet_amount: Valor da aposta
            max_bets: Número máximo de apostas
            
        Returns:
            BacktestResult: Resultado do backtest
        """
        logger.info(f"Iniciando backtest da estratégia: {strategy.name}")
        
        # Filtrar dados por período se especificado
        if start_date or end_date:
            data = self._filter_data_by_date(data, start_date, end_date)
        
        # Executar simulação
        trades = []
        capital = self.initial_capital
        peak_capital = self.initial_capital
        max_drawdown = 0.0
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        # Estatísticas
        total_profit = 0.0
        total_loss = 0.0
        winning_trades = 0
        losing_trades = 0
        largest_win = 0.0
        largest_loss = 0.0
        
        # Lista para Sharpe ratio
        returns = []
        
        for i in range(len(data) - 1):
            if len(trades) >= max_bets:
                break
                
            # Obter dados históricos até o ponto atual
            historical_data = data[:i+1]
            current_result = data[i]
            next_result = data[i+1]
            
            # Obter sinal da estratégia
            signal = strategy.get_signal(historical_data, current_result)
            
            if signal and signal.get('action') == 'bet':
                # Calcular valor da aposta
                bet_value = min(bet_amount, capital * 0.1)  # Máximo 10% do capital
                
                if bet_value <= 0:
                    continue
                
                # Fazer aposta
                predicted_color = signal.get('predicted_color')
                actual_color = self._get_color(next_result.get('roll', 0))
                confidence = signal.get('confidence', 0.5)
                
                # Calcular resultado da aposta
                is_win = predicted_color == actual_color
                payout = bet_value * 2 if is_win else 0  # Payout 2x para acerto
                profit = payout - bet_value
                
                # Atualizar capital
                capital += profit
                
                # Atualizar estatísticas
                if is_win:
                    winning_trades += 1
                    total_profit += profit
                    consecutive_wins += 1
                    consecutive_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                    largest_win = max(largest_win, profit)
                else:
                    losing_trades += 1
                    total_loss += abs(profit)
                    consecutive_losses += 1
                    consecutive_wins = 0
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                    largest_loss = max(largest_loss, abs(profit))
                
                # Calcular drawdown
                if capital > peak_capital:
                    peak_capital = capital
                
                current_drawdown = (peak_capital - capital) / peak_capital
                max_drawdown = max(max_drawdown, current_drawdown)
                
                # Adicionar retorno para Sharpe ratio
                returns.append(profit / self.initial_capital)
                
                # Registrar trade
                trade = {
                    'timestamp': current_result.get('timestamp', i),
                    'predicted_color': predicted_color,
                    'actual_color': actual_color,
                    'bet_amount': bet_value,
                    'profit': profit,
                    'capital_after': capital,
                    'confidence': confidence,
                    'is_win': is_win
                }
                trades.append(trade)
        
        # Calcular métricas finais
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades) if total_trades > 0 else 0
        net_profit = capital - self.initial_capital
        roi = (net_profit / self.initial_capital) * 100
        
        # Calcular Sharpe ratio
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        
        # Calcular profit factor
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        # Calcular médias
        avg_win = (total_profit / winning_trades) if winning_trades > 0 else 0
        avg_loss = (total_loss / losing_trades) if losing_trades > 0 else 0
        
        # Criar resultado
        result = BacktestResult(
            strategy_name=strategy.name,
            start_date=start_date or datetime.fromtimestamp(data[0].get('timestamp', 0)),
            end_date=end_date or datetime.fromtimestamp(data[-1].get('timestamp', 0)),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_profit=total_profit,
            total_loss=total_loss,
            net_profit=net_profit,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=max_consecutive_wins,
            consecutive_losses=max_consecutive_losses,
            roi=roi,
            trades=trades
        )
        
        self.results.append(result)
        logger.info(f"Backtest concluído: {total_trades} trades, ROI: {roi:.2f}%, Win Rate: {win_rate:.2f}%")
        
        return result
    
    def _filter_data_by_date(self, data: List[Dict], start_date: Optional[datetime], end_date: Optional[datetime]) -> List[Dict]:
        """Filtra dados por período"""
        filtered = data
        
        if start_date:
            filtered = [d for d in filtered if datetime.fromtimestamp(d.get('timestamp', 0)) >= start_date]
        
        if end_date:
            filtered = [d for d in filtered if datetime.fromtimestamp(d.get('timestamp', 0)) <= end_date]
        
        return filtered
    
    def _get_color(self, roll: int) -> str:
        """Determina a cor baseada no número"""
        if roll == 0:
            return 'white'
        elif 1 <= roll <= 7:
            return 'red'
        else:
            return 'black'
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calcula o Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Assumindo risk-free rate de 0
        return mean_return / std_return
    
    def compare_strategies(self, strategies: List, data: List[Dict], **kwargs) -> Dict[str, BacktestResult]:
        """Compara múltiplas estratégias"""
        logger.info(f"Comparando {len(strategies)} estratégias")
        
        results = {}
        for strategy in strategies:
            result = self.run_backtest(strategy, data, **kwargs)
            results[strategy.name] = result
        
        return results
    
    def generate_report(self, result: BacktestResult) -> str:
        """Gera relatório detalhado do backtest"""
        report = f"""
=== RELATÓRIO DE BACKTEST ===
Estratégia: {result.strategy_name}
Período: {result.start_date.strftime('%d/%m/%Y')} - {result.end_date.strftime('%d/%m/%Y')}

=== PERFORMANCE GERAL ===
Total de Trades: {result.total_trades}
Trades Vencedores: {result.winning_trades}
Trades Perdedores: {result.losing_trades}
Taxa de Acerto: {result.win_rate:.2%}

=== FINANCEIRO ===
Capital Inicial: R$ {self.initial_capital:.2f}
Capital Final: R$ {self.initial_capital + result.net_profit:.2f}
Lucro Líquido: R$ {result.net_profit:.2f}
ROI: {result.roi:.2f}%

=== RISCO ===
Drawdown Máximo: {result.max_drawdown:.2%}
Sharpe Ratio: {result.sharpe_ratio:.2f}
Profit Factor: {result.profit_factor:.2f}

=== ESTATÍSTICAS DE TRADES ===
Maior Ganho: R$ {result.largest_win:.2f}
Maior Perda: R$ {result.largest_loss:.2f}
Ganho Médio: R$ {result.avg_win:.2f}
Perda Média: R$ {result.avg_loss:.2f}

=== SEQUÊNCIAS ===
Maior Sequência de Vitórias: {result.consecutive_wins}
Maior Sequência de Derrotas: {result.consecutive_losses}
        """
        
        return report
    
    def export_results(self, filename: str = None) -> str:
        """Exporta resultados para arquivo"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_results_{timestamp}.json"
        
        # Converter resultados para formato serializável
        export_data = []
        for result in self.results:
            result_dict = {
                'strategy_name': result.strategy_name,
                'start_date': result.start_date.isoformat(),
                'end_date': result.end_date.isoformat(),
                'total_trades': result.total_trades,
                'winning_trades': result.winning_trades,
                'losing_trades': result.losing_trades,
                'win_rate': result.win_rate,
                'total_profit': result.total_profit,
                'total_loss': result.total_loss,
                'net_profit': result.net_profit,
                'max_drawdown': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'profit_factor': result.profit_factor,
                'avg_win': result.avg_win,
                'avg_loss': result.avg_loss,
                'largest_win': result.largest_win,
                'largest_loss': result.largest_loss,
                'consecutive_wins': result.consecutive_wins,
                'consecutive_losses': result.consecutive_losses,
                'roi': result.roi,
                'trades': result.trades
            }
            export_data.append(result_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados exportados para: {filename}")
        return filename

