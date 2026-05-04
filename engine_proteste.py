import yfinance as yf
import sqlite3
import pandas as pd
import logging
import queue
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class FinancialEnginePro:
    def __init__(self, db_name="market_enterprise_v4.db", max_workers=5):
        self.db_name = db_name
        self.max_workers = max_workers
        self.cache = {}  # Memoria volátil para UI rápida
        self.write_queue = queue.Queue() # Cola para no bloquear la API con la DB
        
        self._init_db()
        self._start_background_worker()
        logging.info("Motor Pro activado con sistema de colas asíncronas.")

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS prices 
                         (ticker TEXT, price REAL, change REAL, vol INTEGER, timestamp DATETIME)''')
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ticker_ts ON prices (ticker, timestamp)")

    def _start_background_worker(self):
        """Hilo dedicado exclusivamente a escribir en la base de datos."""
        def worker():
            while True:
                data = self.write_queue.get()
                if data is None: break
                try:
                    with self._get_connection() as conn:
                        conn.execute(
                            "INSERT INTO prices VALUES (?, ?, ?, ?, ?)",
                            (data['ticker'], data['price'], data['change'], data['vol'], datetime.now())
                        )
                        conn.commit()
                except Exception as e:
                    logging.error(f"Error en Worker de DB: {e}")
                self.write_queue.task_done()

        threading.Thread(target=worker, daemon=True).start()

    def _fetch_single_ticker(self, ticker):
        """Lógica de extracción individual optimizada."""
        try:
            t = yf.Ticker(ticker)
            # Intentamos fast_info primero (baja latencia)
            info = t.fast_info
            
            price = info['last_price']
            prev_close = info['previous_close']
            change = ((price - prev_close) / prev_close) * 100
            
            result = {
                "ticker": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "high": round(info['day_high'], 2),
                "low": round(info['day_low'], 2),
                "vol": int(info['last_volume']),
                "status": "OK"
            }
            
            # Actualizar caché y encolar para persistencia
            self.cache[ticker] = result
            self.write_queue.put(result)
            return result
        except Exception as e:
            return {"ticker": ticker, "status": f"Error: {str(e)}"}

    def update_portfolio(self, tickers):
        """Consulta múltiples activos en paralelo."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self._fetch_single_ticker, tickers))
        return results

    def get_moving_average(self, ticker, window=5):
        """Calcula la Media Móvil Simple (SMA) desde la base de datos."""
        try:
            with self._get_connection() as conn:
                query = f"""SELECT price FROM prices WHERE ticker = ? 
                           ORDER BY timestamp DESC LIMIT {window}"""
                df = pd.read_sql_query(query, conn, params=(ticker,))
                if len(df) < window: return None
                return round(df['price'].mean(), 2)
        except Exception as e:
            logging.error(f"Error calculando SMA: {e}")
            return None

    def get_performance_summary(self):
        """Genera un resumen de la sesión actual."""
        if not self.cache: return "No hay datos en caché."
        
        df = pd.DataFrame(self.cache.values())
        resumen = {
            "Top Gainer": df.loc[df['change'].idxmax()]['ticker'],
            "Top Loser": df.loc[df['change'].idxmin()]['ticker'],
            "Volumen Total": df['vol'].sum(),
            "Promedio Precio": df['price'].mean()
        }
        return resumen

    def shutdown(self):
        """Cierre limpio del sistema."""
        self.write_queue.put(None)
        logging.info("Sistema apagado y colas procesadas.")