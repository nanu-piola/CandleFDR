import argparse
import os
import pandas as pd
import yfinance as yf
from tokenizer import tokenizar_dataframe

def main():
    parser = argparse.ArgumentParser(description="CandleFDR Real-Time Alerts")
    parser.add_argument("--ticker", type=str, default="SPY", help="Ticker a escanear")
    args = parser.parse_args()

    if not os.path.exists("winners.csv"):
        print("Error: No existe winners.csv. Ejecutá ./engine primero.")
        return

    winners_df = pd.read_csv("winners.csv")
    patrones_ganadores = set(winners_df['pattern_id'].astype(str).tolist())

    print(f"Analizando alerta para {args.ticker}...")
    df = yf.download(args.ticker, period="3mo", interval="1d")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    df = tokenizar_dataframe(df)

    # Verificamos las dos últimas velas cerradas
    ultimos_tokens = df['Token'].tail(2).tolist()
    fechas = df.index.tail(2).strftime('%Y-%m-%d').tolist()
    
    secuencia_actual = f"{ultimos_tokens[0]}-{ultimos_tokens[1]}"
    print(f"Vela {fechas[0]}: Token {ultimos_tokens[0]}")
    print(f"Vela {fechas[1]}: Token {ultimos_tokens[1]}")
    print(f"Secuencia detectada: {secuencia_actual}\n")

    if secuencia_actual in patrones_ganadores:
        print(f"🚨 ¡SEÑAL DE COMPRA DETECTADA! ({secuencia_actual})")
        print("💡 Ejecutar orden al OPEN de la siguiente sesión.")
    else:
        print("🟢 Estado: NEUTRO / SIN SEÑAL")

if __name__ == "__main__":
    main()