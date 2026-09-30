#!/bin/bash

echo "=================================================="
echo "   FDR PATTERN MINING & ALPHA ENGINE PIPELINE    "
echo "=================================================="

# 1. Extracción de datos y tokenización
echo -e "\n[1/4] Descargando datos y generando tokens..."
python fetch_and_tokenize.py

# 2. Minería C++ y Test de Hipótesis FDR
echo -e "\n[2/4] Ejecutando motor de minería estadístico en C++..."
./engine

# 3. Alertas en tiempo real para el día de hoy
echo -e "\n[3/4] Escaneando mercado para señal de hoy..."
python alert_engine.py

# 4. Generación de backtest y gráficos
echo -e "\n[4/4] Simulando performance histórica y generando curva de capital..."
python plot_backtest.py

echo -e "\n=================================================="
echo "   PIPELINE COMPLETADO CON ÉXITO   "
echo "=================================================="