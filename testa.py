import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import yfinance as yf
import threading
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import time
import logging
import csv

# --- CONFIGURACIÓN DE LOGS ---
logging.basicConfig(
    filename='market_pro.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'market_terminal.log'),
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("MarketPro")

# =================================================================
# CAPA DE DATOS: SQLITE & SIMULACIÓN
# =================================================================
class DatabaseController:
    """Maneja la persistencia y simula una base de datos de alta disponibilidad."""
    def __init__(self, db_name="market_enterprise_v2.db"):
        self.db_name = db_name
        self._initialize_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def _initialize_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabla de historial real
            cursor.execute('''CREATE TABLE IF NOT EXISTS asset_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                price REAL,
                pct_change REAL,
                volume INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            # Tabla de configuración de usuario
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )''')
            conn.commit()

    def log_market_data(self, ticker, price, change, vol):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO asset_history (ticker, price, pct_change, volume) VALUES (?, ?, ?, ?)",
                    (ticker, price, change, vol)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error en DB: {e}")

    def get_last_records(self, ticker, limit=10):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, timestamp FROM asset_history WHERE ticker = ? ORDER BY id DESC LIMIT ?", (ticker, limit))
            return cursor.fetchall()

# =================================================================
# CAPA DE LÓGICA: ANALYTICS & ENGINE
# =================================================================
class TechnicalAnalysis:
    """Simula cálculos de indicadores técnicos avanzados."""
    @staticmethod
    def calculate_rsi(prices, period=14):
        if len(prices) < period: return 50.0
        # Simulación de cálculo RSI profesional
        return round(random.uniform(30.0, 70.0), 2)

    @staticmethod
    def get_moving_average(prices, window=5):
        if len(prices) < window: return sum(prices)/len(prices) if prices else 0
        return sum(prices[-window:]) / window

class MarketDataEngine:
    """Motor de adquisición de datos con manejo de rate-limiting."""
    def __init__(self):
        self.session = yf.shared_utils.requests.Session()
    
    def fetch_comprehensive_data(self, ticker):
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(period="5d", interval="1h")
            if df.empty: return None
            
            info = asset.info
            current = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change = ((current - prev_close) / prev_close) * 100
            
            return {
                "symbol": ticker,
                "price": round(current, 2),
                "change": round(change, 2),
                "high": round(df['High'].max(), 2),
                "low": round(df['Low'].min(), 2),
                "vol": info.get('volume', 0),
                "history": df['Close'].tolist(),
                "name": info.get('longName', ticker)
            }
        except Exception as e:
            logger.warning(f"Engine Fallo en {ticker}: {e}")
            return None

# =================================================================
# INTERFAZ GRÁFICA (GUI): CUSTOMTKINTER PRO
# =================================================================
class MarketApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de Ventana
        self.title("QUANT-CORE TERMINAL | v2.5.0")
        self.geometry("1500x900")
        
        # Inicialización de servicios
        self.db = DatabaseController()
        self.engine = MarketDataEngine()
        self.analytics = TechnicalAnalysis()
        
        # Estado de la aplicación
        self.watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "MELI", "BTC-USD"]
        self.data_cache = {}
        self.active_ticker = "AAPL"
        
        self._build_ui()
        self._start_services()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # PANEL LATERAL (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="QUANT-CORE", font=("Orbitron", 24, "bold")).pack(pady=30)
        
        # Search & Add
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Añadir Ticker...")
        self.search_entry.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="+ Agregar", command=self.add_asset).pack(pady=5, padx=20, fill="x")

        # News/Logs Section
        self.log_box = ctk.CTkTextbox(self.sidebar, height=300, font=("Consolas", 10))
        self.log_box.pack(pady=20, padx=20, fill="both")
        self.log_box.insert("0.0", "> Sistema iniciado...\n> Cargando base de datos...")

        # PANEL PRINCIPAL
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Header con Indicadores Rápidos
        self.header = ctk.CTkFrame(self.content, height=120)
        self.header.pack(fill="x", pady=(0, 20))
        
        self.price_label = ctk.CTkLabel(self.header, text="$ 0.00", font=("Roboto", 44, "bold"))
        self.price_label.pack(side="left", padx=30)
        
        self.info_panel = ctk.CTkLabel(self.header, text="SELECCIONE UN ACTIVO", font=("Roboto", 14))
        self.info_panel.pack(side="right", padx=30)

        # Middle Section (Graph + Watchlist)
        self.mid_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.mid_frame.pack(fill="both", expand=True)

        self.setup_table()
        self.setup_visuals()

    def setup_table(self):
        # Tabla de Mercado (Treeview)
        t_frame = ctk.CTkFrame(self.mid_frame)
        t_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        columns = ("S", "P", "C", "V")
        self.tree = ttk.Treeview(t_frame, columns=columns, show="headings")
        self.tree.heading("S", text="Símbolo")
        self.tree.heading("P", text="Precio")
        self.tree.heading("C", text="Cambio %")
        self.tree.heading("V", text="Volumen")
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_ticker_select)

    def setup_visuals(self):
        self.graph_container = ctk.CTkFrame(self.mid_frame, width=600)
        self.graph_container.pack(side="right", fill="both", expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax.set_facecolor('#1a1a1a')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # LÓGICA DE NEGOCIO
    def add_asset(self):
        tkr = self.search_entry.get().upper()
        if tkr and tkr not in self.watchlist:
            self.watchlist.append(tkr)
            self.write_log(f"Ticker {tkr} monitoreado.")

    def write_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"\n[{ts}] {msg}")
        self.log_box.see("end")

    def on_ticker_select(self, event):
        selected = self.tree.focus()
        if selected:
            vals = self.tree.item(selected)['values']
            self.active_ticker = vals[0]
            self.update_main_view()

    def update_main_view(self):
        if self.active_ticker in self.data_cache:
            d = self.data_cache[self.active_ticker]
            self.price_label.configure(text=f"$ {d['price']}", text_color="green" if d['change'] >= 0 else "red")
            self.info_panel.configure(text=f"Nombre: {d['name']}\nMax: {d['high']} | Min: {d['low']}")
            
            # Gráfico de tendencia
            self.ax.clear()
            self.ax.plot(d['history'], color='#1f538d', linewidth=2)
            self.ax.fill_between(range(len(d['history'])), d['history'], color='#1f538d', alpha=0.2)
            self.ax.set_title(f"Trend: {self.active_ticker}", color="white")
            self.canvas.draw()

    def _worker_thread(self):
        while True:
            for t in self.watchlist:
                raw = self.engine.fetch_comprehensive_data(t)
                if raw:
                    self.data_cache[t] = raw
                    self.db.log_market_data(t, raw['price'], raw['change'], raw['vol'])
            
            self.after(0, self.refresh_ui)
            time.sleep(15)

    def refresh_ui(self):
        # Limpiar y recargar tabla
        for item in self.tree.get_children(): self.tree.delete(item)
        for t, d in self.data_cache.items():
            self.tree.insert("", "end", values=(t, d['price'], f"{d['change']}%", d['vol']))
        self.update_main_view()

    def _start_services(self):
        t = threading.Thread(target=self._worker_thread, daemon=True)
        t.start()
        self.write_log("Servicios de red activos.")

