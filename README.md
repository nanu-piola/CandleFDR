# 📈 FDR Pattern Mining & Alpha Engine

Un motor cuantitativo híbrido (**C++ / Python**) diseñado para descubrir, verificar y filtrar patrones de velas japonesas utilizando **minería de secuencias discretas ($N$-gramas)** y la corrección de hipótesis múltiples de **Benjamini-Hochberg (False Discovery Rate - FDR)**.

Este sistema separa el ruido aleatorio del mercado de las ventajas estadísticas reales (alfa), eliminando falsos positivos comunes en el trading técnico.

---

## 🚀 Arquitectura del Pipeline


[yfinance / Python] ──> [Tokenización de Velas] ──> [Engine C++ (Fast Search & FDR)]
│                                                               |
[Alertas en Tiempo Real] <── [Backtest & Plots] <───────────────┘


1. **`fetch_and_tokenize.py`**: Bautiza y discretiza el histórico del activo en un alfabeto de tokens (combinando color, tamaño de cuerpo, mechas y posición respecto a la SMA 50).
2. **`engine.cpp`**: Mina secuencias ($N$-gramas) a alta velocidad en C++, calcula $t$-statistic, $p$-values y aplica el filtro **FDR (q = 0.05)**.
3. **`alert_engine.py`**: Lee la última vela cerrada y notifica si se formó una secuencia ganadora hoy.
4. **`plot_backtest.py`**: Genera métricas de efectividad (Win Rate, Retorno Acumulado) y la curva de equity comparada contra *Buy & Hold*.

---

## 🛠️ Requisitos e Instalación

```bash
# 1. Clonar el repositorio
git clone [https://github.com/nanu-piola/fdr-pattern-engine.git](https://github.com/nanu-piola/fdr-pattern-engine.git)
cd fdr-pattern-engine

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias de Python
pip install pandas numpy yfinance matplotlib

# 4. Compilar el motor C++ con máxima optimización
g++ -O3 engine.cpp -o engine

# 5. Dar permisos al pipeline ejecutable
chmod +x run_pipeline.sh

---

Ejecutar con 1 solo comando

para correr todo el análisis de punta a punta (descarga, mineria, alerta diaria y gráfico):

./run_pipeline.sh

---

🔄 ¿Cómo adaptarlo a otros activos (XRP, BTC, ETH, PEPE, S&P 500, etc.)?
El motor es 100% agnóstico al activo. Si querés analizar otra cripto o acción, solo tenés que modificar estas 3 cosas:

1. Cambiar el ticker de descarga (fetch_and_tokenize.py)
Abrí fetch_and_tokenize.py y modificá la variable ticker en la última línea (linea 54):

if __name__ == "__main__":
    ticker = "BTC-USD"  # Ejemplos: "XRP-USD", "ETH-USD", "PEPE-USD", "SPY", "NVDA" (no "USDT" ni "USDC" ni ninguno de esos, solo USD)

Corré python fetch_and_tokenize.py

2. Minar los patrones válidos del nuevo activo (./engine)
Ejecutá el motor en C++:
    
./engine

Mirá la columna FDR Pass. Anotá únicamente los pares que digan SÍ (esos son los patrones con ventaja matemática verificada para este activo específico).

3. Actualizar la alerta y el backtest (alert_engine.py y plot_backtest.py)
Colocá los patrones ganadores obtenidos en el paso anterior dentro del diccionario PATRONES_GANADORES y cambiá el ticker al final del archivo:

    PATRONES_GANADORES = {
        (18, 21): "COMPRA (Estrategia Alfa BTC)"}
    

    if __name__ == "__main__":
        tokenizar_ultima_secuencia("BTC-USD")