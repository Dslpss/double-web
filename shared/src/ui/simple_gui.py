#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interface gráfica simples para o Double da Blaze Analyzer.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SimpleGUI:
    """Interface gráfica simples para o analisador."""
    
    def __init__(self, config: Dict, api_client, data_collector, pattern_analyzer, db_manager, alert_system):
        """
        Inicializa a interface gráfica.
        
        Args:
            config (Dict): Configurações da interface
            api_client: Cliente da API
            data_collector: Coletor de dados
            pattern_analyzer: Analisador de padrões
            db_manager: Gerenciador de banco de dados
            alert_system: Sistema de alertas
        """
        self.config = config
        self.api_client = api_client
        self.data_collector = data_collector
        self.pattern_analyzer = pattern_analyzer
        self.db_manager = db_manager
        self.alert_system = alert_system
        
        self.root = tk.Tk()
        self.setup_ui()
        self.update_interval = self.config.get('update_interval', 5)
        self.update_thread = None
        self.running = False
        
        logger.info("Interface gráfica inicializada")
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        self.root.title("Blaze Double Analyzer")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Cria o notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba de dados recentes
        self.recent_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recent_frame, text="Dados Recentes")
        self.setup_recent_tab()
        
        # Aba de análise
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Análise")
        self.setup_analysis_tab()
        
        # Aba de alertas
        self.alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alerts_frame, text="Alertas")
        self.setup_alerts_tab()
        
        # Barra de status
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto")
        self.status_label.pack(side='left')
        
        self.time_label = ttk.Label(self.status_frame, text="")
        self.time_label.pack(side='right')
        
        # Botões de controle
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = ttk.Button(self.control_frame, text="Iniciar", command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Parar", command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.refresh_button = ttk.Button(self.control_frame, text="Atualizar", command=self.refresh_data)
        self.refresh_button.pack(side='left', padx=5)
    
    def setup_recent_tab(self):
        """Configura a aba de dados recentes."""
        # Frame principal
        main_frame = ttk.Frame(self.recent_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Resultados Recentes", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Treeview para mostrar os dados
        columns = ('ID', 'Número', 'Cor', 'Data/Hora')
        self.recent_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_analysis_tab(self):
        """Configura a aba de análise."""
        main_frame = ttk.Frame(self.analysis_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Análise de Padrões", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame para estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding=10)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=10, wrap='word')
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True)
        stats_scrollbar.pack(side='right', fill='y')
        
        # Frame para predições
        pred_frame = ttk.LabelFrame(main_frame, text="Predições", padding=10)
        pred_frame.pack(fill='x')
        
        self.pred_text = tk.Text(pred_frame, height=6, wrap='word')
        pred_scrollbar = ttk.Scrollbar(pred_frame, orient='vertical', command=self.pred_text.yview)
        self.pred_text.configure(yscrollcommand=pred_scrollbar.set)
        
        self.pred_text.pack(side='left', fill='both', expand=True)
        pred_scrollbar.pack(side='right', fill='y')
    
    def setup_alerts_tab(self):
        """Configura a aba de alertas."""
        main_frame = ttk.Frame(self.alerts_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Alertas", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame para alertas ativos
        active_frame = ttk.LabelFrame(main_frame, text="Alertas Ativos", padding=10)
        active_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.alerts_tree = ttk.Treeview(active_frame, columns=('Data/Hora', 'Mensagem'), show='headings', height=8)
        self.alerts_tree.heading('Data/Hora', text='Data/Hora')
        self.alerts_tree.heading('Mensagem', text='Mensagem')
        self.alerts_tree.column('Data/Hora', width=150)
        self.alerts_tree.column('Mensagem', width=400)
        
        alerts_scrollbar = ttk.Scrollbar(active_frame, orient='vertical', command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alerts_scrollbar.set)
        
        self.alerts_tree.pack(side='left', fill='both', expand=True)
        alerts_scrollbar.pack(side='right', fill='y')
        
        # Botões de controle de alertas
        alert_control_frame = ttk.Frame(main_frame)
        alert_control_frame.pack(fill='x')
        
        ttk.Button(alert_control_frame, text="Reconhecer Todos", command=self.acknowledge_all_alerts).pack(side='left', padx=5)
        ttk.Button(alert_control_frame, text="Limpar Antigos", command=self.clear_old_alerts).pack(side='left', padx=5)
    
    def start_monitoring(self):
        """Inicia o monitoramento."""
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Monitorando...")
        
        # Inicia thread de atualização
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Parado")
        
        logger.info("Monitoramento parado")
    
    def refresh_data(self):
        """Atualiza os dados manualmente."""
        try:
            # Coleta dados recentes
            recent_data = self.data_collector.collect_recent_data(limit=50)
            
            # Atualiza a interface
            self.update_recent_data(recent_data)
            self.update_analysis(recent_data)
            self.update_alerts()
            
            self.status_label.config(text="Dados atualizados")
            logger.info("Dados atualizados manualmente")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados: {str(e)}")
            logger.error(f"Erro ao atualizar dados: {str(e)}")
    
    def update_loop(self):
        """Loop de atualização contínua."""
        while self.running:
            try:
                self.refresh_data()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Erro no loop de atualização: {str(e)}")
                time.sleep(self.update_interval)
    
    def update_recent_data(self, data: List[Dict]):
        """Atualiza a exibição dos dados recentes."""
        # Limpa a treeview
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Adiciona os novos dados
        for result in data:
            color_names = {'red': 'Vermelho', 'black': 'Preto', 'white': 'Branco'}
            color_pt = color_names.get(result.get('color', ''), result.get('color', ''))
            
            # Formata a data/hora
            timestamp = result.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                date_str = dt.strftime('%d/%m/%Y %H:%M:%S')
            else:
                date_str = result.get('created_at', 'N/A')
            
            self.recent_tree.insert('', 'end', values=(
                result.get('id', 'N/A'),
                result.get('roll', 'N/A'),
                color_pt,
                date_str
            ))
    
    def update_analysis(self, data: List[Dict]):
        """Atualiza a análise."""
        if not data:
            return
        
        # Limpa o texto
        self.stats_text.delete(1.0, tk.END)
        self.pred_text.delete(1.0, tk.END)
        
        # Análise básica
        colors = [r.get('color', '') for r in data]
        color_counts = {}
        for color in colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        total = len(colors)
        
        # Estatísticas
        stats = f"Total de resultados: {total}\n\n"
        stats += "Distribuição de cores:\n"
        
        color_names = {'red': 'Vermelho', 'black': 'Preto', 'white': 'Branco'}
        for color, count in color_counts.items():
            percentage = (count / total) * 100
            color_pt = color_names.get(color, color)
            stats += f"- {color_pt}: {count} ({percentage:.1f}%)\n"
        
        self.stats_text.insert(1.0, stats)
        
        # Predição simples
        pred = f"Último resultado: {color_names.get(data[0].get('color', ''), data[0].get('color', ''))}\n"
        pred += f"Número: {data[0].get('roll', 'N/A')}\n\n"
        pred += "Predição para próximo resultado:\n"
        pred += "Baseada apenas na distribuição atual, todas as cores têm probabilidade similar.\n"
        pred += "⚠️ Lembre-se: jogos de azar são aleatórios!"
        
        self.pred_text.insert(1.0, pred)
    
    def update_alerts(self):
        """Atualiza a lista de alertas."""
        # Limpa a treeview
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        # Adiciona alertas ativos
        active_alerts = self.alert_system.get_active_alerts()
        for alert in active_alerts:
            dt = datetime.fromisoformat(alert['timestamp'])
            date_str = dt.strftime('%d/%m/%Y %H:%M:%S')
            
            self.alerts_tree.insert('', 'end', values=(
                date_str,
                alert['message']
            ))
    
    def acknowledge_all_alerts(self):
        """Reconhece todos os alertas."""
        count = self.alert_system.acknowledge_all_alerts()
        self.update_alerts()
        messagebox.showinfo("Sucesso", f"{count} alertas reconhecidos")
    
    def clear_old_alerts(self):
        """Limpa alertas antigos."""
        count = self.alert_system.clear_old_alerts()
        self.update_alerts()
        messagebox.showinfo("Sucesso", f"{count} alertas antigos removidos")
    
    def start(self):
        """Inicia a interface gráfica."""
        # Atualiza o tempo na barra de status
        def update_time():
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.time_label.config(text=current_time)
            self.root.after(1000, update_time)
        
        update_time()
        
        # Carrega dados iniciais
        self.refresh_data()
        
        # Inicia a interface
        logger.info("Interface gráfica iniciada")
        self.root.mainloop()
    
    def close(self):
        """Fecha a interface gráfica."""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        
        self.root.quit()
        self.root.destroy()
        logger.info("Interface gráfica fechada")
