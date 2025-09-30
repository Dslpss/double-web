#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Engine de Machine Learning inspirado no PyBlaze para análise do Double da Blaze.
Baseado nos conceitos do PyBlaze: https://github.com/borchero/pyblaze
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BlazeDataset(Dataset):
    """Dataset personalizado para dados do Double da Blaze."""
    
    def __init__(self, data: List[Dict], sequence_length: int = 10):
        """
        Inicializa o dataset.
        
        Args:
            data (List[Dict]): Lista de resultados do Double
            sequence_length (int): Tamanho da sequência para predição
        """
        self.data = data
        self.sequence_length = sequence_length
        self.sequences, self.targets = self._prepare_sequences()
        
    def _prepare_sequences(self):
        """Prepara sequências de entrada e targets."""
        sequences = []
        targets = []
        
        for i in range(len(self.data) - self.sequence_length):
            # Extrair sequência de cores
            sequence = []
            for j in range(i, i + self.sequence_length):
                color = self.data[j].get('color', 'red')
                # Codificar cores como números
                color_encoding = {'red': 0, 'black': 1, 'white': 2}
                sequence.append(color_encoding.get(color, 0))
            
            # Target é a próxima cor
            target_color = self.data[i + self.sequence_length].get('color', 'red')
            target = {'red': 0, 'black': 1, 'white': 2}.get(target_color, 0)
            
            sequences.append(sequence)
            targets.append(target)
        
        return torch.tensor(sequences, dtype=torch.long), torch.tensor(targets, dtype=torch.long)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

class BlazeLSTM(nn.Module):
    """Modelo LSTM para predição de cores do Double da Blaze."""
    
    def __init__(self, input_size: int = 3, hidden_size: int = 64, num_layers: int = 2, output_size: int = 3):
        """
        Inicializa o modelo LSTM.
        
        Args:
            input_size (int): Tamanho da entrada (número de cores)
            hidden_size (int): Tamanho da camada oculta
            num_layers (int): Número de camadas LSTM
            output_size (int): Tamanho da saída (probabilidades das cores)
        """
        super(BlazeLSTM, self).__init__()
        
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_size, output_size)
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, x):
        """Forward pass do modelo."""
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        # Usar apenas a última saída
        last_output = lstm_out[:, -1, :]
        dropped = self.dropout(last_output)
        output = self.fc(dropped)
        return self.softmax(output)

class Callback(ABC):
    """Classe base para callbacks."""
    
    @abstractmethod
    def on_epoch_begin(self, epoch: int, logs: Dict[str, float]):
        """Chamado no início de cada época."""
        pass
    
    @abstractmethod
    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        """Chamado no final de cada época."""
        pass
    
    def on_batch_begin(self, batch: int, logs: Dict[str, float]):
        """Chamado no início de cada batch."""
        pass
    
    def on_batch_end(self, batch: int, logs: Dict[str, float]):
        """Chamado no final de cada batch."""
        pass

