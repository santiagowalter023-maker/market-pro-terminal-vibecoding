#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARKET PRO TERMINAL v3.0 - VERSIÓN HÍBRIDA
Interfaz profesional + Datos simulados + Intento de datos reales
"""

import customtkinter as ctk
from tkinter import ttk
import random
from datetime import datetime, timedelta
import threading
import time
import yfinance as yf

# Colores
COLORS = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_tertiary": "#0f3460",
    "accent_blue": "#1f538d",
    "accent_cyan": "#00b4d8",
    "accent_green": "#00c896",
    "accent_red": "#ff4757",
    "text_primary": "#e8e8e8",
    "text_secondary": "#a0a0a0",
    "text_muted": "#606060",
}

class MarketProHybrid(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("MARKET PRO TERMINAL v3.0")
        self.geometry("1600x900")
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Tickers para monitorear
        self.tickers_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "SPY"]
        
        # Datos con valores por defecto simulados
        self.tickers_data = {
            "AAPL": {"price": 195.50, "change": 2.5, "volume": "52.3M", "high": 198.20, "low": 193.10},
            "MSFT": {"price": 428.75, "change": 1.8, "volume": "18.2M", "high": 431.50, "low": 425.30},
            "GOOGL": {"price": 152.30, "change": -1.2, "volume": "21.5M", "high": 154.80, "low": 150.20},
            "AMZN": {"price": 185.40, "change": 3.1, "volume": "45.2M", "high": 188.90, "low": 182.50},
            "TSLA": {"price": 242.80, "change": -2.3, "volume": "128.5M", "high": 248.20, "low": 239.10},
            "META": {"price": 512.45, "change": 4.2, "volume": "12.8M", "high": 518.75, "low": 508.30},
            "NVDA": {"price": 875.20, "change": 2.9, "volume": "35.7M", "high": 882.40, "low": 868.50},
            "SPY": {"price": 542.30, "change": 1.5, "volume": "89.3M", "high": 545.20, "low": 539.80},
        }
        
        self.use_real_data = False
        self._setup_ui()
        self._start_update_threads()
    
    def _setup_ui(self):
        """Configura interfaz profesional"""
        # ============= HEADER =============
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            title_frame,
            text="📊 MARKET PRO TERMINAL v3.0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Sistema Profesional de Gestión de Activos Financieros",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")
        
        # Botones
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            width=100,
            height=30,
            command=self._manual_refresh
        ).pack(side="left", padx=5)
        
        self.status_btn = ctk.CTkButton(
            btn_frame,
            text="📡 Datos: DEMO",
            width=120,
            height=30,
            fg_color=COLORS["accent_blue"]
        )
        self.status_btn.pack(side="left", padx=5)
        
        # ============= CONTENIDO PRINCIPAL =============
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título de tabla
        ctk.CTkLabel(
            main_frame,
            text="📈 Monitor de Cotizaciones en Tiempo Real",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Tabla
        self._setup_table(main_frame)
        
        # ============= FOOTER =============
        footer = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=40)
        footer.pack(fill="x", padx=0, pady=0)
        footer.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            footer,
            text="🟢 Mercado: ABIERTO | ⏱ Última actualización: --:--:-- | 📈 Tickers: 8",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(padx=20, pady=10, anchor="w")
    
    def _setup_table(self, parent):
        """Configura tabla profesional"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Professional.Treeview",
            background="#1e1e2e",
            foreground="#e8e8e8",
            fieldbackground="#1e1e2e",
            rowheight=32,
            font=("Consolas", 10),
            borderwidth=0,
        )
        style.configure(
            "Professional.Treeview.Heading",
            background="#2a2a4a",
            foreground="#a0a0c0",
            font=("Consolas", 10, "bold"),
            borderwidth=1,
        )
        style.map("Professional.Treeview",
                  background=[("selected", COLORS["accent_blue"])],
                  foreground=[("selected", "white")])
        
        # Columnas
        columns = ("TICKER", "PRECIO", "CAMBIO", "VOLUMEN", "MÁX", "MÍN")
        
        # Frame para tabla y scrollbar
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_tertiary"], corner_radius=8)
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Professional.Treeview",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            height=20
        )
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("TICKER", text="TICKER")
        self.tree.heading("PRECIO", text="PRECIO")
        self.tree.heading("CAMBIO", text="CAMBIO %")
        self.tree.heading("VOLUMEN", text="VOLUMEN")
        self.tree.heading("MÁX", text="MÁX")
        self.tree.heading("MÍN", text="MÍN")
        
        self.tree.column("TICKER", width=80, anchor="center")
        self.tree.column("PRECIO", width=110, anchor="e")
        self.tree.column("CAMBIO", width=110, anchor="e")
        self.tree.column("VOLUMEN", width=120, anchor="e")
        self.tree.column("MÁX", width=110, anchor="e")
        self.tree.column("MÍN", width=110, anchor="e")
        
        # Tags de colores
        self.tree.tag_configure("up", foreground=COLORS["accent_green"], background="#1e1e2e")
        self.tree.tag_configure("down", foreground=COLORS["accent_red"], background="#1e1e2e")
        self.tree.tag_configure("neutral", foreground=COLORS["text_secondary"], background="#1e1e2e")
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self._update_table()
    
    def _update_table(self):
        """Actualiza tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for ticker in self.tickers_list:
            if ticker in self.tickers_data:
                data = self.tickers_data[ticker]
                change = data["change"]
                tag = "up" if change > 0 else ("down" if change < 0 else "neutral")
                
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        ticker,
                        f"${data['price']:.2f}",
                        f"{change:+.2f}%",
                        data["volume"],
                        f"${data['high']:.2f}",
                        f"${data['low']:.2f}"
                    ),
                    tags=(tag,)
                )
    
    def _fetch_real_data(self):
        """Intenta obtener datos reales del último día de mercado (históricos)"""
        try:
            for ticker in self.tickers_list:
                try:
                    # Obtener últimos 5 días (para conseguir el viernes pasado)
                    data = yf.Ticker(ticker)
                    hist = data.history(period="5d")
                    
                    if len(hist) > 0:
                        # Usar el último día disponible (viernes)
                        price = hist['Close'].iloc[-1]
                        high = hist['High'].iloc[-1]
                        low = hist['Low'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        # Calcular cambio desde hace 2 días
                        if len(hist) > 1:
                            prev_close = hist['Close'].iloc[-2]
                            change_pct = ((price - prev_close) / prev_close) * 100
                        else:
                            change_pct = 0
                        
                        self.tickers_data[ticker] = {
                            "price": float(price),
                            "change": float(change_pct),
                            "volume": f"{volume/1e6:.1f}M",
                            "high": float(high),
                            "low": float(low)
                        }
                        
                        self.use_real_data = True
                        self.status_btn.configure(text="📡 Datos: HISTÓRICOS (Viernes)", fg_color=COLORS["accent_green"])
                        
                except Exception as e:
                    # Si falla, continúa con datos simulados
                    pass
                
                time.sleep(0.5)  # Delay entre requests
        
        except Exception as e:
            pass
    
    def _manual_refresh(self):
        """Refresco manual"""
        self._simulate_price_change()
        self._update_table()
    
    def _simulate_price_change(self):
        """Simula cambios de precio"""
        for ticker in self.tickers_data:
            change_factor = random.uniform(0.995, 1.005)
            self.tickers_data[ticker]["price"] *= change_factor
            self.tickers_data[ticker]["change"] = random.uniform(-5, 5)
            self.tickers_data[ticker]["high"] *= random.uniform(1.0, 1.01)
            self.tickers_data[ticker]["low"] *= random.uniform(0.99, 1.0)
    
    def _start_update_threads(self):
        """Inicia threads de actualización"""
        # Thread 1: Intentar datos reales una sola vez
        def fetch_thread():
            time.sleep(2)  # Esperar a que UI esté lista
            self._fetch_real_data()
        
        # Thread 2: Actualizar UI cada 2-3 segundos
        def update_thread():
            while True:
                self._simulate_price_change()
                self._update_table()
                
                now = datetime.now().strftime("%H:%M:%S")
                self.status_label.configure(
                    text=f"🟢 Mercado: ABIERTO | ⏱ Última act.: {now} | 📈 Tickers: {len(self.tickers_list)}"
                )
                
                time.sleep(2.5)
        
        t1 = threading.Thread(target=fetch_thread, daemon=True)
        t2 = threading.Thread(target=update_thread, daemon=True)
        
        t1.start()
        t2.start()


if __name__ == "__main__":
    app = MarketProHybrid()
    app.mainloop()
