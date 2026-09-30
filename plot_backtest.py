import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from tokenizer import tokenizar_dataframe

def main():
    parser = argparse.ArgumentParser(description="CandleFDR Out-of-Sample Backtester")
    parser.add_argument("--ticker", type=str, default="SPY", help="Ticker a evaluar")
    parser.add_argument("--fee", type=float, default=0.0005, help="Comisión + Slippage por operacion (0.05%)")
    args = parser.parse_args()

    if not os.path.exists("winners.csv"):
        print("Error: No existe winners.csv. Corré ./engine primero.")
        return

    winners_df = pd.read_csv("winners.csv")
    patrones_ganadores = set(winners_df['pattern_id'].astype(str).tolist())

    df = yf.download(args.ticker, start="2018-01-01") # Descargamos desde 2018 para tener SMA 50 lista en 2019
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    df = tokenizar_dataframe(df)

    # Filtración estricta OUT-OF-SAMPLE (2019 - Presente)
    df_oos = df.loc["2019-01-01":].copy()

    df_oos['Prev_Token'] = df_oos['Token'].shift(1)
    df_oos['Pattern_Key'] = df_oos['Prev_Token'].astype(str).str.replace('.0', '', regex=False) + "-" + df_oos['Token'].astype(str).str.replace('.0', '', regex=False)

    # Señal
    df_oos['Signal'] = df_oos['Pattern_Key'].isin(patrones_ganadores)
    signal_mask = df_oos['Signal'].shift(1, fill_value=False)

    # Retorno neto con comisión
    df_oos['Strat_Return'] = np.where(signal_mask, df_oos['Exec_Return'] - (args.fee * 2), 0.0)

    # Equity Curves
    df_oos['Market_Return'] = df_oos['Close'].pct_change()
    df_oos['Equity_Strategy'] = (1 + df_oos['Strat_Return'].fillna(0)).cumprod()
    df_oos['Equity_Market'] = (1 + df_oos['Market_Return'].fillna(0)).cumprod()

    # Métricas Quant
    trades = df_oos[signal_mask]
    n_trades = len(trades)
    
    if n_trades > 0:
        win_rate = (trades['Exec_Return'] > 0).mean() * 100
        avg_ret = trades['Exec_Return'].mean() * 100
    else:
        win_rate = 0.0
        avg_ret = 0.0

    # Sharpe Ratio Anualizado
    daily_rets = df_oos['Strat_Return']
    sharpe = (daily_rets.mean() / daily_rets.std()) * np.sqrt(252) if daily_rets.std() > 0 else 0.0

    print("\n=== METRICAS OUT-OF-SAMPLE (2019-2026) ===")
    print(f"Total Operaciones OOS: {n_trades}")
    print(f"Win Rate OOS: {win_rate:.2f}%")
    print(f"Retorno Medio por Trade: {avg_ret:.2f}%")
    print(f"Sharpe Ratio Anualizado: {sharpe:.2f}")

    # Plotting no bloqueante
    plt.figure(figsize=(10, 5))
    plt.plot(df_oos.index, df_oos['Equity_Strategy'], label="CandleFDR (OOS)", color="green", linewidth=2)
    plt.plot(df_oos.index, df_oos['Equity_Market'], label=f"Buy & Hold ({args.ticker})", color="gray", alpha=0.5)
    plt.title(f"Out-of-Sample Equity Curve - CandleFDR ({args.ticker})")
    plt.ylabel("Multiplicador de Capital (Escala Log)")
    plt.yscale("log")
    plt.legend()
    plt.grid(True)
    plt.savefig("equity_curve.png")
    print("Gráfico OOS guardado como 'equity_curve.png'")
    plt.close()

if __name__ == "__main__":
    main()