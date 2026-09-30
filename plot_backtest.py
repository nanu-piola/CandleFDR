import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Requerimos matplotlib: pip install matplotlib

def correr_backtest_y_graficar(ticker: str):
    print(f"Simulando estrategia para {ticker}...")
    df = yf.download(ticker, start="2000-01-01", end="2026-01-01")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()

    # 1. Recreamos la tokenización
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['Trend'] = np.where(df['Close'] > df['SMA_50'], 1, 0)
    df['Color'] = np.where(df['Close'] >= df['Open'], 1, 0)
    
    df['Body'] = (df['Close'] - df['Open']).abs()
    total_range = (df['High'] - df['Low']).replace(0, np.nan)
    df['Body_Rel'] = df['Body'] / total_range
    df['Body_Cat'] = np.where(df['Body_Rel'] > 0.50, 1, 0)
    
    max_oc = df[['Open', 'Close']].max(axis=1)
    min_oc = df[['Open', 'Close']].min(axis=1)
    df['Upper_Wick'] = (df['High'] - max_oc) / total_range
    df['Lower_Wick'] = (min_oc - df['Low']) / total_range
    
    conditions = [(df['Upper_Wick'] > 0.4), (df['Lower_Wick'] > 0.4)]
    df['Wick_Cat'] = np.select(conditions, [0, 1], default=2)
    
    base_token = (df['Color'].astype(int) * 6 + df['Body_Cat'].astype(int) * 3 + df['Wick_Cat'].astype(int))
    df['Token'] = df['Trend'].astype(int) * 12 + base_token

    # 2. Detección de señales (2-gramas ganadores: 14-17 y 0-23)
    df['Prev_Token'] = df['Token'].shift(1)
    df['Signal'] = ((df['Prev_Token'] == 14) & (df['Token'] == 17)) | ((df['Prev_Token'] == 0) & (df['Token'] == 23))

    # 3. Simulación de retornos
    df['Market_Return'] = df['Close'].pct_change()
    # Entramos al cierre de la señal y mantenemos 1 día
    df['Strategy_Return'] = np.where(df['Signal'].shift(1), df['Market_Return'], 0.0)

    # 4. Curvas de Capital
    df['Equity_Market'] = (1 + df['Market_Return'].fillna(0)).cumprod()
    df['Equity_Strategy'] = (1 + df['Strategy_Return'].fillna(0)).cumprod()

    # 5. Métricas clave
    trades = df[df['Signal'].shift(1).fillna(False)]
    win_rate = (trades['Market_Return'] > 0).mean() * 100
    total_trades = len(trades)
    
    print("\n=== METRICAS DEL BACKTEST ===")
    print(f"Total Operaciones Ejecutadas: {total_trades}")
    print(f"Tasa de Acierto (Win Rate): {win_rate:.2f}%")
    print(f"Retorno Acumulado Estrategia: {(df['Equity_Strategy'].iloc[-1] - 1) * 100:.2f}%")
    print(f"Retorno Acumulado Mercado: {(df['Equity_Market'].iloc[-1] - 1) * 100:.2f}%")

    # 6. Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Equity_Strategy'], label="Estrategia FDR Pattern Alpha", color="green", linewidth=2)
    plt.plot(df.index, df['Equity_Market'], label=f"Buy & Hold ({ticker})", color="gray", alpha=0.5)
    plt.title(f"Curva de Capital - FDR Pattern Mining Strategy ({ticker})")
    plt.xlabel("Fecha")
    plt.ylabel("Multiplicador de Capital")
    plt.legend()
    plt.grid(True)
    plt.savefig("equity_curve.png")
    print("\n Gráfico guardado exitosamente como 'equity_curve.png'")
    plt.show()

if __name__ == "__main__":
    correr_backtest_y_graficar("SPY")