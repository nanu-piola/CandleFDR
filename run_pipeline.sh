#!/bin/bash
set -euo pipefail

TICKER="${1:-SPY}"

echo "=================================================="
echo "    CANDLEFDR QUANTITATIVE ENGINE PIPELINE       "
echo "=================================================="
echo "Activo Seleccionado: $TICKER"

# 1. Compilación de C++ con C++17
echo -e "\n[1/5] Compilando motor C++..."
g++ -O3 -std=c++17 engine.cpp -o engine

# 2. Extracción de datos
echo -e "\n[2/5] Extrayendo y tokenizando datos (Train: 2000-2018)..."
python3 fetch_and_tokenize.py --ticker "$TICKER"

# 3. Minería C++ y Test de Hipótesis FDR
echo -e "\n[3/5] Minando patrones significativos con FDR Step-Up..."
./engine

# 4. Alertas en tiempo real
echo -e "\n[4/5] Escaneando señal de mercado para hoy..."
python3 alert_engine.py --ticker "$TICKER"

# 5. Backtest Out-of-Sample
echo -e "\n[5/5] Ejecutando Backtest Out-of-Sample (2019-2026)..."
python3 plot_backtest.py --ticker "$TICKER"

echo -e "\n=================================================="
echo "           PIPELINE EXITOSO Y COMPLETO            "
echo "=================================================="