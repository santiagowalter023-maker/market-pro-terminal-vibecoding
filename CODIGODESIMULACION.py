#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MARKET PRO TERMINAL v3.0 - CON GRÁFICO DE PROYECCIÓN
Incluye predicción técnica y gráficos en tiempo real
"""

import customtkinter as ctk
from tkinter import ttk
import random
from datetime import datetime, timedelta
import threading
import time
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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

class MarketProWithCharts(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("MARKET PRO TERMINAL v3.0 - CON PROYECCIONES")
        self.geometry("1900x1000")
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
        
        # Histórico de precios para gráficos
        self.price_history = {ticker: [] for ticker in self.tickers_list}
        self.dates_history = []
        
        self.selected_ticker = "AAPL"
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
            text="📊 MARKET PRO TERMINAL v3.0 - CON PROYECCIONES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Sistema Profesional con Gráficos en Tiempo Real y Proyecciones Técnicas",
            font=ctk.CTkFont(size=9),
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
        
        # ===== LADO IZQUIERDO (TABLA) =====
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.configure(width=450)
        
        ctk.CTkLabel(
            left_frame,
            text="📈 Monitor de Cotizaciones",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))
        
        self._setup_table(left_frame)
        
        # ===== LADO DERECHO (GRÁFICOS) =====
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Selector de ticker
        selector_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        selector_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            selector_frame,
            text="📊 Gráfico de Proyección:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        self.ticker_combo = ctk.CTkComboBox(
            selector_frame,
            values=self.tickers_list,
            command=self._on_ticker_select,
            width=150
        )
        self.ticker_combo.set("AAPL")
        self.ticker_combo.pack(side="left")
        
        # Frame para gráficos
        self.chart_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["bg_tertiary"], corner_radius=8)
        self.chart_frame.pack(fill="both", expand=True)
        
        # Canvas para matplotlib
        self.fig = Figure(figsize=(8, 5), dpi=100, facecolor=COLORS["bg_primary"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS["bg_tertiary"])
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
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
            rowheight=28,
            font=("Consolas", 9),
            borderwidth=0,
        )
        style.configure(
            "Professional.Treeview.Heading",
            background="#2a2a4a",
            foreground="#a0a0c0",
            font=("Consolas", 9, "bold"),
        )
        style.map("Professional.Treeview",
                  background=[("selected", COLORS["accent_blue"])],
                  foreground=[("selected", "white")])
        
        columns = ("TICKER", "PRECIO", "CAMBIO", "VOLUMEN")
        
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_tertiary"], corner_radius=8)
        table_frame.pack(fill="both", expand=True)
        
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Professional.Treeview",
            yscrollcommand=v_scroll.set,
            height=15
        )
        
        v_scroll.config(command=self.tree.yview)
        
        self.tree.heading("TICKER", text="TICKER")
        self.tree.heading("PRECIO", text="PRECIO")
        self.tree.heading("CAMBIO", text="CAMBIO %")
        self.tree.heading("VOLUMEN", text="VOLUMEN")
        
        self.tree.column("TICKER", width=70, anchor="center")
        self.tree.column("PRECIO", width=100, anchor="e")
        self.tree.column("CAMBIO", width=90, anchor="e")
        self.tree.column("VOLUMEN", width=90, anchor="e")
        
        self.tree.tag_configure("up", foreground=COLORS["accent_green"], background="#1e1e2e")
        self.tree.tag_configure("down", foreground=COLORS["accent_red"], background="#1e1e2e")
        self.tree.tag_configure("neutral", foreground=COLORS["text_secondary"], background="#1e1e2e")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
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
                        data["volume"]
                    ),
                    tags=(tag,)
                )
    
    def _on_ticker_select(self, choice):
        """Cuando se selecciona un ticker"""
        self.selected_ticker = choice
        self._update_chart()
    
    def _update_chart(self):
        """Actualiza el gráfico con proyección"""
        ticker = self.selected_ticker
        
        if ticker not in self.price_history or len(self.price_history[ticker]) < 5:
            return
        
        prices = np.array(self.price_history[ticker])
        
        # Limpiar gráfico
        self.ax.clear()
        
        # Datos históricos
        x = np.arange(len(prices))
        self.ax.plot(x, prices, 'o-', color=COLORS["accent_cyan"], linewidth=2.5, 
                    markersize=6, label="Precio Histórico")
        
        # ===== PROYECCIÓN LINEAR =====
        z = np.polyfit(x, prices, 1)
        p = np.poly1d(z)
        x_future = np.arange(len(prices) + 10)
        y_future = p(x_future)
        
        self.ax.plot(x_future[len(prices)-1:], y_future[len(prices)-1:], 
                    '--', color=COLORS["accent_green"], linewidth=2, label="Proyección Linear", alpha=0.8)
        
        # ===== PROYECCIÓN CON POLINOMIO (Más realista) =====
        z2 = np.polyfit(x, prices, 2)
        p2 = np.poly1d(z2)
        y_future2 = p2(x_future)
        
        self.ax.plot(x_future[len(prices)-1:], y_future2[len(prices)-1:], 
                    ':', color=COLORS["accent_red"], linewidth=2.5, label="Proyección Cuadrática", alpha=0.8)
        
        # ===== PROYECCIÓN CON MEDIA MÓVIL =====
        if len(prices) >= 3:
            ma = np.convolve(prices, np.ones(3)/3, mode='valid')
            self.ax.fill_between(x[:len(ma)], ma-5, ma+5, alpha=0.2, color=COLORS["accent_blue"], 
                                label="Banda de volatilidad")
        
        # Configurar gráfico
        self.ax.set_facecolor(COLORS["bg_tertiary"])
        self.ax.grid(True, alpha=0.2, color=COLORS["text_secondary"])
        self.ax.legend(loc="best", facecolor=COLORS["bg_secondary"], edgecolor=COLORS["border"], 
                      labelcolor=COLORS["text_primary"], fontsize=9)
        
        # Títulos y etiquetas
        self.ax.set_title(f"📈 Proyección de {ticker}", fontsize=14, weight="bold", 
                         color=COLORS["text_primary"], pad=15)
        self.ax.set_xlabel("Tiempo (períodos)", fontsize=10, color=COLORS["text_secondary"])
        self.ax.set_ylabel("Precio USD ($)", fontsize=10, color=COLORS["text_secondary"])
        
        # Colorear los ejes
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["text_secondary"])
            spine.set_alpha(0.3)
        self.ax.tick_params(colors=COLORS["text_secondary"])
        
        # Dibujar
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _simulate_price_change(self):
        """Simula cambios de precio"""
        for ticker in self.tickers_data:
            change_factor = random.uniform(0.98, 1.02)
            self.tickers_data[ticker]["price"] *= change_factor
            self.tickers_data[ticker]["change"] = random.uniform(-5, 5)
            self.tickers_data[ticker]["high"] *= random.uniform(1.0, 1.01)
            self.tickers_data[ticker]["low"] *= random.uniform(0.99, 1.0)
            
            # Agregar al histórico
            self.price_history[ticker].append(self.tickers_data[ticker]["price"])
            if len(self.price_history[ticker]) > 50:
                self.price_history[ticker].pop(0)
    
    def _manual_refresh(self):
        """Refresco manual"""
        self._simulate_price_change()
        self._update_table()
        self._update_chart()
    
    def _start_update_threads(self):
        """Inicia threads de actualización"""
        def update_thread():
            counter = 0
            while True:
                self._simulate_price_change()
                self._update_table()
                
                # Actualizar gráfico cada 3 ciclos
                if counter % 3 == 0:
                    self._update_chart()
                counter += 1
                
                now = datetime.now().strftime("%H:%M:%S")
                self.status_label.configure(
                    text=f"🟢 Mercado: ABIERTO | ⏱ Última act.: {now} | 📈 Tickers: {len(self.tickers_list)}"
                )
                
                time.sleep(1.5)
        
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()


if __name__ == "__main__":
    app = MarketProWithCharts()
    app.mainloop()
