# 📈 CandleFDR: FDR Pattern Mining & Out-of-Sample Alpha Engine

Un motor cuantitativo híbrido (**C++17 / Python**) diseñado para descubrir, verificar y filtrar patrones de velas japonesas utilizando **minería de secuencias discretas ($N$-gramas)** y la corrección de hipótesis múltiples de **Benjamini-Hochberg (False Discovery Rate - FDR Step-Up)**.

El sistema elimina el ruido aleatorio del mercado y el sobreajuste (*overfitting*), evaluando los patrones descubiertos bajo un régimen estricto de prueba **Out-of-Sample (2019–2026)** con ejecución al Open de $T+1$ y costos de transacción incorporados.

---

## 🚀 Arquitectura del Pipeline


[yfinance / Python] ──> [tokenizer.py] ──> [Engine C++17 (FDR Step-Up)]
│
[Alertas en Tiempo Real] <── [winners.csv] <───────────┘
│
[Backtest Out-of-Sample (2019-2026)]



1. **`tokenizer.py`**: Módulo centralizado de tokenización determinística con umbrales fijos (0.50 cuerpo, 0.40 mechas) que previene el *look-ahead bias*.
2. **`fetch_and_tokenize.py`**: Descarga el historial con `yfinance` y exporta la ventana **In-Sample (2000–2018)** para la minería cuantitativa en C++.
3. **`engine.cpp`**: Motor en C++17 con cálculo de varianza $N-1$, $p$-values precisos mediante `std::erfc`, filtro **FDR Step-Up ($q = 0.05$)**, selección de $t_{stat} > 0$ y exportación dinámica a `winners.csv`.
4. **`alert_engine.py`**: Lee `winners.csv` y escanea las velas recientes para alertar si hoy se formó un patrón ganador validado.
5. **`plot_backtest.py`**: Evalúa la estrategia **exclusivamente en el período Out-of-Sample (2019–2026)** ingresando al Open de $T+1$, aplicando comisiones/slippage y generando métricas finas (Sharpe Ratio, Win Rate, Equity Curve).
6. **`run_pipeline.sh`**: Script ejecutable en Bash con `set -euo pipefail` que compila el motor C++17 y ejecuta las 5 etapas del pipeline en un solo comando.

---

## 🛠️ Requisitos e Instalación

```bash
# 1. Clonar el repositorio
git clone [https://github.com/nanu-piola/CandleFDR.git](https://github.com/nanu-piola/CandleFDR.git)
cd CandleFDR

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias de Python
pip install -r requirements.txt

# 4. Dar permisos de ejecución al pipeline
chmod +x run_pipeline.sh


⚡ Ejecución en Un Solo Comando
Podés analizar cualquier activo pasando el ticker deseado como argumento (por defecto procesa SPY)[cite: 12]:



Bash
# Analizar el S&P 500 (SPY)
./run_pipeline.sh SPY

# Analizar Criptomonedas
./run_pipeline.sh BTC-USD
./run_pipeline.sh ETH-USD
./run_pipeline.sh XRP-USD

# Analizar Acciones Individuales
./run_pipeline.sh NVDA
./run_pipeline.sh AAPL


🔄 ¿Cómo funciona con otros activos?
El pipeline es 100% dinámico. Cuando ejecutás ./run_pipeline.sh TICKER:

Se descargan los datos y se tokenizan con tokenizer.py.

El motor C++ mina los patrones significativos de ese activo en el período de entrenamiento (2000-2018) y guarda los patrones aprobados por FDR en winners.csv.

Los scripts de alerta y backtest leen automáticamente winners.csv, garantizando que siempre se operen los patrones estadísticamente válidos para el ticker seleccionado.

📊 Integración con TradingView (Pine Script)
El archivo strategy.pinescript contiene la implementación oficial en Pine Script v5. Incluye la instrucción process_orders_on_close=true para garantizar una ejecución 1:1 sincronizada con la simulación en Python.




Licencia
MIT License - Desarrollado de forma libre para fines educativos y cuantitativos.