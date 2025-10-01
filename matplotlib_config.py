#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuração do matplotlib para Railway - SEM GUI
Este arquivo DEVE ser importado ANTES de qualquer outro import que use matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Usar backend sem GUI para Railway

# Configurar outras opções do matplotlib
import matplotlib.pyplot as plt
plt.ioff()  # Desabilitar modo interativo

print("✅ Matplotlib configurado para Railway (sem GUI)")
