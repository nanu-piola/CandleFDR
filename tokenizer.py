import pandas as pd
import numpy as np

# Umbrales fijos y determinísticos
BODY_THRESHOLD = 0.50
WICK_THRESHOLD = 0.40

def tokenizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. SMA 50 (Filtro de Tendencia)
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Eliminamos las primeras filas sin SMA para evitar señales falsas
    df = df.dropna(subset=['SMA_50']).copy()
    
    df['Trend'] = np.where(df['Close'] > df['SMA_50'], 1, 0)
    df['Color'] = np.where(df['Close'] >= df['Open'], 1, 0)
    
    # 2. Tamaño de Cuerpo
    df['Body'] = (df['Close'] - df['Open']).abs()
    total_range = (df['High'] - df['Low']).replace(0, np.nan)
    df['Body_Rel'] = df['Body'] / total_range
    df['Body_Cat'] = np.where(df['Body_Rel'] > BODY_THRESHOLD, 1, 0)
    
    # 3. Mechas
    max_oc = df[['Open', 'Close']].max(axis=1)
    min_oc = df[['Open', 'Close']].min(axis=1)
    df['Upper_Wick'] = (df['High'] - max_oc) / total_range
    df['Lower_Wick'] = (min_oc - df['Low']) / total_range
    
    conditions = [
        (df['Upper_Wick'] > WICK_THRESHOLD),
        (df['Lower_Wick'] > WICK_THRESHOLD)
    ]
    df['Wick_Cat'] = np.select(conditions, [0, 1], default=2)
    
    # 4. Tokenización (0 a 23)
    base_token = (
        df['Color'].astype(int) * 6 +
        df['Body_Cat'].astype(int) * 3 +
        df['Wick_Cat'].astype(int)
    )
    df['Token'] = df['Trend'].astype(int) * 12 + base_token
    
    # 5. Retorno ejecutable: Compra al OPEN de T+1 y salida al CLOSE de T+1
    df['Exec_Return'] = (df['Close'].shift(-1) / df['Open'].shift(-1)) - 1.0
    
    return df