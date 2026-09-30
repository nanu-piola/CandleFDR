import argparse
import pandas as pd
import yfinance as yf
from tokenizer import tokenizar_dataframe

def main():
    parser = argparse.ArgumentParser(description="CandleFDR Data Extractor")
    parser.add_argument("--ticker", type=str, default="SPY", help="Ticker del activo (ej: SPY, BTC-USD, XRP-USD)")
    args = parser.parse_args()

    print(f"Descargando datos históricos completos para {args.ticker}...")
    df = yf.download(args.ticker, start="2000-01-01")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()
    df = tokenizar_dataframe(df)

    # Split Train (In-Sample para minar)
    train_df = df.loc[:"2018-12-31"]
    
    # Exportamos los datos de entrenamiento para C++
    train_export = train_df[['Token', 'Exec_Return']].dropna()
    train_export.to_csv("tokens_data.csv", index=False)
    print(f"Datos de Entrenamiento (2000-2018) exportados a tokens_data.csv ({len(train_export)} velas).")

if __name__ == "__main__":
    main()