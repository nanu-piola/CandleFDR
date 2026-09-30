import pandas as pd
import numpy as np
import yfinance as yf

# Patrones ganadores validados por el Engine C++ (FDR Pass = SÍ para SPY)
PATRONES_GANADORES = {
    (14, 17): "COMPRA (Pullback en Tendencia Alcista)",
    (0, 23): "COMPRA (Breakout / Ruptura de SMA 50)"
}

def tokenizar_ultima_secuencia(ticker: str) -> None:
    print(f"Analizando últimas velas de {ticker}...\n")
    # Usamos '3mo' en lugar de '3m'
    df = yf.download(ticker, period="3mo", interval="1d")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df[['Open', 'High', 'Low', 'Close']].dropna()

    # 1. Filtro de Tendencia (SMA 50)
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['Trend'] = np.where(df['Close'] > df['SMA_50'], 1, 0)
    
    # 2. Color
    df['Color'] = np.where(df['Close'] >= df['Open'], 1, 0)
    
    # 3. Tamaño de Cuerpo
    df['Body'] = (df['Close'] - df['Open']).abs()
    total_range = (df['High'] - df['Low']).replace(0, np.nan)
    df['Body_Rel'] = df['Body'] / total_range
    df['Body_Cat'] = np.where(df['Body_Rel'] > 0.50, 1, 0)
    
    # 4. Mechas
    max_oc = df[['Open', 'Close']].max(axis=1)
    min_oc = df[['Open', 'Close']].min(axis=1)
    df['Upper_Wick'] = (df['High'] - max_oc) / total_range
    df['Lower_Wick'] = (min_oc - df['Low']) / total_range
    
    conditions = [(df['Upper_Wick'] > 0.4), (df['Lower_Wick'] > 0.4)]
    df['Wick_Cat'] = np.select(conditions, [0, 1], default=2)
    
    # Token
    base_token = (df['Color'].astype(int) * 6 + df['Body_Cat'].astype(int) * 3 + df['Wick_Cat'].astype(int))
    df['Token'] = df['Trend'].astype(int) * 12 + base_token
    
    # Fix: tomamos los últimos 2 registros limpios
    df_ultimos = df.tail(2)
    ultimos_tokens = df_ultimos['Token'].tolist()
    fechas = df_ultimos.index.strftime('%Y-%m-%d').tolist()
    
    token_anteayer, token_ayer = ultimos_tokens[0], ultimos_tokens[1]
    par_actual = (token_anteayer, token_ayer)
    
    print(f"Vela {fechas[0]}: Token {token_anteayer}")
    print(f"Vela {fechas[1]}: Token {token_ayer}")
    print(f"Secuencia actual detectada: {token_anteayer}-{token_ayer}\n")
    
    # Generador de señal
    if par_actual in PATRONES_GANADORES:
        accion = PATRONES_GANADORES[par_actual]
        print(f"🚨 ¡SEÑAL DETECTADA! -> {accion}")
        print("💡 Ejecutar orden al CIERRE de hoy para mantener 1 día.")
    else:
        print("🟢 Estado: NEUTRO / SIN SEÑAL")
        print("No hay ningún patrón cuantitativo válido presente al cierre de hoy.")

if __name__ == "__main__":
    tokenizar_ultima_secuencia("SPY")