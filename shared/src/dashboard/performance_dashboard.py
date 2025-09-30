#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard de Performance em Tempo Real para Blaze Double Analyzer
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import logging

logger = logging.getLogger(__name__)

class PerformanceDashboard:
    """Dashboard de performance em tempo real"""
    
    def __init__(self, parent, analyzer=None):
        self.parent = parent
        self.analyzer = analyzer
        self.is_running = False
        self.update_interval = 5  # segundos
        
        # Integrador de métricas
        from .metrics_integrator import MetricsIntegrator
        self.metrics_integrator = MetricsIntegrator(analyzer=analyzer)
        
        # Dados em tempo real
        self.performance_data = {
            'timestamps': [],
            'win_rate': [],
            'roi': [],
            'drawdown': [],
            'sharpe_ratio': [],
            'profit_factor': [],
            'total_trades': [],
            'current_capital': []
        }
        
        # Configurar interface
        self.setup_ui()
        
        logger.info("Performance Dashboard inicializado")
    
    def setup_ui(self):
        """Configura a interface do dashboard"""
        # Janela principal
        self.window = tk.Toplevel(self.parent)
        self.window.title("📊 Dashboard de Performance - Tempo Real")
        self.window.geometry("1200x800")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(title_frame, text="📊 DASHBOARD DE PERFORMANCE", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # Status
        self.status_var = tk.StringVar(value="🟢 Ativo")
        ttk.Label(title_frame, textvariable=self.status_var, 
                 font=('Arial', 12)).pack(side='right')
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text="Controles", padding=10)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Botões de controle
        ttk.Button(controls_frame, text="▶️ Iniciar", 
                  command=self.start_monitoring).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="⏸️ Pausar", 
                  command=self.pause_monitoring).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="🔄 Atualizar", 
                  command=self.update_data).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="📊 Exportar", 
                  command=self.export_data).pack(side='left', padx=(0, 5))
        
        # Intervalo de atualização
        ttk.Label(controls_frame, text="Intervalo (s):").pack(side='left', padx=(20, 5))
        self.interval_var = tk.StringVar(value="5")
        interval_spin = ttk.Spinbox(controls_frame, from_=1, to=60, width=5, 
                                   textvariable=self.interval_var)
        interval_spin.pack(side='left', padx=(0, 10))
        
        # Frame principal com métricas
        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.pack(fill='both', expand=True)
        
        # Coluna esquerda - Métricas numéricas
        left_frame = ttk.Frame(metrics_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Métricas principais
        self.setup_metrics_cards(left_frame)
        
        # Coluna direita - Gráficos
        right_frame = ttk.Frame(metrics_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Gráficos
        self.setup_charts(right_frame)
    
    def setup_metrics_cards(self, parent):
        """Configura os cards de métricas"""
        # Card 1: Performance Geral
        card1 = ttk.LabelFrame(parent, text="📈 Performance Geral", padding=10)
        card1.pack(fill='x', pady=(0, 10))
        
        self.win_rate_var = tk.StringVar(value="0.0%")
        self.roi_var = tk.StringVar(value="0.0%")
        self.total_trades_var = tk.StringVar(value="0")
        
        ttk.Label(card1, text="Taxa de Acerto:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card1, textvariable=self.win_rate_var, 
                 font=('Arial', 14, 'bold'), foreground='green').pack(anchor='w')
        
        ttk.Label(card1, text="ROI:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card1, textvariable=self.roi_var, 
                 font=('Arial', 14, 'bold'), foreground='blue').pack(anchor='w')
        
        ttk.Label(card1, text="Total de Trades:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card1, textvariable=self.total_trades_var, 
                 font=('Arial', 14, 'bold')).pack(anchor='w')
        
        # Card 2: Risco
        card2 = ttk.LabelFrame(parent, text="⚠️ Gestão de Risco", padding=10)
        card2.pack(fill='x', pady=(0, 10))
        
        self.drawdown_var = tk.StringVar(value="0.0%")
        self.sharpe_var = tk.StringVar(value="0.00")
        self.profit_factor_var = tk.StringVar(value="0.00")
        
        ttk.Label(card2, text="Drawdown Máximo:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card2, textvariable=self.drawdown_var, 
                 font=('Arial', 14, 'bold'), foreground='red').pack(anchor='w')
        
        ttk.Label(card2, text="Sharpe Ratio:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card2, textvariable=self.sharpe_var, 
                 font=('Arial', 14, 'bold'), foreground='purple').pack(anchor='w')
        
        ttk.Label(card2, text="Profit Factor:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card2, textvariable=self.profit_factor_var, 
                 font=('Arial', 14, 'bold'), foreground='orange').pack(anchor='w')
        
        # Card 3: Capital
        card3 = ttk.LabelFrame(parent, text="💰 Capital", padding=10)
        card3.pack(fill='x', pady=(0, 10))
        
        self.capital_var = tk.StringVar(value="R$ 0.00")
        self.profit_var = tk.StringVar(value="R$ 0.00")
        self.avg_win_var = tk.StringVar(value="R$ 0.00")
        
        ttk.Label(card3, text="Capital Atual:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card3, textvariable=self.capital_var, 
                 font=('Arial', 14, 'bold'), foreground='green').pack(anchor='w')
        
        ttk.Label(card3, text="Lucro/Prejuízo:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card3, textvariable=self.profit_var, 
                 font=('Arial', 14, 'bold')).pack(anchor='w')
        
        ttk.Label(card3, text="Ganho Médio:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card3, textvariable=self.avg_win_var, 
                 font=('Arial', 14, 'bold'), foreground='blue').pack(anchor='w')
        
        # Card 4: Status
        card4 = ttk.LabelFrame(parent, text="📊 Status Atual", padding=10)
        card4.pack(fill='x')
        
        self.last_update_var = tk.StringVar(value="Nunca")
        self.next_update_var = tk.StringVar(value="N/A")
        self.data_points_var = tk.StringVar(value="0")
        
        ttk.Label(card4, text="Última Atualização:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card4, textvariable=self.last_update_var, 
                 font=('Arial', 12)).pack(anchor='w')
        
        ttk.Label(card4, text="Próxima Atualização:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card4, textvariable=self.next_update_var, 
                 font=('Arial', 12)).pack(anchor='w')
        
        ttk.Label(card4, text="Pontos de Dados:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(card4, textvariable=self.data_points_var, 
                 font=('Arial', 12)).pack(anchor='w')
    
    def setup_charts(self, parent):
        """Configura os gráficos"""
        # Frame para gráficos
        charts_frame = ttk.Frame(parent)
        charts_frame.pack(fill='both', expand=True)
        
        # Gráfico 1: Performance ao longo do tempo
        chart1_frame = ttk.LabelFrame(charts_frame, text="📈 Performance ao Longo do Tempo", padding=5)
        chart1_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.fig1 = Figure(figsize=(6, 4), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, chart1_frame)
        self.canvas1.get_tk_widget().pack(fill='both', expand=True)
        
        # Gráfico 2: Distribuição de resultados
        chart2_frame = ttk.LabelFrame(charts_frame, text="📊 Distribuição de Resultados", padding=5)
        chart2_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        self.fig2 = Figure(figsize=(6, 3), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, chart2_frame)
        self.canvas2.get_tk_widget().pack(fill='both', expand=True)
        
        # Inicializar gráficos
        self.init_charts()
    
    def init_charts(self):
        """Inicializa os gráficos"""
        # Gráfico 1: Performance
        self.ax1.set_title('Performance ao Longo do Tempo')
        self.ax1.set_xlabel('Tempo')
        self.ax1.set_ylabel('Valor')
        self.ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Distribuição
        self.ax2.set_title('Distribuição de Resultados')
        self.ax2.set_xlabel('Tipo')
        self.ax2.set_ylabel('Quantidade')
        self.ax2.grid(True, alpha=0.3)
        
        # Atualizar gráficos
        self.update_charts()
    
    def start_monitoring(self):
        """Inicia o monitoramento em tempo real"""
        if not self.is_running:
            self.is_running = True
            self.update_interval = int(self.interval_var.get())
            self.status_var.set("🟢 Ativo")
            
            # Iniciar thread de atualização
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("Monitoramento iniciado")
    
    def pause_monitoring(self):
        """Pausa o monitoramento"""
        self.is_running = False
        self.status_var.set("⏸️ Pausado")
        logger.info("Monitoramento pausado")
    
    def monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            try:
                self.update_data()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(5)
    
    def update_data(self):
        """Atualiza os dados do dashboard"""
        try:
            if not self.analyzer:
                return
            
            # Obter dados do analyzer
            current_data = self.get_current_metrics()
            
            # Atualizar dados em tempo real
            timestamp = datetime.now()
            self.performance_data['timestamps'].append(timestamp)
            
            for key, value in current_data.items():
                if key in self.performance_data:
                    self.performance_data[key].append(value)
            
            # Manter apenas últimos 100 pontos
            max_points = 100
            for key in self.performance_data:
                if len(self.performance_data[key]) > max_points:
                    self.performance_data[key] = self.performance_data[key][-max_points:]
            
            # Atualizar interface
            self.update_metrics_display(current_data)
            self.update_charts()
            
            # Atualizar status
            self.last_update_var.set(timestamp.strftime("%H:%M:%S"))
            next_update = timestamp + timedelta(seconds=self.update_interval)
            self.next_update_var.set(next_update.strftime("%H:%M:%S"))
            self.data_points_var.set(str(len(self.performance_data['timestamps'])))
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dados: {e}")
    
    def get_current_metrics(self):
        """Obtém métricas atuais do analyzer"""
        try:
            # Usar o integrador de métricas
            return self.metrics_integrator.get_current_metrics()
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {
                'win_rate': 0.0,
                'roi': 0.0,
                'drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'profit_factor': 0.0,
                'total_trades': 0,
                'current_capital': 1000.0
            }
    
    def update_metrics_display(self, data):
        """Atualiza a exibição das métricas"""
        try:
            self.win_rate_var.set(f"{data['win_rate']:.1%}")
            self.roi_var.set(f"{data['roi']:.1f}%")
            self.total_trades_var.set(str(data['total_trades']))
            
            self.drawdown_var.set(f"{data['drawdown']:.1f}%")
            self.sharpe_var.set(f"{data['sharpe_ratio']:.2f}")
            self.profit_factor_var.set(f"{data['profit_factor']:.2f}")
            
            self.capital_var.set(f"R$ {data['current_capital']:.2f}")
            profit = data['current_capital'] - 1000.0  # Assumindo capital inicial de 1000
            self.profit_var.set(f"R$ {profit:+.2f}")
            self.avg_win_var.set(f"R$ {data['current_capital'] * 0.1:.2f}")  # Exemplo
            
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas: {e}")
    
    def update_charts(self):
        """Atualiza os gráficos"""
        try:
            if not self.performance_data['timestamps']:
                return
            
            # Gráfico 1: Performance ao longo do tempo
            self.ax1.clear()
            
            if len(self.performance_data['timestamps']) > 1:
                times = self.performance_data['timestamps']
                roi_data = self.performance_data['roi']
                win_rate_data = [x * 100 for x in self.performance_data['win_rate']]
                
                # Plotar ROI
                self.ax1.plot(times, roi_data, label='ROI (%)', color='blue', linewidth=2)
                
                # Plotar Win Rate
                ax1_twin = self.ax1.twinx()
                ax1_twin.plot(times, win_rate_data, label='Win Rate (%)', color='green', linewidth=2)
                
                self.ax1.set_title('Performance ao Longo do Tempo')
                self.ax1.set_xlabel('Tempo')
                self.ax1.set_ylabel('ROI (%)', color='blue')
                ax1_twin.set_ylabel('Win Rate (%)', color='green')
                
                # Adicionar legendas
                lines1, labels1 = self.ax1.get_legend_handles_labels()
                lines2, labels2 = ax1_twin.get_legend_handles_labels()
                self.ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            self.ax1.grid(True, alpha=0.3)
            
            # Gráfico 2: Distribuição de resultados
            self.ax2.clear()
            
            if len(self.performance_data['total_trades']) > 0:
                # Obter distribuição real de resultados
                distribution = self.metrics_integrator.get_trade_distribution()
                wins = distribution.get('wins', 0)
                losses = distribution.get('losses', 0)
                
                categories = ['Vitórias', 'Derrotas']
                values = [wins, losses]
                colors = ['green', 'red']
                
                bars = self.ax2.bar(categories, values, color=colors, alpha=0.7)
                
                # Adicionar valores nas barras
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    self.ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{value}', ha='center', va='bottom')
                
                self.ax2.set_title('Distribuição de Resultados')
                self.ax2.set_ylabel('Quantidade')
            
            self.ax2.grid(True, alpha=0.3)
            
            # Atualizar canvas
            self.canvas1.draw()
            self.canvas2.draw()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar gráficos: {e}")
    
    def export_data(self):
        """Exporta os dados do dashboard"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Exportar Dados do Dashboard"
            )
            
            if filename:
                # Criar DataFrame com os dados
                df = pd.DataFrame(self.performance_data)
                df.to_csv(filename, index=False)
                
                logger.info(f"Dados exportados para: {filename}")
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
    
    def on_closing(self):
        """Chamado quando a janela é fechada"""
        self.is_running = False
        self.window.destroy()
        logger.info("Dashboard fechado")
