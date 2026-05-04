import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import logging

class MarketAnalytics:
    def __init__(self, db_name="market_enterprise_v3.db"):
        self.db_name = db_name
        self.logger = logging.getLogger("AnalyticsEngine")

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def fetch_historical_data(self, ticker, minutes=60):
        """Extrae datos de la base de datos local para analizar."""
        query = """
            SELECT price, timestamp FROM transactions 
            WHERE ticker = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """
        limit_time = datetime.now() - timedelta(minutes=minutes)
        with self._get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(ticker, limit_time))

    def calculate_indicators(self, ticker):
        """Calcula indicadores técnicos avanzados sobre los datos de SQL."""
        df = self.fetch_historical_data(ticker)
        
        if len(df) < 5:
            return {"status": "Insuvicient Data", "signal": "WAIT"}

        # Cálculo de Media Móvil Simple (SMA)
        df['SMA_5'] = df['price'].rolling(window=5).mean()
        
        # Cálculo de Volatilidad (Desviación Estándar)
        volatility = df['price'].std()
        
        last_price = df['price'].iloc[-1]
        last_sma = df['SMA_5'].iloc[-1]

        # Lógica de señales (Cruce de medias simple)
        if last_price > last_sma:
            signal = "BUY (Alcista)"
        elif last_price < last_sma:
            signal = "SELL (Bajista)"
        else:
            signal = "NEUTRAL"

        return {
            "ticker": ticker,
            "last_price": round(last_price, 2),
            "sma": round(last_sma, 2) if not np.isnan(last_sma) else 0,
            "volatility": round(volatility, 4) if not np.isnan(volatility) else 0,
            "signal": signal,
            "data_points": len(df)
        }

    def generate_prediction(self, ticker):
        """
        Simula un modelo de predicción basado en la tendencia actual.
        En un entorno real, aquí integraríamos Scikit-Learn o TensorFlow.
        """
        indicators = self.calculate_indicators(ticker)
        if indicators.get("signal") == "WAIT":
            return "Analizando mercado..."

        # Simulación de tendencia futura (Monte Carlo simplificado)
        current = indicators['last_price']
        change_random = np.random.normal(0, indicators['volatility'] + 0.01)
        prediction = current + (current * change_random)
        
        return {
            "current": current,
            "target_24h": round(prediction, 2),
            "confidence": "65% (Simulado)"
        }