class EarlyStopping(Callback):
    """Callback para parada antecipada."""
    
    def __init__(self, patience: int = 10, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.wait = 0
        self.stopped_epoch = 0
        
    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        current_loss = logs.get('val_loss', logs.get('loss', float('inf')))
        
        if current_loss < self.best_loss - self.min_delta:
            self.best_loss = current_loss
            self.wait = 0
        else:
            self.wait += 1
            
        if self.wait >= self.patience:
            self.stopped_epoch = epoch
            logger.info(f"Early stopping at epoch {epoch}")
            return True
        return False

class ModelCheckpoint(Callback):
    """Callback para salvar o melhor modelo."""
    
    def __init__(self, filepath: str, monitor: str = 'val_loss', save_best_only: bool = True):
        self.filepath = filepath
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.best_score = float('inf')
        
    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        current_score = logs.get(self.monitor, float('inf'))
        
        if not self.save_best_only or current_score < self.best_score:
            self.best_score = current_score
            torch.save({
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'loss': current_score,
                'logs': logs
            }, self.filepath)
            logger.info(f"Model saved to {self.filepath}")

class PatternAlertCallback(Callback):
    """Callback para alertas de padrões detectados."""
    
    def __init__(self, alert_system):
        self.alert_system = alert_system
        self.confidence_threshold = 0.8
        
    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        accuracy = logs.get('val_accuracy', logs.get('accuracy', 0))
        
        if accuracy >= self.confidence_threshold:
            prediction = {
                'confidence': accuracy,
                'method': 'ML_LSTM',
                'color': 'high_confidence_detected',
                'timestamp': datetime.now().isoformat()
            }
            self.alert_system.set_alert(prediction)

class BlazeMLEngine:
    """
    Engine de Machine Learning inspirado no PyBlaze para análise do Double da Blaze.
    """
    
    def __init__(self, model: nn.Module, device: str = None):
        """
        Inicializa o engine.
        
        Args:
            model (nn.Module): Modelo PyTorch
            device (str): Dispositivo para execução ('cpu', 'cuda', etc.)
        """
        self.model = model
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.callbacks: List[Callback] = []
        self.history: List[Dict[str, float]] = []
        
        logger.info(f"BlazeMLEngine inicializado no dispositivo: {self.device}")
    
    def add_callback(self, callback: Callback):
        """Adiciona um callback ao engine."""
        self.callbacks.append(callback)
        # Passar referências necessárias para o callback
        if hasattr(callback, 'model'):
            callback.model = self.model
        if hasattr(callback, 'optimizer'):
            callback.optimizer = getattr(self, 'optimizer', None)
    
    def train(self, 
              train_loader: DataLoader, 
              val_loader: DataLoader = None,
              epochs: int = 100,
              optimizer: optim.Optimizer = None,
              criterion: nn.Module = None,
              scheduler: Any = None) -> List[Dict[str, float]]:
        """
        Treina o modelo.
        
        Args:
            train_loader (DataLoader): Loader de dados de treino
            val_loader (DataLoader): Loader de dados de validação
            epochs (int): Número de épocas
            optimizer (optim.Optimizer): Otimizador
            criterion (nn.Module): Função de perda
            scheduler: Scheduler de learning rate
            
        Returns:
            List[Dict[str, float]]: Histórico de treinamento
        """
        if optimizer is None:
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        if criterion is None:
            criterion = nn.CrossEntropyLoss()
            
        self.optimizer = optimizer
        
        # Configurar callbacks
        for callback in self.callbacks:
            if hasattr(callback, 'model'):
                callback.model = self.model
            if hasattr(callback, 'optimizer'):
                callback.optimizer = optimizer
        
        logger.info(f"Iniciando treinamento por {epochs} épocas")
        
        for epoch in range(epochs):
            # Início da época
            epoch_logs = {'epoch': epoch}
            
            for callback in self.callbacks:
                callback.on_epoch_begin(epoch, epoch_logs)
            
            # Treinamento
            train_loss, train_accuracy = self._train_epoch(train_loader, criterion, optimizer)
            epoch_logs.update({
                'loss': train_loss,
                'accuracy': train_accuracy
            })
            
            # Validação
            if val_loader:
                val_loss, val_accuracy = self._validate_epoch(val_loader, criterion)
                epoch_logs.update({
                    'val_loss': val_loss,
                    'val_accuracy': val_accuracy
                })
            
            # Scheduler step
            if scheduler:
                scheduler.step()
                epoch_logs['lr'] = scheduler.get_last_lr()[0]
            
            # Callbacks de fim de época
            should_stop = False
            for callback in self.callbacks:
                if callback.on_epoch_end(epoch, epoch_logs):
                    should_stop = True
            
            self.history.append(epoch_logs)
            
            # Log de progresso
            if epoch % 10 == 0 or epoch == epochs - 1:
                logger.info(f"Época {epoch}: Loss={train_loss:.4f}, Acc={train_accuracy:.4f}, Val_Loss={epoch_logs.get('val_loss', 'N/A'):.4f}, Val_Acc={epoch_logs.get('val_accuracy', 'N/A'):.4f}")
            
            if should_stop:
                logger.info("Treinamento interrompido por callback")
                break
        
        return self.history
    
    def _train_epoch(self, train_loader: DataLoader, criterion: nn.Module, optimizer: optim.Optimizer):
        """Executa uma época de treinamento."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            optimizer.zero_grad()
            output = self.model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            # Callbacks de batch
            batch_logs = {'batch': batch_idx, 'batch_loss': loss.item()}
            for callback in self.callbacks:
                callback.on_batch_end(batch_idx, batch_logs)
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def _validate_epoch(self, val_loader: DataLoader, criterion: nn.Module):
        """Executa uma época de validação."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def predict(self, data_loader: DataLoader) -> np.ndarray:
        """Faz predições."""
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for data, _ in data_loader:
                data = data.to(self.device)
                output = self.model(data)
                predictions.extend(output.cpu().numpy())
        
        return np.array(predictions)
    
    def predict_single_sequence(self, sequence: List[int]) -> Dict[str, float]:
        """
        Prediz a próxima cor baseada em uma sequência.
        
        Args:
            sequence (List[int]): Sequência de cores codificadas
            
        Returns:
            Dict[str, float]: Probabilidades para cada cor
        """
        self.model.eval()
        
        # Converter para tensor
        seq_tensor = torch.tensor([sequence], dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            output = self.model(seq_tensor)
            probabilities = output.cpu().numpy()[0]
        
        color_names = ['red', 'black', 'white']
        result = {color_names[i]: float(prob) for i, prob in enumerate(probabilities)}
        
        return result
    
    def save_model(self, filepath: str):
        """Salva o modelo."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'history': self.history
        }, filepath)
        logger.info(f"Modelo salvo em: {filepath}")
    
    def load_model(self, filepath: str):
        """Carrega o modelo."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.history = checkpoint.get('history', [])
        logger.info(f"Modelo carregado de: {filepath}")
    
    def get_model_summary(self) -> str:
        """Retorna um resumo do modelo."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        summary = f"""
=== RESUMO DO MODELO BLAZE LSTM ===
Dispositivo: {self.device}
Total de parâmetros: {total_params:,}
Parâmetros treináveis: {trainable_params:,}
Histórico de treinamento: {len(self.history)} épocas

Último resultado de treinamento:
"""
        
        if self.history:
            last_log = self.history[-1]
            summary += f"Época: {last_log.get('epoch', 'N/A')}\n"
            summary += f"Loss: {last_log.get('loss', 'N/A'):.4f}\n"
            summary += f"Accuracy: {last_log.get('accuracy', 'N/A'):.4f}\n"
            if 'val_loss' in last_log:
                summary += f"Val Loss: {last_log['val_loss']:.4f}\n"
                summary += f"Val Accuracy: {last_log['val_accuracy']:.4f}\n"
        
        return summary

def create_blaze_model(input_size: int = 3, hidden_size: int = 64, num_layers: int = 2) -> BlazeLSTM:
    """
    Cria um modelo Blaze LSTM.
    
    Args:
        input_size (int): Tamanho da entrada
        hidden_size (int): Tamanho da camada oculta
        num_layers (int): Número de camadas LSTM
        
    Returns:
        BlazeLSTM: Modelo LSTM configurado
    """
    return BlazeLSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers)

def create_blaze_engine(model: nn.Module = None, device: str = None) -> BlazeMLEngine:
    """
    Cria um engine Blaze ML.
    
    Args:
        model (nn.Module): Modelo personalizado (opcional)
        device (str): Dispositivo para execução
        
    Returns:
        BlazeMLEngine: Engine configurado
    """
    if model is None:
        model = create_blaze_model()
    
    return BlazeMLEngine(model, device)