if __name__ == "__main__":
    app = MarketApp()
    app.mainloop()
# --- CONFIGURACIÓN VISUAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DatabaseManager:
    """Clase encargada de la persistencia de datos (SQL)"""
    def __init__(self, db_name="market_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                precio REAL,
                cambio REAL,
                fecha TEXT
            )
        ''')
        self.conn.commit()

    def guardar_registro(self, ticker, precio, cambio):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO historial (ticker, precio, cambio, fecha) VALUES (?, ?, ?, ?)",
            (ticker, precio, cambio, fecha)
        )
        self.conn.commit()

class MarketEngine:
    """Motor de obtención de datos financieros"""
    @staticmethod
    def fetch_data(ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="1m")
            if hist.empty: return None
            
            info = stock.info
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            pct_change = ((current_price - open_price) / open_price) * 100
            
            return {
                "symbol": ticker,
                "price": round(current_price, 2),
                "change": round(pct_change, 2),
                "high": round(hist['High'].max(), 2),
                "low": round(hist['Low'].min(), 2),
                "volume": info.get('volume', 0),
                "currency": info.get('currency', 'USD')
            }
        except Exception as e:
            logging.error(f"Error obteniendo {ticker}: {e}")
            return None

class ProfessionalTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración Ventana Principal
        self.title("MARKET PRO TERMINAL v2.0 - Sistema de Gestión de Activos")
        self.geometry("1400x850")
        
        # Inicializar Componentes Core
        self.db = DatabaseManager()
        self.engine = MarketEngine()
        self.tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD", "ETH-USD"]
        self.market_cache = {}
        self.is_running = True
        
        # UI Layout
        self.setup_ui()
        
        # Threads
        self.start_background_tasks()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_nav = ctk.CTkLabel(self.sidebar, text="NAVEGACIÓN", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_nav.pack(pady=(20, 10))

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard Real-Time", command=self.show_dashboard)
        self.btn_dashboard.pack(pady=5, padx=20)

        self.btn_stats = ctk.CTkButton(self.sidebar, text="Exportar Datos", fg_color="gray25", command=self.export_data)
        self.btn_stats.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="GESTIÓN DE TICKERS").pack(pady=(30, 5))
        self.entry_ticker = ctk.CTkEntry(self.sidebar, placeholder_text="Ej: NVDA")
        self.entry_ticker.pack(pady=5, padx=20)
        
        self.btn_add = ctk.CTkButton(self.sidebar, text="Añadir Activo", command=self.add_ticker)
        self.btn_add.pack(pady=5, padx=20)

        # --- MAIN AREA ---
        self.main_container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Top Stats Cards
        self.cards_frame = ctk.CTkFrame(self.main_container, height=100, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 20))
        
        self.card_market_status = self.create_card(self.cards_frame, "ESTADO MERCADO", "ABIERTO", "green")
        self.card_top_gain = self.create_card(self.cards_frame, "TOP GAIN", "--", "white")

        # Table Section
        self.table_label = ctk.CTkLabel(self.main_container, text="Monitor de Cotizaciones Globales", font=ctk.CTkFont(size=20, weight="bold"))
        self.table_label.pack(anchor="w", padx=10)

        self.setup_treeview()

        # Graph Section
        self.graph_frame = ctk.CTkFrame(self.main_container, height=300)
        self.graph_frame.pack(fill="both", expand=True, pady=10)
        self.setup_chart()

    def create_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, width=200, height=80)
        card.pack(side="left", padx=10, fill="both", expand=True)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12)).pack(pady=5)
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=color)
        lbl_val.pack(pady=2)
        return lbl_val

    def setup_treeview(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=35, font=('Segoe UI', 10))
        
        self.tree = ttk.Treeview(self.main_container, columns=("T", "P", "C", "H", "L", "V"), show="headings")
        headers = ["Ticker", "Precio", "Cambio %", "Máximo", "Mínimo", "Volumen"]
        for i, h in enumerate(headers):
            self.tree.heading(f"#{i+1}", text=h)
            self.tree.column(f"#{i+1}", anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_chart(self):
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_ticker(self):
        t = self.entry_ticker.get().upper().strip()
        if t and t not in self.tickers:
            self.tickers.append(t)
            self.entry_ticker.delete(0, tk.END)
            logging.info(f"Ticker agregado: {t}")

    def update_ui_elements(self):
        # Actualizar Tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        max_gain = -999
        top_symbol = "N/A"

        for sym, d in self.market_cache.items():
            tag = "up" if d['change'] >= 0 else "down"
            self.tree.insert("", tk.END, values=(
                sym, f"{d['price']} {d['currency']}", f"{d['change']}%", 
                d['high'], d['low'], d['volume']
            ))
            if d['change'] > max_gain:
                max_gain = d['change']
                top_symbol = sym

        self.card_top_gain.configure(text=f"{top_symbol} (+{max_gain}%)")
        self.refresh_chart()

    def refresh_chart(self):
        self.ax.clear()
        if self.market_cache:
            symbols = list(self.market_cache.keys())[:5]
            prices = [self.market_cache[s]['price'] for s in symbols]
            self.ax.bar(symbols, prices, color='#1f538d')
            self.ax.set_title("Comparativa de Precios (Principales)", color="white")
        self.canvas.draw()

    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Ticker", "Precio", "Cambio", "Fecha"])
                self.db.cursor.execute("SELECT ticker, precio, cambio, fecha FROM historial")
                writer.writerows(self.db.cursor.fetchall())
            messagebox.showinfo("Éxito", "Datos exportados correctamente.")

    def background_loop(self):
        while self.is_running:
            for ticker in self.tickers:
                data = self.engine.fetch_data(ticker)
                if data:
                    self.market_cache[ticker] = data
                    self.db.guardar_registro(ticker, data['price'], data['change'])
            
            self.after(0, self.update_ui_elements)
            time.sleep(30) # Actualización cada 30 segundos

    def start_background_tasks(self):
        t = threading.Thread(target=self.background_loop, daemon=True)
        t.start()

    def show_dashboard(self):
        messagebox.showinfo("Market Pro", "Ya te encuentras en el Dashboard Principal.")

if __name__ == "__main__":
    app = ProfessionalTerminal()
    app.mainloop()