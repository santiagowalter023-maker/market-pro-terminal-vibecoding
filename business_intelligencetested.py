import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class BusinessIntelligence:
    def __init__(self, db_name="market_enterprise_v3.db"):
        self.db_name = db_name

    def get_market_performance_report(self):
        """
        Usa SQL avanzado para calcular el rendimiento por activo 
        comparando el primer precio registrado vs el último.
        """
        query = """
            WITH FirstLastPrices AS (
                SELECT 
                    ticker,
                    price,
                    timestamp,
                    ROW_NUMBER() OVER(PARTITION BY ticker ORDER BY timestamp ASC) as rank_asc,
                    ROW_NUMBER() OVER(PARTITION BY ticker ORDER BY timestamp DESC) as rank_desc
                FROM transactions
            )
            SELECT 
                f.ticker,
                f.price as price_start,
                l.price as price_end,
                round(((l.price - f.price) / f.price) * 100, 4) as net_yield_percentage
            FROM FirstLastPrices f
            JOIN FirstLastPrices l ON f.ticker = l.ticker
            WHERE f.rank_asc = 1 AND l.rank_desc = 1
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            return f"Error en reporte SQL: {e}"

    def get_peak_volatility_hours(self):
        """
        Identifica en qué horas del día hay más fluctuación de precios 
        usando funciones de agregación SQL.
        """
        query = """
            SELECT 
                strftime('%H', timestamp) as hour,
                count(*) as update_frequency,
                avg(price) as average_price,
                (max(price) - min(price)) as price_spread
            FROM transactions
            GROUP BY hour
            ORDER BY price_spread DESC
        """
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql_query(query, conn)

    def detect_anomalies(self, threshold=5.0):
        """
        Detecta saltos de precio inusuales (gaps) que superen un % definido.
        Ideal para auditoría de mercado.
        """
        query = f"""
            SELECT ticker, price, timestamp
            FROM (
                SELECT ticker, price, timestamp,
                       LAG(price) OVER (PARTITION BY ticker ORDER BY timestamp) as prev_price
                FROM transactions
            )
            WHERE abs((price - prev_price) / prev_price) * 100 > {threshold}
        """
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql_query(query, conn)