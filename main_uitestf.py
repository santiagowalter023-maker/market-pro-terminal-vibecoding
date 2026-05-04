import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from engine_pro import FinancialEngine # Importamos nuestro otro archivo
# En main_ui.py
from business_intelligence import BusinessIntelligence

# Dentro de __init__
self.bi_engine = BusinessIntelligence()

# En setup_ui, añadimos un botón de reporte
self.btn_report = ctk.CTkButton(self.side, text="Generar Reporte KPI", 
                                command=self.show_business_report,
                                fg_color="#2E7D32") # Verde empresarial
self.btn_report.pack(pady=10, padx=20)

def show_business_report(self):
    report_data = self.bi_engine.get_market_performance_report()
    
    # Crear una ventana nueva para el reporte
    report_window = ctk.CTkToplevel(self)
    report_window.title("Executive Performance Report")
    report_window.geometry("600x400")
    
    txt_area = ctk.CTkTextbox(report_window, width=580, height=380)
    txt_area.pack(padx=10, pady=10)
    
    if isinstance(report_data, pd.DataFrame):
        txt_area.insert("0.0", report_data.to_string(index=False))
    else:
        txt_area.insert("0.0", "Sin datos suficientes para el reporte.")
# Dentro de la clase MarketTerminalPro en main_ui.py

from analytics import MarketAnalytics # Importar el nuevo archivo

# ... en el __init__ ...
self.analyzer = MarketAnalytics()

# ... Agregar un botón en setup_ui ...
self.btn_analyze = ctk.CTkButton(self.side, text="Ejecutar Predictor AI", 
                                 command=self.run_ai_analysis,
                                 fg_color="#A33333")
self.btn_analyze.pack(pady=10, padx=20)

def run_ai_analysis(self):
    """Toma el ticker seleccionado y lanza el análisis."""
    selected = self.tree.focus()
    if not selected:
        messagebox.showwarning("Analítica", "Selecciona un activo de la tabla primero.")
        return
    
    ticker = self.tree.item(selected)['values'][0]
    results = self.analyzer.calculate_indicators(ticker)
    prediction = self.analyzer.generate_prediction(ticker)
    
    # Mostrar resultados en una ventana emergente o en el log
    msg = f"--- Análisis para {ticker} ---\n"
    msg += f"Señal: {results['signal']}\n"
    msg += f"Volatilidad: {results['volatility']}\n"
    msg += f"Precio Objetivo: {prediction['target_24h']}"
    
    messagebox.showinfo("Motor de Analítica", msg)
class MarketTerminalPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.engine = FinancialEngine()
        self.title("QUANT-CORE REAL-TIME TERMINAL v3.0")
        self.geometry("1400x850")
        
        # Configuración de estado
        self.watchlist = ["AAPL", "TSLA", "BTC-USD", "GOOGL", "MSFT"]
        self.cache_data = {}
        self.is_running = True
        self.update_interval = 3 # ACTUALIZACIÓN CADA 3 SEGUNDOS
        
        self.setup_ui()
        self.start_threads()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Lateral
        self.side = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.side.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.side, text="OPERACIONES", font=("Segoe UI", 18, "bold")).pack(pady=20)
        
        self.btn_export = ctk.CTkButton(self.side, text="Exportar SQL a CSV", command=self.exportar)
        self.btn_export.pack(pady=10, padx=20)
        
        self.status_indicator = ctk.CTkLabel(self.side, text="● LIVE", text_color="green")
        self.status_indicator.pack(side="bottom", pady=20)

        # Principal
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.table_frame = ctk.CTkFrame(self.main)
        self.table_frame.pack(fill="both", expand=True, pady=10)
        
        cols = ("Ticker", "Precio", "Variación", "Volumen")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def exportar(self):
        archivo = self.engine.export_to_csv()
        messagebox.showinfo("SQL Export", f"Base de datos exportada a: {archivo}")

    def update_cycle(self):
        def update_main_view(self):
        """Actualiza la vista principal con el gráfico de proyección."""
        if self.active_ticker in self.cache_data:
            d = self.cache_data[self.active_ticker]
            
            # Actualizar etiquetas de texto
            self.price_label.configure(
                text=f"$ {d['price']}", 
                text_color="#2ECC71" if d['change'] >= 0 else "#E74C3C"
            )

            # --- LÓGICA DE GRÁFICO CON PROYECCIÓN ---
            self.ax.clear()
            
            # 1. Dibujar Histórico (Datos reales en la DB)
            history = d.get('history', [])
            self.ax.plot(history, color='#1f538d', linewidth=3, label="Historial Real")
            
            # 2. Calcular y Dibujar Proyección
            future_x, future_y = self.analyzer.get_projection_coords(self.active_ticker)
            
            if future_x is not None:
                # Dibujamos la línea de tendencia futura
                self.ax.plot(future_x, future_y, color='#E74C3C', linestyle='--', 
                             linewidth=2, label="Proyección AI")
                
                # Sombreado de confianza (opcional, nivel Pro)
                self.ax.fill_between(future_x, future_y - 0.5, future_y + 0.5, 
                                     color='#E74C3C', alpha=0.1)

            # Estética de la gráfica empresarial
            self.ax.set_title(f"ANÁLISIS PREDICTIVO: {self.active_ticker}", color="white", fontsize=12)
            self.ax.legend(facecolor='#1a1a1a', labelcolor='white')
            self.ax.grid(True, alpha=0.1)
            self.canvas.draw()
        """Ciclo de actualización ultra-rápido."""
        while self.is_running:
            for ticker in self.watchlist:
                data = self.engine.fetch_live_price(ticker)
                if data:
                    self.cache_data[ticker] = data
            
            # Refrescar UI en el hilo principal
            self.after(0, self.refresh_table)
            time.sleep(self.update_interval)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for t, d in self.cache_data.items():
            color = "green" if d['change'] >= 0 else "red"
            self.tree.insert("", "end", values=(t, f"$ {d['price']}", f"{d['change']}%", d['vol']))

    def start_threads(self):
        self.engine.log_event("Inicio de terminal profesional")
        t = threading.Thread(target=self.update_cycle, daemon=True)
        t.start()

if __name__ == "__main__":
    app = MarketTerminalPro()
    app.mainloop()