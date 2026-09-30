import pandas as pd
import numpy as np
import yfinance as yf

def obtener_datos(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    return df

def tokenizar_velas(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Trend Filter: ¿Precio por encima o debajo de SMA 50?
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['Trend'] = np.where(df['Close'] > df['SMA_50'], 1, 0) # 1: Uptrend, 0: Downtrend
    
    # 2. Color (0: Bajista, 1: Alcista)
    df['Color'] = np.where(df['Close'] >= df['Open'], 1, 0)
    
    # 3. Tamaño del cuerpo
    df['Body'] = (df['Close'] - df['Open']).abs()
    total_range = (df['High'] - df['Low']).replace(0, np.nan)
    df['Body_Rel'] = df['Body'] / total_range
    
    body_median = df['Body_Rel'].median()
    df['Body_Cat'] = np.where(df['Body_Rel'] > body_median, 1, 0)
    
    # 4. Mechas
    max_oc = df[['Open', 'Close']].max(axis=1)
    min_oc = df[['Open', 'Close']].min(axis=1)
    df['Upper_Wick'] = (df['High'] - max_oc) / total_range
    df['Lower_Wick'] = (min_oc - df['Low']) / total_range
    
    conditions = [
        (df['Upper_Wick'] > 0.4),
        (df['Lower_Wick'] > 0.4)
    ]
    df['Wick_Cat'] = np.select(conditions, [0, 1], default=2)
    
    # Token base (0-11) + Tendencia -> Total 24 Tokens únicos
    # Token = Trend * 12 + Base_Token
    base_token = (
        df['Color'].astype(int) * 6 +
        df['Body_Cat'].astype(int) * 3 +
        df['Wick_Cat'].astype(int)
    )
    
    df['Token'] = df['Trend'].astype(int) * 12 + base_token
    df['Fwd_Return_1d'] = df['Close'].pct_change(1).shift(-1)
    
    return df.dropna()

if __name__ == "__main__":
    ticker = "SPY" # Probamos SPY (S&P 500) que tiene más de 20 años de historia limpia
    print(f"Descargando datos históricos para {ticker}...")
    df = obtener_datos(ticker, "2000-01-01", "2026-01-01")
    df = tokenizar_velas(df)
    
    df_export = df[['Token', 'Fwd_Return_1d']]
    df_export.to_csv("tokens_data.csv", index=False)
    print(f"Datos exportados a tokens_data.csv ({len(df_export)} velas procesadas).")