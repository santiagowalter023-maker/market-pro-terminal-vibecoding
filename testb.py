#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  MARKET PRO TERMINAL v3.0
  Sistema Profesional de Gestión de Activos Financieros
  Con Base de Datos SQL Completa (Simulada + SQLite)
================================================================================
  Autor       : Market Pro Team
  Versión     : 3.0.0
  Python      : 3.9+
  Dependencias: tkinter, customtkinter, yfinance, pandas, matplotlib, sqlite3
================================================================================
"""

# ==============================================================================
# SECCIÓN 1: IMPORTACIONES Y CONFIGURACIÓN GLOBAL
# ==============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import yfinance as yf
import threading
import pandas as pd
import sqlite3
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import time
import logging
import csv
import os
import json
import math
import random
import hashlib
import uuid
import copy
import statistics
import traceback
import sys
import io
import re
from collections import defaultdict, OrderedDict
from typing import Optional, List, Dict, Tuple, Any, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from functools import lru_cache, wraps
import queue
import weakref
import struct
import zlib
import base64
import hmac
import secrets
import itertools
import functools
import operator
import heapq
import bisect
import textwrap


# ==============================================================================
# SECCIÓN 2: CONFIGURACIÓN DE LOGGING
# ==============================================================================

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(log_file: str = 'market_pro.log', level: int = logging.DEBUG) -> logging.Logger:
    """
    Configura el sistema de logging con rotación de archivos y formato profesional.
    
    Args:
        log_file: Ruta al archivo de log
        level: Nivel mínimo de logging
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger('MarketPro')
    logger.setLevel(level)
    
    # Handler para archivo
    try:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(fh)
    except Exception as e:
        print(f"Warning: No se pudo crear el log file: {e}")
    
    # Handler para consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', LOG_DATE_FORMAT))
    logger.addHandler(ch)
    
    return logger


# Logger global
logger = setup_logging()


# ==============================================================================
# SECCIÓN 3: CONSTANTES Y CONFIGURACIÓN
# ==============================================================================

APP_NAME = "MARKET PRO TERMINAL"
APP_VERSION = "3.0.0"
APP_BUILD = "20240115"
APP_AUTHOR = "Market Pro Team"
APP_LICENSE = "Professional"

# Configuración de ventana
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700

# Configuración de actualización
DEFAULT_REFRESH_INTERVAL = 30  # segundos
MIN_REFRESH_INTERVAL = 5
MAX_REFRESH_INTERVAL = 300

# Configuración de base de datos
DB_NAME = "market_data.db"
DB_VERSION = "3.0"
DB_MAX_HISTORY_DAYS = 365
DB_VACUUM_INTERVAL = 7  # días

# Tickers predeterminados
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "META", "NVDA", "BTC-USD", "ETH-USD", "SPY",
    "QQQ", "NFLX", "AMD", "INTC", "DIS"
]

# Colores del tema
COLORS = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_tertiary": "#0f3460",
    "accent_blue": "#1f538d",
    "accent_cyan": "#00b4d8",
    "accent_green": "#00c896",
    "accent_red": "#ff4757",
    "accent_yellow": "#ffd700",
    "accent_purple": "#7b2d8b",
    "text_primary": "#e8e8e8",
    "text_secondary": "#a0a0a0",
    "text_muted": "#606060",
    "border": "#2a2a4a",
    "success": "#2ed573",
    "warning": "#ffa502",
    "error": "#ff6b81",
    "info": "#1e90ff",
}

# Monedas soportadas
SUPPORTED_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF",
    "CNY", "HKD", "NZD", "SEK", "NOK", "DKK", "SGD",
    "ARS", "BRL", "MXN", "CLP", "COP", "PEN"
]

# Intervalos de tiempo para gráficos
TIME_INTERVALS = {
    "1m": "1 Minuto",
    "5m": "5 Minutos",
    "15m": "15 Minutos",
    "30m": "30 Minutos",
    "1h": "1 Hora",
    "4h": "4 Horas",
    "1d": "1 Día",
    "1wk": "1 Semana",
    "1mo": "1 Mes"
}

# Periodos históricos
HISTORY_PERIODS = {
    "1d": "Hoy",
    "5d": "5 Días",
    "1mo": "1 Mes",
    "3mo": "3 Meses",
    "6mo": "6 Meses",
    "1y": "1 Año",
    "2y": "2 Años",
    "5y": "5 Años",
    "10y": "10 Años",
    "ytd": "Año en Curso",
    "max": "Máximo"
}

# Indicadores técnicos disponibles
TECHNICAL_INDICATORS = [
    "SMA_20", "SMA_50", "SMA_200",
    "EMA_12", "EMA_26",
    "MACD", "RSI", "BOLLINGER",
    "STOCHASTIC", "ADX",
    "VOLUME_SMA", "OBV",
    "ATR", "CCI", "MFI"
]

# Tipos de orden
ORDER_TYPES = ["MARKET", "LIMIT", "STOP", "STOP_LIMIT", "TRAILING_STOP"]

# Estados de orden
ORDER_STATUS = ["PENDING", "FILLED", "PARTIAL", "CANCELLED", "REJECTED", "EXPIRED"]

# Tipos de activos
ASSET_TYPES = {
    "STOCK": "Acciones",
    "ETF": "ETF",
    "CRYPTO": "Criptomoneda",
    "FOREX": "Divisas",
    "COMMODITY": "Commodities",
    "BOND": "Bonos",
    "INDEX": "Índice",
    "FUTURE": "Futuro",
    "OPTION": "Opción"
}

# Sectores del mercado
MARKET_SECTORS = [
    "Technology", "Healthcare", "Financials", "Consumer Discretionary",
    "Communication Services", "Industrials", "Consumer Staples",
    "Energy", "Utilities", "Real Estate", "Materials"
]


# ==============================================================================
# SECCIÓN 4: ENUMERACIONES Y TIPOS DE DATOS
# ==============================================================================
class MarketProTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()
        # ... tus configuraciones de ventana ...
        
        # Inicializamos el NUEVO MOTOR
        self.financial_engine = FinancialEnginePro()
        
        # Lista de tickers a monitorear (usando tus constantes)
        self.active_tickers = DEFAULT_TICKERS
        
        # Iniciar el bucle de actualización de 3 segundos
        self.start_live_updates()

    def start_live_updates(self):
        """Lanza el ciclo de actualización en un hilo separado."""
        def update_loop():
            while True:
                # El motor actualiza todo en paralelo
                updated_data = self.financial_engine.update_batch(self.active_tickers)
                
                # Aquí enviarías los datos a tu Treeview (Sección 12 de tu archivo)
                self.after(0, lambda: self.refresh_ui_elements(updated_data))
                
                time.sleep(3) # Frecuencia de 3 segundos

        threading.Thread(target=update_loop, daemon=True).start()

    def refresh_ui_elements(self, data):
        """Actualiza las tablas y etiquetas con la nueva data del motor."""
        for item in data:
            if item:
                # Lógica para actualizar tu Treeview existente
                # self.tree.item(item['ticker'], values=(...))
                pass
class OrderSide(Enum):
    """Lado de la orden: compra o venta"""
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    """Tipo de orden de mercado"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"

class OrderStatus(Enum):
    """Estado actual de una orden"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class AssetType(Enum):
    """Tipo de activo financiero"""
    STOCK = "STOCK"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"
    BOND = "BOND"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"

class AlertType(Enum):
    """Tipo de alerta de precio"""
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    PERCENT_CHANGE = "PERCENT_CHANGE"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    RSI_OVERBOUGHT = "RSI_OVERBOUGHT"
    RSI_OVERSOLD = "RSI_OVERSOLD"
    MACD_CROSS = "MACD_CROSS"

class NotificationType(Enum):
    """Tipo de notificación del sistema"""
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    ALERT = "ALERT"

class MarketStatus(Enum):
    """Estado del mercado"""
    PRE_MARKET = "PRE_MARKET"
    OPEN = "OPEN"
    AFTER_HOURS = "AFTER_HOURS"
    CLOSED = "CLOSED"
    HOLIDAY = "HOLIDAY"


# ==============================================================================
# SECCIÓN 5: DATACLASSES - MODELOS DE DATOS
# ==============================================================================

@dataclass
class TickerData:
    """
    Modelo de datos para la información de un ticker financiero.
    Contiene todos los datos de precio, volumen e indicadores.
    """
    symbol: str
    price: float = 0.0
    open_price: float = 0.0
    prev_close: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: int = 0
    avg_volume: int = 0
    market_cap: float = 0.0
    pe_ratio: float = 0.0
    eps: float = 0.0
    dividend_yield: float = 0.0
    beta: float = 0.0
    week_52_high: float = 0.0
    week_52_low: float = 0.0
    currency: str = "USD"
    asset_type: str = "STOCK"
    sector: str = ""
    industry: str = ""
    company_name: str = ""
    exchange: str = ""
    country: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    is_valid: bool = True
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el dataclass a diccionario"""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "open_price": self.open_price,
            "prev_close": self.prev_close,
            "change": self.change,
            "change_pct": self.change_pct,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "avg_volume": self.avg_volume,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "eps": self.eps,
            "dividend_yield": self.dividend_yield,
            "beta": self.beta,
            "week_52_high": self.week_52_high,
            "week_52_low": self.week_52_low,
            "currency": self.currency,
            "asset_type": self.asset_type,
            "sector": self.sector,
            "industry": self.industry,
            "company_name": self.company_name,
            "exchange": self.exchange,
            "country": self.country,
            "timestamp": self.timestamp.isoformat(),
            "is_valid": self.is_valid,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TickerData':
        """Crea una instancia desde un diccionario"""
        instance = cls(symbol=data.get("symbol", ""))
        for key, value in data.items():
            if hasattr(instance, key) and key != "timestamp":
                setattr(instance, key, value)
        if "timestamp" in data:
            try:
                instance.timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                instance.timestamp = datetime.now()
        return instance

    def format_price(self) -> str:
        """Formatea el precio con la moneda correspondiente"""
        symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
        symbol = symbols.get(self.currency, self.currency + " ")
        return f"{symbol}{self.price:,.2f}"

    def format_change(self) -> str:
        """Formatea el cambio porcentual con signo"""
        sign = "+" if self.change_pct >= 0 else ""
        return f"{sign}{self.change_pct:.2f}%"

    def format_volume(self) -> str:
        """Formatea el volumen en formato legible (K, M, B)"""
        if self.volume >= 1_000_000_000:
            return f"{self.volume / 1_000_000_000:.2f}B"
        elif self.volume >= 1_000_000:
            return f"{self.volume / 1_000_000:.2f}M"
        elif self.volume >= 1_000:
            return f"{self.volume / 1_000:.2f}K"
        return str(self.volume)

    def format_market_cap(self) -> str:
        """Formatea la capitalización de mercado"""
        if self.market_cap >= 1_000_000_000_000:
            return f"${self.market_cap / 1_000_000_000_000:.2f}T"
        elif self.market_cap >= 1_000_000_000:
            return f"${self.market_cap / 1_000_000_000:.2f}B"
        elif self.market_cap >= 1_000_000:
            return f"${self.market_cap / 1_000_000:.2f}M"
        return f"${self.market_cap:,.0f}"

    def is_bullish(self) -> bool:
        """Determina si el activo está en tendencia alcista"""
        return self.change_pct > 0

    def get_trend_emoji(self) -> str:
        """Retorna emoji de tendencia"""
        if self.change_pct > 2:
            return "🚀"
        elif self.change_pct > 0:
            return "📈"
        elif self.change_pct < -2:
            return "📉"
        else:
            return "➡️"

# ==============================================================================
# SECCIÓN 5.5: MOTOR FINANCIERO ENTERPRISE (EL NUEVO "MOTOR")
# ==============================================================================

class FinancialEnginePro:
    """
    Motor de alta frecuencia optimizado para la Terminal Market Pro.
    Maneja caché en RAM, escritura asíncrona y consultas paralelas.
    """
    def __init__(self, db_name="market_enterprise_v4.db", max_workers=8):
        self.db_name = db_name
        self.max_workers = max_workers
        self.cache = {}  
        self.write_queue = queue.Queue()
        self._init_db()
        self._start_background_worker()
        logger.info("Motor Enterprise Pro vinculado correctamente.")

    @contextmanager
    def _get_connection(self):
        """Gestión de conexión segura para evitar bloqueos de SQLite."""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL") # Permite lectura/escritura simultánea
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
        """Hilo dedicado a escribir en DB sin congelar la interfaz."""
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
                    logger.error(f"Error en persistencia: {e}")
                self.write_queue.task_done()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def fetch_live_data(self, ticker):
        """Obtención ultra-rápida usando fast_info."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            # Cálculo de métricas
            price = info['last_price']
            prev_close = info['previous_close']
            change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
            
            data_packet = {
                "ticker": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "high": round(info['day_high'], 2),
                "low": round(info['day_low'], 2),
                "vol": int(info['last_volume']),
                "ts": datetime.now()
            }
            
            # Actualizamos RAM y encolamos para DISCO
            self.cache[ticker] = data_packet
            self.write_queue.put(data_packet)
            return data_packet
        except Exception as e:
            logger.warning(f"No se pudo obtener {ticker}: {e}")
            return None

    def update_batch(self, tickers):
        """Actualiza múltiples tickers en paralelo usando hilos."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.fetch_live_data, tickers))

    def get_sma(self, ticker, window=20):
        """Calcula Media Móvil desde los datos reales guardados."""
        try:
            with self._get_connection() as conn:
                df = pd.read_sql_query(
                    f"SELECT price FROM prices WHERE ticker='{ticker}' ORDER BY timestamp DESC LIMIT {window}", 
                    conn
                )
                return round(df['price'].mean(), 2) if not df.empty else None
        except: return None
@dataclass
class Portfolio:
    """
    Modelo de datos para un portafolio de inversión.
    """
    portfolio_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Mi Portafolio"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    currency: str = "USD"
    initial_capital: float = 100000.0
    cash_balance: float = 100000.0
    positions: Dict[str, 'Position'] = field(default_factory=dict)
    transactions: List['Transaction'] = field(default_factory=list)
    is_active: bool = True
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def total_value(self) -> float:
        """Calcula el valor total del portafolio"""
        return self.cash_balance + sum(
            pos.current_value for pos in self.positions.values()
        )

    @property
    def total_gain_loss(self) -> float:
        """Calcula la ganancia/pérdida total"""
        return self.total_value - self.initial_capital

    @property
    def total_gain_loss_pct(self) -> float:
        """Calcula el porcentaje de ganancia/pérdida"""
        if self.initial_capital == 0:
            return 0.0
        return (self.total_gain_loss / self.initial_capital) * 100

    @property
    def num_positions(self) -> int:
        """Número de posiciones activas"""
        return len([p for p in self.positions.values() if p.quantity > 0])

    def get_allocation(self) -> Dict[str, float]:
        """Calcula la asignación porcentual por activo"""
        total = self.total_value
        if total == 0:
            return {}
        allocation = {"CASH": (self.cash_balance / total) * 100}
        for sym, pos in self.positions.items():
            allocation[sym] = (pos.current_value / total) * 100
        return allocation

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el portafolio a diccionario"""
        return {
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "currency": self.currency,
            "initial_capital": self.initial_capital,
            "cash_balance": self.cash_balance,
            "is_active": self.is_active,
            "tags": self.tags,
            "notes": self.notes,
            "total_value": self.total_value,
            "total_gain_loss": self.total_gain_loss,
            "total_gain_loss_pct": self.total_gain_loss_pct,
        }


@dataclass
class Position:
    """
    Modelo de datos para una posición dentro de un portafolio.
    """
    position_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str = ""
    symbol: str = ""
    quantity: float = 0.0
    avg_cost: float = 0.0
    current_price: float = 0.0
    asset_type: str = "STOCK"
    opened_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    tags: List[str] = field(default_factory=list)

    @property
    def current_value(self) -> float:
        """Valor actual de la posición"""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Costo base de la posición"""
        return self.quantity * self.avg_cost

    @property
    def unrealized_pnl(self) -> float:
        """Ganancia/pérdida no realizada"""
        return self.current_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        """Porcentaje de ganancia/pérdida no realizada"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    @property
    def is_profitable(self) -> bool:
        """Indica si la posición es rentable"""
        return self.unrealized_pnl > 0

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la posición a diccionario"""
        return {
            "position_id": self.position_id,
            "portfolio_id": self.portfolio_id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_cost": self.avg_cost,
            "current_price": self.current_price,
            "asset_type": self.asset_type,
            "opened_at": self.opened_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_value": self.current_value,
            "cost_basis": self.cost_basis,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_pct": self.unrealized_pnl_pct,
        }


@dataclass
class Transaction:
    """
    Modelo de datos para una transacción de compra/venta.
    """
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str = ""
    symbol: str = ""
    side: str = "BUY"
    order_type: str = "MARKET"
    quantity: float = 0.0
    price: float = 0.0
    total_value: float = 0.0
    commission: float = 0.0
    executed_at: datetime = field(default_factory=datetime.now)
    status: str = "FILLED"
    notes: str = ""
    tax_lot_id: str = ""

    @property
    def net_amount(self) -> float:
        """Monto neto de la transacción (incluyendo comisión)"""
        if self.side == "BUY":
            return -(self.total_value + self.commission)
        else:
            return self.total_value - self.commission

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la transacción a diccionario"""
        return {
            "transaction_id": self.transaction_id,
            "portfolio_id": self.portfolio_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "quantity": self.quantity,
            "price": self.price,
            "total_value": self.total_value,
            "commission": self.commission,
            "executed_at": self.executed_at.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "net_amount": self.net_amount,
        }


@dataclass
class PriceAlert:
    """
    Modelo de datos para una alerta de precio.
    """
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    alert_type: str = "PRICE_ABOVE"
    threshold: float = 0.0
    message: str = ""
    is_active: bool = True
    is_triggered: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    repeat: bool = False
    priority: str = "MEDIUM"

    def check_trigger(self, current_price: float, current_pct_change: float = 0.0) -> bool:
        """
        Verifica si la alerta debe dispararse.
        
        Args:
            current_price: Precio actual del activo
            current_pct_change: Cambio porcentual actual
        
        Returns:
            True si la alerta debe dispararse
        """
        if not self.is_active or (self.is_triggered and not self.repeat):
            return False
        
        if self.alert_type == "PRICE_ABOVE":
            return current_price >= self.threshold
        elif self.alert_type == "PRICE_BELOW":
            return current_price <= self.threshold
        elif self.alert_type == "PERCENT_CHANGE":
            return abs(current_pct_change) >= self.threshold
        
        return False

    def trigger(self) -> None:
        """Marca la alerta como disparada"""
        self.is_triggered = True
        self.triggered_at = datetime.now()
        if not self.repeat:
            self.is_active = False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la alerta a diccionario"""
        return {
            "alert_id": self.alert_id,
            "symbol": self.symbol,
            "alert_type": self.alert_type,
            "threshold": self.threshold,
            "message": self.message,
            "is_active": self.is_active,
            "is_triggered": self.is_triggered,
            "created_at": self.created_at.isoformat(),
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "repeat": self.repeat,
            "priority": self.priority,
        }


@dataclass
class Watchlist:
    """
    Modelo de datos para una lista de seguimiento de activos.
    """
    watchlist_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Mi Watchlist"
    description: str = ""
    symbols: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    color: str = "#1f538d"
    icon: str = "⭐"
    is_default: bool = False
    tags: List[str] = field(default_factory=list)

    def add_symbol(self, symbol: str) -> bool:
        """Añade un símbolo a la watchlist"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.updated_at = datetime.now()
            return True
        return False

    def remove_symbol(self, symbol: str) -> bool:
        """Elimina un símbolo de la watchlist"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            self.updated_at = datetime.now()
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la watchlist a diccionario"""
        return {
            "watchlist_id": self.watchlist_id,
            "name": self.name,
            "description": self.description,
            "symbols": self.symbols,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "color": self.color,
            "icon": self.icon,
            "is_default": self.is_default,
        }


@dataclass
class MarketNews:
    """
    Modelo de datos para noticias del mercado.
    """
    news_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    summary: str = ""
    url: str = ""
    source: str = ""
    published_at: datetime = field(default_factory=datetime.now)
    related_symbols: List[str] = field(default_factory=list)
    sentiment: str = "NEUTRAL"
    impact: str = "LOW"
    tags: List[str] = field(default_factory=list)
    is_read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la noticia a diccionario"""
        return {
            "news_id": self.news_id,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "related_symbols": self.related_symbols,
            "sentiment": self.sentiment,
            "impact": self.impact,
            "is_read": self.is_read,
        }


@dataclass
class UserSettings:
    """
    Configuración de usuario para la aplicación.
    """
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = "Usuario"
    email: str = ""
    theme: str = "Dark"
    language: str = "es"
    default_currency: str = "USD"
    refresh_interval: int = 30
    show_notifications: bool = True
    play_sounds: bool = False
    default_chart_type: str = "line"
    default_period: str = "1d"
    default_interval: str = "1m"
    decimal_places: int = 2
    timezone: str = "America/New_York"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    watchlist_columns: List[str] = field(default_factory=lambda: [
        "symbol", "price", "change_pct", "volume", "market_cap"
    ])
    chart_indicators: List[str] = field(default_factory=lambda: ["SMA_20", "SMA_50"])
    commission_rate: float = 0.0  # en porcentaje
    risk_tolerance: str = "MODERATE"
    investment_goal: str = "GROWTH"

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la configuración a diccionario"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "theme": self.theme,
            "language": self.language,
            "default_currency": self.default_currency,
            "refresh_interval": self.refresh_interval,
            "show_notifications": self.show_notifications,
            "play_sounds": self.play_sounds,
            "default_chart_type": self.default_chart_type,
            "default_period": self.default_period,
            "default_interval": self.default_interval,
            "decimal_places": self.decimal_places,
            "timezone": self.timezone,
            "commission_rate": self.commission_rate,
            "risk_tolerance": self.risk_tolerance,
            "investment_goal": self.investment_goal,
        }


# ==============================================================================
# SECCIÓN 6: BASE DE DATOS SIMULADA EN MEMORIA
# ==============================================================================

class SimulatedDatabase:
    """
    Base de datos simulada en memoria para demostración y testing.
    Implementa todas las operaciones CRUD de manera programática,
    sin depender de SQLite ni ningún motor externo.
    
    Esta implementación simula un motor relacional completo con:
    - Tablas como diccionarios indexados
    - Índices para búsquedas eficientes
    - Transacciones ACID simplificadas
    - Consultas tipo SQL con filtros
    - Joins entre tablas
    - Agregaciones (COUNT, SUM, AVG, MAX, MIN)
    - Triggers simulados
    - Procedimientos almacenados como métodos
    """

    def __init__(self):
        """Inicializa la base de datos simulada con todas las tablas"""
        logger.info("Inicializando base de datos simulada en memoria...")
        
        # Almacenamiento principal: tabla -> {id -> registro}
        self._tables: Dict[str, Dict[str, Dict]] = {}
        
        # Índices para búsqueda eficiente: tabla -> campo -> {valor -> [ids]}
        self._indexes: Dict[str, Dict[str, Dict]] = {}
        
        # Auto-increment por tabla
        self._auto_increment: Dict[str, int] = {}
        
        # Transacciones en curso
        self._transactions: List[Dict] = []
        self._in_transaction: bool = False
        self._transaction_log: List[Dict] = []
        
        # Triggers: tabla -> evento -> [callbacks]
        self._triggers: Dict[str, Dict[str, List]] = {}
        
        # Estadísticas de uso
        self._stats = {
            "total_reads": 0,
            "total_writes": 0,
            "total_deletes": 0,
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        # Cache de consultas
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._cache_duration: int = 30  # segundos
        
        # Historial de cambios (para auditoría)
        self._audit_log: List[Dict] = []
        self._max_audit_entries: int = 10000
        
        # Inicializar esquema
        self._initialize_schema()
        
        # Poblar con datos simulados
        self._populate_simulated_data()
        
        logger.info("Base de datos simulada inicializada correctamente.")

    # ─────────────────────────────────────────────────────────────────────────
    # INICIALIZACIÓN DEL ESQUEMA
    # ─────────────────────────────────────────────────────────────────────────

    def _initialize_schema(self) -> None:
        """
        Define el esquema completo de la base de datos.
        Crea todas las tablas con sus columnas, tipos y constraints.
        """
        logger.info("Creando esquema de base de datos simulada...")
        
        # Tabla: tickers (información básica de activos)
        self._create_table("tickers", {
            "ticker_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT UNIQUE NOT NULL",
            "company_name": "TEXT",
            "asset_type": "TEXT DEFAULT 'STOCK'",
            "exchange": "TEXT",
            "sector": "TEXT",
            "industry": "TEXT",
            "country": "TEXT DEFAULT 'US'",
            "currency": "TEXT DEFAULT 'USD'",
            "isin": "TEXT",
            "cusip": "TEXT",
            "description": "TEXT",
            "website": "TEXT",
            "ceo": "TEXT",
            "employees": "INTEGER",
            "founded_year": "INTEGER",
            "is_active": "BOOLEAN DEFAULT 1",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        })
        self._create_index("tickers", "symbol")
        self._create_index("tickers", "asset_type")
        self._create_index("tickers", "sector")
        self._create_index("tickers", "exchange")

        # Tabla: price_history (historial de precios)
        self._create_table("price_history", {
            "history_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "open_price": "REAL",
            "high_price": "REAL",
            "low_price": "REAL",
            "close_price": "REAL",
            "adj_close": "REAL",
            "volume": "INTEGER",
            "interval": "TEXT DEFAULT '1d'",
            "timestamp": "DATETIME NOT NULL",
            "source": "TEXT DEFAULT 'yfinance'",
            "is_adjusted": "BOOLEAN DEFAULT 0",
        })
        self._create_index("price_history", "symbol")
        self._create_index("price_history", "timestamp")

        # Tabla: real_time_quotes (cotizaciones en tiempo real)
        self._create_table("real_time_quotes", {
            "quote_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "bid": "REAL",
            "ask": "REAL",
            "last_price": "REAL",
            "bid_size": "INTEGER",
            "ask_size": "INTEGER",
            "spread": "REAL",
            "mid_price": "REAL",
            "timestamp": "DATETIME",
        })
        self._create_index("real_time_quotes", "symbol")

        # Tabla: market_data (datos de mercado actuales)
        self._create_table("market_data", {
            "data_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "price": "REAL",
            "open_price": "REAL",
            "prev_close": "REAL",
            "change": "REAL",
            "change_pct": "REAL",
            "high": "REAL",
            "low": "REAL",
            "volume": "INTEGER",
            "avg_volume": "INTEGER",
            "market_cap": "REAL",
            "pe_ratio": "REAL",
            "eps": "REAL",
            "dividend_yield": "REAL",
            "beta": "REAL",
            "week_52_high": "REAL",
            "week_52_low": "REAL",
            "currency": "TEXT",
            "timestamp": "DATETIME",
            "is_market_hours": "BOOLEAN",
        })
        self._create_index("market_data", "symbol")
        self._create_index("market_data", "timestamp")

        # Tabla: portfolios (portafolios de inversión)
        self._create_table("portfolios", {
            "portfolio_id": "TEXT PRIMARY KEY",
            "name": "TEXT NOT NULL",
            "description": "TEXT",
            "currency": "TEXT DEFAULT 'USD'",
            "initial_capital": "REAL DEFAULT 100000",
            "cash_balance": "REAL DEFAULT 100000",
            "is_active": "BOOLEAN DEFAULT 1",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
            "notes": "TEXT",
            "benchmark": "TEXT DEFAULT 'SPY'",
            "strategy": "TEXT",
        })

        # Tabla: positions (posiciones del portafolio)
        self._create_table("positions", {
            "position_id": "TEXT PRIMARY KEY",
            "portfolio_id": "TEXT NOT NULL",
            "symbol": "TEXT NOT NULL",
            "quantity": "REAL DEFAULT 0",
            "avg_cost": "REAL DEFAULT 0",
            "current_price": "REAL DEFAULT 0",
            "asset_type": "TEXT DEFAULT 'STOCK'",
            "opened_at": "DATETIME",
            "updated_at": "DATETIME",
            "is_short": "BOOLEAN DEFAULT 0",
            "notes": "TEXT",
            "tax_lot": "TEXT",
        })
        self._create_index("positions", "portfolio_id")
        self._create_index("positions", "symbol")

        # Tabla: transactions (historial de transacciones)
        self._create_table("transactions", {
            "transaction_id": "TEXT PRIMARY KEY",
            "portfolio_id": "TEXT NOT NULL",
            "symbol": "TEXT NOT NULL",
            "side": "TEXT NOT NULL",
            "order_type": "TEXT DEFAULT 'MARKET'",
            "quantity": "REAL NOT NULL",
            "price": "REAL NOT NULL",
            "total_value": "REAL",
            "commission": "REAL DEFAULT 0",
            "executed_at": "DATETIME",
            "status": "TEXT DEFAULT 'FILLED'",
            "notes": "TEXT",
            "order_id": "TEXT",
            "tax_lot_id": "TEXT",
            "realized_pnl": "REAL DEFAULT 0",
        })
        self._create_index("transactions", "portfolio_id")
        self._create_index("transactions", "symbol")
        self._create_index("transactions", "executed_at")

        # Tabla: orders (órdenes pendientes)
        self._create_table("orders", {
            "order_id": "TEXT PRIMARY KEY",
            "portfolio_id": "TEXT NOT NULL",
            "symbol": "TEXT NOT NULL",
            "side": "TEXT NOT NULL",
            "order_type": "TEXT NOT NULL",
            "quantity": "REAL NOT NULL",
            "limit_price": "REAL",
            "stop_price": "REAL",
            "trail_amount": "REAL",
            "status": "TEXT DEFAULT 'PENDING'",
            "filled_qty": "REAL DEFAULT 0",
            "avg_fill_price": "REAL DEFAULT 0",
            "created_at": "DATETIME",
            "expires_at": "DATETIME",
            "updated_at": "DATETIME",
            "notes": "TEXT",
            "time_in_force": "TEXT DEFAULT 'GTC'",
        })
        self._create_index("orders", "portfolio_id")
        self._create_index("orders", "symbol")
        self._create_index("orders", "status")

        # Tabla: price_alerts (alertas de precio)
        self._create_table("price_alerts", {
            "alert_id": "TEXT PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "alert_type": "TEXT NOT NULL",
            "threshold": "REAL NOT NULL",
            "message": "TEXT",
            "is_active": "BOOLEAN DEFAULT 1",
            "is_triggered": "BOOLEAN DEFAULT 0",
            "created_at": "DATETIME",
            "triggered_at": "DATETIME",
            "repeat": "BOOLEAN DEFAULT 0",
            "priority": "TEXT DEFAULT 'MEDIUM'",
            "portfolio_id": "TEXT",
            "notify_email": "BOOLEAN DEFAULT 0",
            "notify_sms": "BOOLEAN DEFAULT 0",
        })
        self._create_index("price_alerts", "symbol")
        self._create_index("price_alerts", "is_active")

        # Tabla: watchlists (listas de seguimiento)
        self._create_table("watchlists", {
            "watchlist_id": "TEXT PRIMARY KEY",
            "name": "TEXT NOT NULL",
            "description": "TEXT",
            "color": "TEXT DEFAULT '#1f538d'",
            "icon": "TEXT DEFAULT '⭐'",
            "is_default": "BOOLEAN DEFAULT 0",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        })

        # Tabla: watchlist_symbols (símbolos en watchlists)
        self._create_table("watchlist_symbols", {
            "ws_id": "INTEGER PRIMARY KEY",
            "watchlist_id": "TEXT NOT NULL",
            "symbol": "TEXT NOT NULL",
            "added_at": "DATETIME",
            "notes": "TEXT",
            "sort_order": "INTEGER DEFAULT 0",
        })
        self._create_index("watchlist_symbols", "watchlist_id")
        self._create_index("watchlist_symbols", "symbol")

        # Tabla: technical_indicators (indicadores técnicos calculados)
        self._create_table("technical_indicators", {
            "indicator_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "indicator_name": "TEXT NOT NULL",
            "value": "REAL",
            "signal": "TEXT",
            "period": "INTEGER",
            "timestamp": "DATETIME",
        })
        self._create_index("technical_indicators", "symbol")
        self._create_index("technical_indicators", "indicator_name")

        # Tabla: market_news (noticias del mercado)
        self._create_table("market_news", {
            "news_id": "TEXT PRIMARY KEY",
            "title": "TEXT NOT NULL",
            "summary": "TEXT",
            "url": "TEXT",
            "source": "TEXT",
            "published_at": "DATETIME",
            "sentiment": "TEXT DEFAULT 'NEUTRAL'",
            "impact": "TEXT DEFAULT 'LOW'",
            "is_read": "BOOLEAN DEFAULT 0",
            "related_symbols": "TEXT",
        })
        self._create_index("market_news", "published_at")
        self._create_index("market_news", "sentiment")

        # Tabla: economic_calendar (calendario económico)
        self._create_table("economic_calendar", {
            "event_id": "INTEGER PRIMARY KEY",
            "event_name": "TEXT NOT NULL",
            "country": "TEXT",
            "event_date": "DATETIME",
            "impact": "TEXT DEFAULT 'LOW'",
            "previous": "TEXT",
            "forecast": "TEXT",
            "actual": "TEXT",
            "currency": "TEXT",
            "description": "TEXT",
        })
        self._create_index("economic_calendar", "event_date")
        self._create_index("economic_calendar", "country")

        # Tabla: performance_metrics (métricas de rendimiento del portafolio)
        self._create_table("performance_metrics", {
            "metric_id": "INTEGER PRIMARY KEY",
            "portfolio_id": "TEXT NOT NULL",
            "date": "DATE",
            "total_value": "REAL",
            "daily_return": "REAL",
            "cumulative_return": "REAL",
            "benchmark_return": "REAL",
            "alpha": "REAL",
            "beta": "REAL",
            "sharpe_ratio": "REAL",
            "sortino_ratio": "REAL",
            "max_drawdown": "REAL",
            "volatility": "REAL",
            "var_95": "REAL",
        })
        self._create_index("performance_metrics", "portfolio_id")
        self._create_index("performance_metrics", "date")

        # Tabla: user_settings (configuración de usuario)
        self._create_table("user_settings", {
            "setting_id": "INTEGER PRIMARY KEY",
            "user_id": "TEXT NOT NULL",
            "setting_key": "TEXT NOT NULL",
            "setting_value": "TEXT",
            "setting_type": "TEXT DEFAULT 'string'",
            "updated_at": "DATETIME",
        })
        self._create_index("user_settings", "user_id")

        # Tabla: audit_log (registro de auditoría)
        self._create_table("audit_log", {
            "log_id": "INTEGER PRIMARY KEY",
            "table_name": "TEXT NOT NULL",
            "record_id": "TEXT NOT NULL",
            "action": "TEXT NOT NULL",
            "old_values": "TEXT",
            "new_values": "TEXT",
            "performed_at": "DATETIME",
            "user_id": "TEXT",
            "ip_address": "TEXT",
        })

        # Tabla: system_logs (logs del sistema)
        self._create_table("system_logs", {
            "log_id": "INTEGER PRIMARY KEY",
            "level": "TEXT NOT NULL",
            "module": "TEXT",
            "message": "TEXT NOT NULL",
            "details": "TEXT",
            "logged_at": "DATETIME",
            "user_id": "TEXT",
            "session_id": "TEXT",
        })

        # Tabla: data_snapshots (instantáneas del mercado)
        self._create_table("data_snapshots", {
            "snapshot_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "price": "REAL",
            "change_pct": "REAL",
            "volume": "INTEGER",
            "timestamp": "DATETIME",
            "market_status": "TEXT",
            "notes": "TEXT",
        })
        self._create_index("data_snapshots", "symbol")
        self._create_index("data_snapshots", "timestamp")

        # Tabla: correlations (correlaciones entre activos)
        self._create_table("correlations", {
            "corr_id": "INTEGER PRIMARY KEY",
            "symbol_a": "TEXT NOT NULL",
            "symbol_b": "TEXT NOT NULL",
            "correlation": "REAL",
            "period": "TEXT DEFAULT '1y'",
            "calculated_at": "DATETIME",
        })
        self._create_index("correlations", "symbol_a")

        # Tabla: sector_performance (rendimiento por sector)
        self._create_table("sector_performance", {
            "perf_id": "INTEGER PRIMARY KEY",
            "sector": "TEXT NOT NULL",
            "daily_change": "REAL",
            "weekly_change": "REAL",
            "monthly_change": "REAL",
            "ytd_change": "REAL",
            "market_cap": "REAL",
            "timestamp": "DATETIME",
        })
        self._create_index("sector_performance", "sector")

        # Tabla: dividend_history (historial de dividendos)
        self._create_table("dividend_history", {
            "div_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "ex_date": "DATE",
            "payment_date": "DATE",
            "record_date": "DATE",
            "amount": "REAL",
            "frequency": "TEXT",
            "type": "TEXT DEFAULT 'REGULAR'",
        })
        self._create_index("dividend_history", "symbol")
        self._create_index("dividend_history", "ex_date")

        # Tabla: earnings_calendar (calendario de ganancias corporativas)
        self._create_table("earnings_calendar", {
            "earning_id": "INTEGER PRIMARY KEY",
            "symbol": "TEXT NOT NULL",
            "report_date": "DATE",
            "report_time": "TEXT",
            "eps_estimate": "REAL",
            "eps_actual": "REAL",
            "revenue_estimate": "REAL",
            "revenue_actual": "REAL",
            "surprise_pct": "REAL",
            "period": "TEXT",
        })
        self._create_index("earnings_calendar", "symbol")
        self._create_index("earnings_calendar", "report_date")

        # Tabla: options_chain (cadena de opciones)
        self._create_table("options_chain", {
            "option_id": "TEXT PRIMARY KEY",
            "underlying": "TEXT NOT NULL",
            "option_type": "TEXT NOT NULL",
            "strike": "REAL NOT NULL",
            "expiration": "DATE NOT NULL",
            "last_price": "REAL",
            "bid": "REAL",
            "ask": "REAL",
            "volume": "INTEGER",
            "open_interest": "INTEGER",
            "implied_volatility": "REAL",
            "delta": "REAL",
            "gamma": "REAL",
            "theta": "REAL",
            "vega": "REAL",
            "rho": "REAL",
            "in_the_money": "BOOLEAN",
            "timestamp": "DATETIME",
        })
        self._create_index("options_chain", "underlying")
        self._create_index("options_chain", "expiration")

        logger.info(f"Esquema creado: {len(self._tables)} tablas, {sum(len(idx) for idx in self._indexes.values())} índices")

    # ─────────────────────────────────────────────────────────────────────────
    # OPERACIONES DE ESQUEMA (DDL simulado)
    # ─────────────────────────────────────────────────────────────────────────

    def _create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Crea una nueva tabla en la base de datos simulada.
        
        Args:
            table_name: Nombre de la tabla
            schema: Diccionario con los campos y sus tipos
        """
        if table_name not in self._tables:
            self._tables[table_name] = {}
            self._indexes[table_name] = {}
            self._auto_increment[table_name] = 1
            self._triggers[table_name] = {
                "before_insert": [],
                "after_insert": [],
                "before_update": [],
                "after_update": [],
                "before_delete": [],
                "after_delete": [],
            }
            logger.debug(f"Tabla creada: {table_name}")

    def _create_index(self, table_name: str, field_name: str) -> None:
        """
        Crea un índice sobre un campo de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            field_name: Campo a indexar
        """
        if table_name in self._indexes:
            self._indexes[table_name][field_name] = defaultdict(list)
            logger.debug(f"Índice creado: {table_name}.{field_name}")

    def _rebuild_index(self, table_name: str, field_name: str) -> None:
        """
        Reconstruye un índice desde los datos actuales de la tabla.
        
        Args:
            table_name: Nombre de la tabla
            field_name: Campo del índice a reconstruir
        """
        if table_name not in self._indexes:
            return
        if field_name not in self._indexes[table_name]:
            return
        
        self._indexes[table_name][field_name] = defaultdict(list)
        for rec_id, record in self._tables[table_name].items():
            value = record.get(field_name)
            if value is not None:
                self._indexes[table_name][field_name][str(value)].append(rec_id)

    def _update_index(self, table_name: str, record_id: str, record: Dict, old_record: Dict = None) -> None:
        """
        Actualiza los índices para un registro modificado.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            record: Nuevo registro
            old_record: Registro anterior (para actualización)
        """
        if table_name not in self._indexes:
            return
        
        for field_name, index in self._indexes[table_name].items():
            # Eliminar entrada anterior
            if old_record and field_name in old_record:
                old_value = str(old_record[field_name])
                if old_value in index and record_id in index[old_value]:
                    index[old_value].remove(record_id)
            
            # Añadir nueva entrada
            if field_name in record:
                new_value = str(record[field_name])
                if record_id not in index[new_value]:
                    index[new_value].append(record_id)

    def _remove_from_index(self, table_name: str, record_id: str, record: Dict) -> None:
        """
        Elimina un registro de todos los índices.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
            record: Datos del registro
        """
        if table_name not in self._indexes:
            return
        
        for field_name, index in self._indexes[table_name].items():
            if field_name in record:
                value = str(record[field_name])
                if value in index and record_id in index[value]:
                    index[value].remove(record_id)

    # ─────────────────────────────────────────────────────────────────────────
    # OPERACIONES CRUD (DML simulado)
    # ─────────────────────────────────────────────────────────────────────────

    def insert(self, table_name: str, record: Dict) -> str:
        """
        Inserta un nuevo registro en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            record: Datos del registro a insertar
        
        Returns:
            ID del registro insertado
        
        Raises:
            ValueError: Si la tabla no existe o hay violación de constraint
        """
        if table_name not in self._tables:
            raise ValueError(f"Tabla '{table_name}' no existe")
        
        # Ejecutar triggers before_insert
        for trigger in self._triggers[table_name]["before_insert"]:
            trigger(record)
        
        # Generar ID si no se provee
        record_copy = copy.deepcopy(record)
        
        # Determinar el campo primary key
        pk_field = self._get_primary_key(table_name)
        if pk_field and pk_field not in record_copy:
            if "INTEGER" in str(self._get_field_type(table_name, pk_field) or ""):
                record_copy[pk_field] = self._auto_increment[table_name]
                self._auto_increment[table_name] += 1
            else:
                record_copy[pk_field] = str(uuid.uuid4())
        
        record_id = str(record_copy.get(pk_field, len(self._tables[table_name]) + 1))
        
        # Verificar UNIQUE constraints
        if record_id in self._tables[table_name]:
            raise ValueError(f"Registro con ID '{record_id}' ya existe en '{table_name}'")
        
        # Agregar timestamp de creación si aplica
        if "created_at" in record_copy and not record_copy.get("created_at"):
            record_copy["created_at"] = datetime.now().isoformat()
        if "updated_at" in record_copy and not record_copy.get("updated_at"):
            record_copy["updated_at"] = datetime.now().isoformat()
        
        # Insertar registro
        self._tables[table_name][record_id] = record_copy
        
        # Actualizar índices
        self._update_index(table_name, record_id, record_copy)
        
        # Registrar en audit log
        self._log_audit(table_name, record_id, "INSERT", None, record_copy)
        
        # Actualizar estadísticas
        self._stats["total_writes"] += 1
        
        # Ejecutar triggers after_insert
        for trigger in self._triggers[table_name]["after_insert"]:
            trigger(record_copy)
        
        # Invalidar cache
        self._invalidate_cache(table_name)
        
        logger.debug(f"INSERT en {table_name}: ID={record_id}")
        return record_id

    def select(self, table_name: str, filters: Dict = None, 
               order_by: str = None, limit: int = None,
               offset: int = 0, columns: List[str] = None) -> List[Dict]:
        """
        Selecciona registros de una tabla con filtros opcionales.
        
        Args:
            table_name: Nombre de la tabla
            filters: Diccionario de filtros {campo: valor} o {campo: (operador, valor)}
            order_by: Campo por el que ordenar (prefijo '-' para DESC)
            limit: Número máximo de registros
            offset: Número de registros a saltar
            columns: Lista de columnas a retornar (None = todas)
        
        Returns:
            Lista de registros que cumplen los filtros
        """
        if table_name not in self._tables:
            raise ValueError(f"Tabla '{table_name}' no existe")
        
        self._stats["total_reads"] += 1
        self._stats["total_queries"] += 1
        
        # Obtener todos los registros
        records = list(self._tables[table_name].values())
        
        # Aplicar filtros
        if filters:
            records = self._apply_filters(records, filters)
        
        # Ordenar
        if order_by:
            reverse = order_by.startswith('-')
            field = order_by.lstrip('-')
            try:
                records.sort(
                    key=lambda r: (r.get(field) is None, r.get(field, "")),
                    reverse=reverse
                )
            except TypeError:
                records.sort(
                    key=lambda r: str(r.get(field, "")),
                    reverse=reverse
                )
        
        # Aplicar offset y limit
        if offset:
            records = records[offset:]
        if limit is not None:
            records = records[:limit]
        
        # Seleccionar columnas
        if columns:
            records = [{col: r.get(col) for col in columns} for r in records]
        
        return copy.deepcopy(records)

    def select_one(self, table_name: str, filters: Dict = None) -> Optional[Dict]:
        """
        Selecciona un único registro (el primero que coincida).
        
        Args:
            table_name: Nombre de la tabla
            filters: Diccionario de filtros
        
        Returns:
            Registro encontrado o None
        """
        results = self.select(table_name, filters=filters, limit=1)
        return results[0] if results else None

    def select_by_id(self, table_name: str, record_id: str) -> Optional[Dict]:
        """
        Selecciona un registro por su ID.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro
        
        Returns:
            Registro encontrado o None
        """
        if table_name not in self._tables:
            return None
        record = self._tables[table_name].get(str(record_id))
        return copy.deepcopy(record) if record else None

    def update(self, table_name: str, record_id: str, updates: Dict) -> bool:
        """
        Actualiza un registro existente.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro a actualizar
            updates: Diccionario con los campos a actualizar
        
        Returns:
            True si se actualizó correctamente, False si no encontró el registro
        """
        if table_name not in self._tables:
            raise ValueError(f"Tabla '{table_name}' no existe")
        
        record_id = str(record_id)
        if record_id not in self._tables[table_name]:
            return False
        
        old_record = copy.deepcopy(self._tables[table_name][record_id])
        
        # Ejecutar triggers before_update
        for trigger in self._triggers[table_name]["before_update"]:
            trigger(old_record, updates)
        
        # Aplicar actualizaciones
        new_record = copy.deepcopy(old_record)
        new_record.update(updates)
        
        # Actualizar timestamp si aplica
        if "updated_at" in new_record:
            new_record["updated_at"] = datetime.now().isoformat()
        
        self._tables[table_name][record_id] = new_record
        
        # Actualizar índices
        self._update_index(table_name, record_id, new_record, old_record)
        
        # Registrar en audit log
        self._log_audit(table_name, record_id, "UPDATE", old_record, new_record)
        
        # Estadísticas
        self._stats["total_writes"] += 1
        
        # Ejecutar triggers after_update
        for trigger in self._triggers[table_name]["after_update"]:
            trigger(old_record, new_record)
        
        # Invalidar cache
        self._invalidate_cache(table_name)
        
        logger.debug(f"UPDATE en {table_name}: ID={record_id}")
        return True

    def update_where(self, table_name: str, filters: Dict, updates: Dict) -> int:
        """
        Actualiza múltiples registros que coincidan con los filtros.
        
        Args:
            table_name: Nombre de la tabla
            filters: Filtros para seleccionar registros
            updates: Campos a actualizar
        
        Returns:
            Número de registros actualizados
        """
        records = self.select(table_name, filters=filters)
        count = 0
        for record in records:
            pk = self._get_primary_key(table_name)
            if pk and pk in record:
                if self.update(table_name, str(record[pk]), updates):
                    count += 1
        return count

    def delete(self, table_name: str, record_id: str) -> bool:
        """
        Elimina un registro de la tabla.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro a eliminar
        
        Returns:
            True si se eliminó correctamente
        """
        if table_name not in self._tables:
            raise ValueError(f"Tabla '{table_name}' no existe")
        
        record_id = str(record_id)
        if record_id not in self._tables[table_name]:
            return False
        
        old_record = copy.deepcopy(self._tables[table_name][record_id])
        
        # Ejecutar triggers before_delete
        for trigger in self._triggers[table_name]["before_delete"]:
            trigger(old_record)
        
        # Eliminar de índices
        self._remove_from_index(table_name, record_id, old_record)
        
        # Eliminar registro
        del self._tables[table_name][record_id]
        
        # Registrar en audit log
        self._log_audit(table_name, record_id, "DELETE", old_record, None)
        
        # Estadísticas
        self._stats["total_deletes"] += 1
        
        # Ejecutar triggers after_delete
        for trigger in self._triggers[table_name]["after_delete"]:
            trigger(old_record)
        
        # Invalidar cache
        self._invalidate_cache(table_name)
        
        logger.debug(f"DELETE en {table_name}: ID={record_id}")
        return True

    def delete_where(self, table_name: str, filters: Dict) -> int:
        """
        Elimina todos los registros que coincidan con los filtros.
        
        Args:
            table_name: Nombre de la tabla
            filters: Filtros para seleccionar registros
        
        Returns:
            Número de registros eliminados
        """
        records = self.select(table_name, filters=filters)
        count = 0
        pk = self._get_primary_key(table_name)
        for record in records:
            if pk and pk in record:
                if self.delete(table_name, str(record[pk])):
                    count += 1
        return count

    def count(self, table_name: str, filters: Dict = None) -> int:
        """
        Cuenta los registros que coincidan con los filtros.
        
        Args:
            table_name: Nombre de la tabla
            filters: Filtros opcionales
        
        Returns:
            Número de registros
        """
        if filters:
            return len(self.select(table_name, filters=filters))
        return len(self._tables.get(table_name, {}))

    def upsert(self, table_name: str, record: Dict, unique_fields: List[str]) -> str:
        """
        Inserta o actualiza un registro basándose en campos únicos.
        
        Args:
            table_name: Nombre de la tabla
            record: Datos del registro
            unique_fields: Campos que determinan la unicidad
        
        Returns:
            ID del registro insertado/actualizado
        """
        filters = {f: record[f] for f in unique_fields if f in record}
        existing = self.select_one(table_name, filters=filters)
        
        if existing:
            pk = self._get_primary_key(table_name)
            record_id = str(existing.get(pk, ""))
            self.update(table_name, record_id, record)
            return record_id
        else:
            return self.insert(table_name, record)

    # ─────────────────────────────────────────────────────────────────────────
    # OPERACIONES AVANZADAS (JOIN, AGGREGATE, etc.)
    # ─────────────────────────────────────────────────────────────────────────

    def join(self, table_a: str, table_b: str, 
             join_field_a: str, join_field_b: str,
             filters_a: Dict = None, filters_b: Dict = None,
             join_type: str = "INNER") -> List[Dict]:
        """
        Realiza un JOIN entre dos tablas.
        
        Args:
            table_a: Primera tabla
            table_b: Segunda tabla
            join_field_a: Campo de unión en tabla A
            join_field_b: Campo de unión en tabla B
            filters_a: Filtros para tabla A
            filters_b: Filtros para tabla B
            join_type: Tipo de JOIN (INNER, LEFT, RIGHT)
        
        Returns:
            Lista de registros combinados
        """
        records_a = self.select(table_a, filters=filters_a)
        records_b = self.select(table_b, filters=filters_b)
        
        # Construir índice de tabla B para búsqueda eficiente
        index_b = defaultdict(list)
        for rec_b in records_b:
            key = str(rec_b.get(join_field_b, ""))
            index_b[key].append(rec_b)
        
        result = []
        for rec_a in records_a:
            key = str(rec_a.get(join_field_a, ""))
            matching_b = index_b.get(key, [])
            
            if matching_b:
                for rec_b in matching_b:
                    combined = {}
                    # Prefijar campos con el nombre de la tabla para evitar colisiones
                    for k, v in rec_a.items():
                        combined[f"{table_a}.{k}"] = v
                    for k, v in rec_b.items():
                        combined[f"{table_b}.{k}"] = v
                    result.append(combined)
            elif join_type in ("LEFT", "FULL"):
                combined = {}
                for k, v in rec_a.items():
                    combined[f"{table_a}.{k}"] = v
                result.append(combined)
        
        return result

    def aggregate(self, table_name: str, group_by: str, 
                  aggregations: Dict[str, str], filters: Dict = None) -> List[Dict]:
        """
        Realiza operaciones de agregación (GROUP BY).
        
        Args:
            table_name: Nombre de la tabla
            group_by: Campo por el que agrupar
            aggregations: Dict {alias: "FUNC(campo)"} 
                          Funciones: COUNT, SUM, AVG, MAX, MIN, FIRST, LAST
            filters: Filtros previos a la agregación
        
        Returns:
            Lista de grupos con los valores agregados
        """
        records = self.select(table_name, filters=filters)
        
        # Agrupar registros
        groups: Dict[str, List[Dict]] = defaultdict(list)
        for record in records:
            key = str(record.get(group_by, ""))
            groups[key].append(record)
        
        result = []
        for group_key, group_records in groups.items():
            row = {group_by: group_key}
            
            for alias, expr in aggregations.items():
                func_match = re.match(r'(\w+)\((\w+)\)', expr)
                if not func_match:
                    continue
                
                func = func_match.group(1).upper()
                field = func_match.group(2)
                
                values = [r.get(field) for r in group_records if r.get(field) is not None]
                numeric_values = []
                for v in values:
                    try:
                        numeric_values.append(float(v))
                    except (TypeError, ValueError):
                        pass
                
                if func == "COUNT":
                    row[alias] = len(group_records)
                elif func == "SUM" and numeric_values:
                    row[alias] = sum(numeric_values)
                elif func == "AVG" and numeric_values:
                    row[alias] = statistics.mean(numeric_values)
                elif func == "MAX" and numeric_values:
                    row[alias] = max(numeric_values)
                elif func == "MIN" and numeric_values:
                    row[alias] = min(numeric_values)
                elif func == "FIRST" and group_records:
                    row[alias] = group_records[0].get(field)
                elif func == "LAST" and group_records:
                    row[alias] = group_records[-1].get(field)
                elif func == "STDDEV" and len(numeric_values) > 1:
                    row[alias] = statistics.stdev(numeric_values)
                else:
                    row[alias] = None
            
            result.append(row)
        
        return result

    def query(self, sql_like: str) -> List[Dict]:
        """
        Ejecuta una consulta tipo SQL simplificada.
        Soporta: SELECT, FROM, WHERE, ORDER BY, LIMIT, GROUP BY
        
        NOTA: Esta es una implementación simplificada para demostración.
        
        Args:
            sql_like: Consulta en formato SQL simplificado
        
        Returns:
            Lista de registros resultantes
        """
        logger.debug(f"Query ejecutada: {sql_like[:100]}...")
        self._stats["total_queries"] += 1
        
        sql = sql_like.strip().upper()
        
        # Parse básico de SELECT
        table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            return []
        
        table_name = table_match.group(1).lower()
        if table_name not in self._tables:
            return []
        
        # WHERE clause
        filters = {}
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|LIMIT|GROUP|$)', sql, re.IGNORECASE)
        if where_match:
            where_str = where_match.group(1).strip()
            # Parse simple equality conditions
            conditions = where_str.split(' AND ')
            for cond in conditions:
                eq_match = re.match(r'(\w+)\s*=\s*[\'"]?([^\'"]+)[\'"]?', cond.strip())
                if eq_match:
                    filters[eq_match.group(1).lower()] = eq_match.group(2).strip()
        
        # ORDER BY
        order_by = None
        order_match = re.search(r'ORDER\s+BY\s+(\w+)(\s+DESC)?', sql, re.IGNORECASE)
        if order_match:
            order_by = order_match.group(1).lower()
            if order_match.group(2):
                order_by = "-" + order_by
        
        # LIMIT
        limit = None
        limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
        
        return self.select(table_name, filters=filters, order_by=order_by, limit=limit)

    # ─────────────────────────────────────────────────────────────────────────
    # PROCEDIMIENTOS ALMACENADOS SIMULADOS
    # ─────────────────────────────────────────────────────────────────────────

    def sp_get_portfolio_summary(self, portfolio_id: str) -> Dict:
        """
        Stored procedure: Resumen completo del portafolio.
        
        Args:
            portfolio_id: ID del portafolio
        
        Returns:
            Diccionario con métricas del portafolio
        """
        portfolio = self.select_one("portfolios", {"portfolio_id": portfolio_id})
        if not portfolio:
            return {}
        
        positions = self.select("positions", {"portfolio_id": portfolio_id})
        transactions = self.select("transactions", {"portfolio_id": portfolio_id})
        
        total_invested = sum(
            t.get("total_value", 0) 
            for t in transactions 
            if t.get("side") == "BUY"
        )
        
        total_sold = sum(
            t.get("total_value", 0) 
            for t in transactions 
            if t.get("side") == "SELL"
        )
        
        total_positions_value = sum(
            p.get("quantity", 0) * p.get("current_price", 0) 
            for p in positions
        )
        
        total_cost_basis = sum(
            p.get("quantity", 0) * p.get("avg_cost", 0) 
            for p in positions
        )
        
        return {
            "portfolio_id": portfolio_id,
            "name": portfolio.get("name"),
            "cash_balance": portfolio.get("cash_balance", 0),
            "total_positions_value": total_positions_value,
            "total_value": portfolio.get("cash_balance", 0) + total_positions_value,
            "initial_capital": portfolio.get("initial_capital", 0),
            "total_invested": total_invested,
            "total_sold": total_sold,
            "total_cost_basis": total_cost_basis,
            "unrealized_pnl": total_positions_value - total_cost_basis,
            "num_positions": len(positions),
            "num_transactions": len(transactions),
        }

    def sp_get_top_performers(self, limit: int = 10) -> List[Dict]:
        """
        Stored procedure: Obtiene los activos con mejor/peor rendimiento.
        
        Args:
            limit: Número de activos a retornar
        
        Returns:
            Lista de activos ordenados por rendimiento
        """
        data = self.select("market_data", order_by="-change_pct", limit=limit)
        return data

    def sp_get_sector_breakdown(self) -> List[Dict]:
        """
        Stored procedure: Desglose del mercado por sectores.
        
        Returns:
            Lista de sectores con sus estadísticas
        """
        return self.aggregate(
            "tickers",
            group_by="sector",
            aggregations={
                "count": "COUNT(symbol)",
                "avg_change": "AVG(change_pct)",
            }
        )

    def sp_calculate_portfolio_pnl(self, portfolio_id: str) -> Dict:
        """
        Stored procedure: Calcula PnL detallado del portafolio.
        
        Args:
            portfolio_id: ID del portafolio
        
        Returns:
            Diccionario con PnL realizado y no realizado
        """
        transactions = self.select("transactions", {"portfolio_id": portfolio_id})
        positions = self.select("positions", {"portfolio_id": portfolio_id})
        
        realized_pnl = sum(t.get("realized_pnl", 0) for t in transactions if t.get("side") == "SELL")
        
        unrealized_pnl = sum(
            p.get("quantity", 0) * (p.get("current_price", 0) - p.get("avg_cost", 0))
            for p in positions
        )
        
        total_commissions = sum(t.get("commission", 0) for t in transactions)
        
        return {
            "portfolio_id": portfolio_id,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": realized_pnl + unrealized_pnl,
            "total_commissions": total_commissions,
            "net_pnl": realized_pnl + unrealized_pnl - total_commissions,
        }

    def sp_search_tickers(self, query: str) -> List[Dict]:
        """
        Stored procedure: Busca tickers por símbolo o nombre.
        
        Args:
            query: Texto de búsqueda
        
        Returns:
            Lista de tickers que coinciden
        """
        query = query.upper()
        all_tickers = self.select("tickers")
        results = []
        
        for ticker in all_tickers:
            symbol = str(ticker.get("symbol", "")).upper()
            name = str(ticker.get("company_name", "")).upper()
            
            if query in symbol or query in name:
                results.append(ticker)
        
        return results[:20]  # Máximo 20 resultados

    def sp_get_market_movers(self) -> Dict[str, List[Dict]]:
        """
        Stored procedure: Obtiene los mayores movimientos del día.
        
        Returns:
            Diccionario con gainers, losers y most active
        """
        all_data = self.select("market_data")
        
        # Ordenar por cambio porcentual
        sorted_by_change = sorted(
            all_data, 
            key=lambda x: x.get("change_pct", 0),
            reverse=True
        )
        
        # Ordenar por volumen
        sorted_by_volume = sorted(
            all_data,
            key=lambda x: x.get("volume", 0),
            reverse=True
        )
        
        return {
            "top_gainers": sorted_by_change[:5],
            "top_losers": sorted_by_change[-5:][::-1],
            "most_active": sorted_by_volume[:5],
        }

    def sp_get_correlation_matrix(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Stored procedure: Calcula la matriz de correlación entre activos.
        
        Args:
            symbols: Lista de símbolos
        
        Returns:
            Matriz de correlación
        """
        correlations = self.select("correlations")
        
        matrix = {}
        for sym_a in symbols:
            matrix[sym_a] = {}
            for sym_b in symbols:
                if sym_a == sym_b:
                    matrix[sym_a][sym_b] = 1.0
                else:
                    # Buscar correlación en la tabla
                    corr = next(
                        (c.get("correlation", 0) for c in correlations 
                         if c.get("symbol_a") == sym_a and c.get("symbol_b") == sym_b),
                        None
                    )
                    if corr is None:
                        corr = next(
                            (c.get("correlation", 0) for c in correlations 
                             if c.get("symbol_a") == sym_b and c.get("symbol_b") == sym_a),
                            random.uniform(-0.3, 0.8)  # Valor simulado
                        )
                    matrix[sym_a][sym_b] = corr
        
        return matrix

    # ─────────────────────────────────────────────────────────────────────────
    # TRANSACCIONES
    # ─────────────────────────────────────────────────────────────────────────

    def begin_transaction(self) -> None:
        """Inicia una transacción"""
        self._in_transaction = True
        self._transaction_log = []
        logger.debug("Transacción iniciada")

    def commit_transaction(self) -> None:
        """Confirma una transacción"""
        self._in_transaction = False
        self._transaction_log.clear()
        logger.debug("Transacción confirmada")

    def rollback_transaction(self) -> None:
        """
        Revierte una transacción deshaciendo todos los cambios.
        NOTA: En esta implementación simulada, el rollback es básico.
        """
        if self._transaction_log:
            logger.info(f"Rollback: revirtiendo {len(self._transaction_log)} operaciones")
            # Revertir en orden inverso
            for operation in reversed(self._transaction_log):
                try:
                    if operation["type"] == "INSERT":
                        table = operation["table"]
                        record_id = operation["id"]
                        if record_id in self._tables[table]:
                            del self._tables[table][record_id]
                    elif operation["type"] == "UPDATE":
                        table = operation["table"]
                        record_id = operation["id"]
                        old_data = operation["old_data"]
                        if old_data:
                            self._tables[table][record_id] = old_data
                    elif operation["type"] == "DELETE":
                        table = operation["table"]
                        old_data = operation["old_data"]
                        if old_data:
                            pk = self._get_primary_key(table)
                            if pk:
                                record_id = str(old_data.get(pk, ""))
                                self._tables[table][record_id] = old_data
                except Exception as e:
                    logger.error(f"Error en rollback: {e}")
        
        self._in_transaction = False
        self._transaction_log.clear()
        logger.debug("Transacción revertida")

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES INTERNAS
    # ─────────────────────────────────────────────────────────────────────────

    def _apply_filters(self, records: List[Dict], filters: Dict) -> List[Dict]:
        """
        Aplica filtros a una lista de registros.
        Soporta operadores: =, !=, >, <, >=, <=, LIKE, IN, IS NULL, IS NOT NULL
        
        Args:
            records: Lista de registros
            filters: Diccionario de filtros
        
        Returns:
            Lista filtrada
        """
        result = []
        
        for record in records:
            match = True
            for field, condition in filters.items():
                record_value = record.get(field)
                
                if isinstance(condition, tuple) and len(condition) == 2:
                    operator, value = condition
                    operator = operator.upper()
                    
                    if operator == "=" or operator == "==":
                        match = match and (record_value == value)
                    elif operator in ("!=", "<>"):
                        match = match and (record_value != value)
                    elif operator == ">":
                        try:
                            match = match and (float(record_value) > float(value))
                        except (TypeError, ValueError):
                            match = False
                    elif operator == "<":
                        try:
                            match = match and (float(record_value) < float(value))
                        except (TypeError, ValueError):
                            match = False
                    elif operator == ">=":
                        try:
                            match = match and (float(record_value) >= float(value))
                        except (TypeError, ValueError):
                            match = False
                    elif operator == "<=":
                        try:
                            match = match and (float(record_value) <= float(value))
                        except (TypeError, ValueError):
                            match = False
                    elif operator == "LIKE":
                        pattern = str(value).replace("%", ".*").replace("_", ".")
                        match = match and bool(re.match(pattern, str(record_value or ""), re.IGNORECASE))
                    elif operator == "IN":
                        match = match and (record_value in value)
                    elif operator == "NOT IN":
                        match = match and (record_value not in value)
                    elif operator == "IS NULL":
                        match = match and (record_value is None)
                    elif operator == "IS NOT NULL":
                        match = match and (record_value is not None)
                    elif operator == "BETWEEN":
                        try:
                            match = match and (float(value[0]) <= float(record_value) <= float(value[1]))
                        except (TypeError, ValueError):
                            match = False
                    else:
                        match = match and (record_value == condition)
                else:
                    # Igualdad simple
                    if condition is None:
                        match = match and (record_value is None)
                    else:
                        match = match and (str(record_value) == str(condition))
                
                if not match:
                    break
            
            if match:
                result.append(record)
        
        return result

    def _get_primary_key(self, table_name: str) -> Optional[str]:
        """
        Retorna el nombre del campo primary key de una tabla.
        Convención: campo que termina en '_id'
        """
        pk_candidates = {
            "tickers": "ticker_id",
            "price_history": "history_id",
            "real_time_quotes": "quote_id",
            "market_data": "data_id",
            "portfolios": "portfolio_id",
            "positions": "position_id",
            "transactions": "transaction_id",
            "orders": "order_id",
            "price_alerts": "alert_id",
            "watchlists": "watchlist_id",
            "watchlist_symbols": "ws_id",
            "technical_indicators": "indicator_id",
            "market_news": "news_id",
            "economic_calendar": "event_id",
            "performance_metrics": "metric_id",
            "user_settings": "setting_id",
            "audit_log": "log_id",
            "system_logs": "log_id",
            "data_snapshots": "snapshot_id",
            "correlations": "corr_id",
            "sector_performance": "perf_id",
            "dividend_history": "div_id",
            "earnings_calendar": "earning_id",
            "options_chain": "option_id",
        }
        return pk_candidates.get(table_name)

    def _get_field_type(self, table_name: str, field_name: str) -> Optional[str]:
        """Retorna el tipo SQL simulado de un campo"""
        # Heurística simple basada en el nombre del campo
        if field_name.endswith("_id") and field_name != "portfolio_id":
            return "INTEGER PRIMARY KEY"
        elif field_name in ("is_active", "is_triggered", "is_short", "repeat", 
                            "is_default", "is_read", "in_the_money", "is_adjusted",
                            "is_market_hours", "notify_email", "notify_sms"):
            return "BOOLEAN"
        elif field_name in ("created_at", "updated_at", "timestamp", "executed_at",
                            "triggered_at", "logged_at", "performed_at", "added_at"):
            return "DATETIME"
        elif field_name in ("date", "ex_date", "payment_date", "record_date", 
                            "report_date", "event_date"):
            return "DATE"
        elif any(field_name.endswith(s) for s in ("_price", "_value", "_cap", 
                                                    "_yield", "ratio", "alpha",
                                                    "beta", "_pct", "vega", "delta",
                                                    "gamma", "theta", "rho")):
            return "REAL"
        elif any(field_name.endswith(s) for s in ("volume", "quantity", "size", 
                                                     "employees", "_year", "order",
                                                     "interest", "_id")):
            return "INTEGER"
        else:
            return "TEXT"

    def _log_audit(self, table_name: str, record_id: str, action: str,
                   old_data: Optional[Dict], new_data: Optional[Dict]) -> None:
        """
        Registra una operación en el log de auditoría.
        
        Args:
            table_name: Nombre de la tabla
            record_id: ID del registro afectado
            action: Tipo de acción (INSERT, UPDATE, DELETE)
            old_data: Datos anteriores (para UPDATE y DELETE)
            new_data: Datos nuevos (para INSERT y UPDATE)
        """
        entry = {
            "log_id": len(self._audit_log) + 1,
            "table_name": table_name,
            "record_id": str(record_id),
            "action": action,
            "old_values": json.dumps(old_data) if old_data else None,
            "new_values": json.dumps(new_data) if new_data else None,
            "performed_at": datetime.now().isoformat(),
            "user_id": "system",
        }
        
        self._audit_log.append(entry)
        
        # Mantener tamaño máximo
        if len(self._audit_log) > self._max_audit_entries:
            self._audit_log = self._audit_log[-self._max_audit_entries:]

    def _invalidate_cache(self, table_name: str) -> None:
        """Invalida las entradas de cache relacionadas con una tabla"""
        keys_to_remove = [k for k in self._query_cache.keys() if table_name in k]
        for key in keys_to_remove:
            del self._query_cache[key]
            if key in self._cache_ttl:
                del self._cache_ttl[key]

    def get_table_info(self, table_name: str) -> Dict:
        """
        Retorna información sobre una tabla.
        
        Args:
            table_name: Nombre de la tabla
        
        Returns:
            Diccionario con estadísticas de la tabla
        """
        if table_name not in self._tables:
            return {}
        
        records = self._tables[table_name]
        return {
            "name": table_name,
            "record_count": len(records),
            "indexes": list(self._indexes.get(table_name, {}).keys()),
            "size_estimate_bytes": sum(
                len(json.dumps(r, default=str)) 
                for r in records.values()
            ),
        }

    def get_all_table_info(self) -> List[Dict]:
        """Retorna información de todas las tablas"""
        return [self.get_table_info(t) for t in self._tables.keys()]

    def get_database_stats(self) -> Dict:
        """Retorna estadísticas globales de la base de datos"""
        total_records = sum(len(t) for t in self._tables.values())
        total_size = sum(
            sum(len(json.dumps(r, default=str)) for r in t.values())
            for t in self._tables.values()
        )
        
        return {
            "total_tables": len(self._tables),
            "total_records": total_records,
            "total_indexes": sum(len(idx) for idx in self._indexes.values()),
            "estimated_size_bytes": total_size,
            "estimated_size_kb": total_size / 1024,
            "audit_entries": len(self._audit_log),
            "operations": self._stats.copy(),
            "cache_size": len(self._query_cache),
        }

    def export_to_json(self, table_name: str = None) -> str:
        """
        Exporta datos a formato JSON.
        
        Args:
            table_name: Tabla específica o None para todas
        
        Returns:
            String JSON con los datos
        """
        if table_name:
            data = {table_name: list(self._tables.get(table_name, {}).values())}
        else:
            data = {name: list(records.values()) for name, records in self._tables.items()}
        
        return json.dumps(data, default=str, indent=2, ensure_ascii=False)

    def import_from_json(self, json_str: str) -> int:
        """
        Importa datos desde formato JSON.
        
        Args:
            json_str: String JSON con los datos
        
        Returns:
            Número total de registros importados
        """
        data = json.loads(json_str)
        total = 0
        
        for table_name, records in data.items():
            if table_name in self._tables:
                for record in records:
                    try:
                        self.insert(table_name, record)
                        total += 1
                    except Exception as e:
                        logger.warning(f"Error importando registro en {table_name}: {e}")
        
        return total

    # ─────────────────────────────────────────────────────────────────────────
    # DATOS SIMULADOS
    # ─────────────────────────────────────────────────────────────────────────

    def _populate_simulated_data(self) -> None:
        """
        Pobla la base de datos con datos simulados realistas.
        Incluye tickers, historial de precios, portafolios, etc.
        """
        logger.info("Populando datos simulados en base de datos...")
        
        self._populate_tickers()
        self._populate_market_data()
        self._populate_portfolios()
        self._populate_watchlists()
        self._populate_price_alerts()
        self._populate_news()
        self._populate_economic_calendar()
        self._populate_sector_performance()
        self._populate_correlations()
        self._populate_dividend_history()
        self._populate_earnings_calendar()
        self._populate_technical_indicators()
        self._populate_price_history()
        
        logger.info(f"Datos simulados creados. Total: {sum(len(t) for t in self._tables.values())} registros")

    def _populate_tickers(self) -> None:
        """Pobla la tabla de tickers con datos de empresas reales"""
        tickers_data = [
            # Tech
            ("AAPL", "Apple Inc.", "STOCK", "NASDAQ", "Technology", "Consumer Electronics", "US", "USD",
             "US0378331005", "Apple diseña y vende electrónicos, software y servicios.", "https://apple.com",
             "Tim Cook", 164000, 1976),
            ("MSFT", "Microsoft Corporation", "STOCK", "NASDAQ", "Technology", "Software", "US", "USD",
             "US5949181045", "Microsoft desarrolla software y servicios en la nube.", "https://microsoft.com",
             "Satya Nadella", 221000, 1975),
            ("GOOGL", "Alphabet Inc.", "STOCK", "NASDAQ", "Communication Services", "Internet Content", "US", "USD",
             "US02079K3059", "Alphabet es la empresa matriz de Google.", "https://abc.xyz",
             "Sundar Pichai", 182502, 1998),
            ("AMZN", "Amazon.com Inc.", "STOCK", "NASDAQ", "Consumer Discretionary", "Retail", "US", "USD",
             "US0231351067", "Amazon es líder en comercio electrónico y cloud computing.", "https://amazon.com",
             "Andy Jassy", 1541000, 1994),
            ("TSLA", "Tesla Inc.", "STOCK", "NASDAQ", "Consumer Discretionary", "Auto Manufacturers", "US", "USD",
             "US88160R1014", "Tesla fabrica vehículos eléctricos y almacenamiento de energía.", "https://tesla.com",
             "Elon Musk", 127855, 2003),
            ("META", "Meta Platforms Inc.", "STOCK", "NASDAQ", "Communication Services", "Social Media", "US", "USD",
             "US30303M1027", "Meta opera Facebook, Instagram y WhatsApp.", "https://meta.com",
             "Mark Zuckerberg", 86482, 2004),
            ("NVDA", "NVIDIA Corporation", "STOCK", "NASDAQ", "Technology", "Semiconductors", "US", "USD",
             "US67066G1040", "NVIDIA diseña GPUs y chips para IA.", "https://nvidia.com",
             "Jensen Huang", 29600, 1993),
            ("AMD", "Advanced Micro Devices", "STOCK", "NASDAQ", "Technology", "Semiconductors", "US", "USD",
             "US0079031078", "AMD desarrolla microprocesadores y GPUs.", "https://amd.com",
             "Lisa Su", 26000, 1969),
            ("INTC", "Intel Corporation", "STOCK", "NASDAQ", "Technology", "Semiconductors", "US", "USD",
             "US4581401001", "Intel es el mayor fabricante de semiconductores.", "https://intel.com",
             "Pat Gelsinger", 124800, 1968),
            ("NFLX", "Netflix Inc.", "STOCK", "NASDAQ", "Communication Services", "Entertainment", "US", "USD",
             "US64110L1061", "Netflix es la plataforma de streaming líder mundial.", "https://netflix.com",
             "Ted Sarandos", 13000, 1997),
            # Finance
            ("JPM", "JPMorgan Chase & Co.", "STOCK", "NYSE", "Financials", "Banking", "US", "USD",
             "US46625H1005", "JPMorgan es el mayor banco de EE.UU.", "https://jpmorganchase.com",
             "Jamie Dimon", 293723, 1799),
            ("BAC", "Bank of America Corp.", "STOCK", "NYSE", "Financials", "Banking", "US", "USD",
             "US0605051046", "Bank of America es uno de los mayores bancos del mundo.", "https://bankofamerica.com",
             "Brian Moynihan", 213000, 1904),
            ("GS", "Goldman Sachs Group Inc.", "STOCK", "NYSE", "Financials", "Investment Banking", "US", "USD",
             "US38141G1040", "Goldman Sachs es banco de inversión líder global.", "https://goldmansachs.com",
             "David Solomon", 45400, 1869),
            ("V", "Visa Inc.", "STOCK", "NYSE", "Financials", "Payments", "US", "USD",
             "US92826C8394", "Visa opera la red de pagos digitales más grande.", "https://visa.com",
             "Ryan McInerney", 26500, 1958),
            ("MA", "Mastercard Incorporated", "STOCK", "NYSE", "Financials", "Payments", "US", "USD",
             "US57636Q1040", "Mastercard es red de pagos global.", "https://mastercard.com",
             "Michael Miebach", 29900, 1966),
            # Healthcare
            ("JNJ", "Johnson & Johnson", "STOCK", "NYSE", "Healthcare", "Drug Manufacturers", "US", "USD",
             "US4781601046", "J&J es empresa farmacéutica y de dispositivos médicos.", "https://jnj.com",
             "Joaquin Duato", 152700, 1886),
            ("PFE", "Pfizer Inc.", "STOCK", "NYSE", "Healthcare", "Drug Manufacturers", "US", "USD",
             "US7170811035", "Pfizer es una de las mayores farmacéuticas del mundo.", "https://pfizer.com",
             "Albert Bourla", 83000, 1849),
            ("UNH", "UnitedHealth Group Inc.", "STOCK", "NYSE", "Healthcare", "Health Insurance", "US", "USD",
             "US91324P1021", "UnitedHealth es la mayor aseguradora médica de EE.UU.", "https://unitedhealthgroup.com",
             "Andrew Witty", 400000, 1977),
            # Energy
            ("XOM", "Exxon Mobil Corporation", "STOCK", "NYSE", "Energy", "Oil & Gas", "US", "USD",
             "US30231G1022", "ExxonMobil es la mayor empresa petrolera de EE.UU.", "https://exxonmobil.com",
             "Darren Woods", 62000, 1870),
            ("CVX", "Chevron Corporation", "STOCK", "NYSE", "Energy", "Oil & Gas", "US", "USD",
             "US1667641005", "Chevron es empresa energética integrada global.", "https://chevron.com",
             "Mike Wirth", 43846, 1879),
            # ETFs
            ("SPY", "SPDR S&P 500 ETF Trust", "ETF", "NYSE Arca", "Diversified", "Large Blend", "US", "USD",
             "US78462F1030", "ETF que replica el índice S&P 500.", "https://ssga.com",
             None, None, 1993),
            ("QQQ", "Invesco QQQ Trust", "ETF", "NASDAQ", "Technology", "Large Blend", "US", "USD",
             "US46090E1038", "ETF que replica el índice Nasdaq-100.", "https://invesco.com",
             None, None, 1999),
            ("DIA", "SPDR Dow Jones Industrial Average ETF", "ETF", "NYSE Arca", "Diversified", "Large Blend", "US", "USD",
             "US78467X1090", "ETF que replica el Dow Jones.", "https://ssga.com",
             None, None, 1998),
            # Crypto
            ("BTC-USD", "Bitcoin USD", "CRYPTO", "CoinMarketCap", "Cryptocurrency", "Currency", "GLOBAL", "USD",
             None, "Bitcoin es la primera y mayor criptomoneda.", "https://bitcoin.org",
             "Satoshi Nakamoto", None, 2009),
            ("ETH-USD", "Ethereum USD", "CRYPTO", "CoinMarketCap", "Cryptocurrency", "Smart Contracts", "GLOBAL", "USD",
             None, "Ethereum es plataforma de contratos inteligentes.", "https://ethereum.org",
             "Vitalik Buterin", None, 2015),
            ("BNB-USD", "BNB USD", "CRYPTO", "CoinMarketCap", "Cryptocurrency", "Exchange Token", "GLOBAL", "USD",
             None, "BNB es el token nativo de Binance.", "https://binance.com",
             None, None, 2017),
            # Consumer
            ("WMT", "Walmart Inc.", "STOCK", "NYSE", "Consumer Staples", "Retail", "US", "USD",
             "US9311421039", "Walmart es la mayor cadena minorista del mundo.", "https://walmart.com",
             "Doug McMillon", 2300000, 1945),
            ("KO", "The Coca-Cola Company", "STOCK", "NYSE", "Consumer Staples", "Beverages", "US", "USD",
             "US1912161007", "Coca-Cola produce bebidas no alcohólicas.", "https://coca-colacompany.com",
             "James Quincey", 79000, 1892),
            ("MCD", "McDonald's Corporation", "STOCK", "NYSE", "Consumer Discretionary", "Restaurants", "US", "USD",
             "US5801351017", "McDonald's es la cadena de restaurantes más grande.", "https://mcdonalds.com",
             "Chris Kempczinski", 200000, 1940),
            ("DIS", "The Walt Disney Company", "STOCK", "NYSE", "Communication Services", "Entertainment", "US", "USD",
             "US2546871060", "Disney es empresa de entretenimiento y medios.", "https://thewaltdisneycompany.com",
             "Bob Iger", 220000, 1923),
        ]
        
        for i, data in enumerate(tickers_data):
            (symbol, name, asset_type, exchange, sector, industry, country, currency,
             isin, description, website, ceo, employees, founded) = data
            
            self.insert("tickers", {
                "ticker_id": i + 1,
                "symbol": symbol,
                "company_name": name,
                "asset_type": asset_type,
                "exchange": exchange,
                "sector": sector,
                "industry": industry,
                "country": country,
                "currency": currency,
                "isin": isin or "",
                "description": description,
                "website": website,
                "ceo": ceo or "N/A",
                "employees": employees or 0,
                "founded_year": founded or 0,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })

    def _populate_market_data(self) -> None:
        """Pobla la tabla de datos de mercado con precios simulados"""
        market_data = [
            # symbol, price, open, prev_close, high, low, volume, avg_vol, mkt_cap, pe, eps, div_yield, beta, 52h, 52l, currency
            ("AAPL", 189.30, 187.50, 186.20, 190.15, 186.80, 62_450_000, 58_000_000, 2_950_000_000_000, 28.5, 6.43, 0.52, 1.28, 199.62, 142.17, "USD"),
            ("MSFT", 415.20, 412.00, 410.50, 417.80, 411.20, 28_300_000, 25_000_000, 3_080_000_000_000, 35.2, 11.45, 0.72, 0.89, 430.82, 310.34, "USD"),
            ("GOOGL", 175.80, 173.20, 172.40, 176.90, 173.00, 22_100_000, 20_500_000, 2_200_000_000_000, 24.8, 6.52, 0.0, 1.05, 193.31, 115.83, "USD"),
            ("AMZN", 195.40, 192.30, 190.80, 196.50, 192.10, 45_600_000, 40_000_000, 2_050_000_000_000, 52.3, 3.17, 0.0, 1.18, 201.20, 112.54, "USD"),
            ("TSLA", 242.80, 238.00, 236.50, 245.30, 237.20, 125_000_000, 115_000_000, 775_000_000_000, 68.4, 3.56, 0.0, 2.15, 299.29, 138.80, "USD"),
            ("META", 528.50, 524.00, 521.30, 531.20, 522.80, 18_900_000, 17_500_000, 1_350_000_000_000, 24.1, 21.90, 0.30, 1.21, 545.06, 279.40, "USD"),
            ("NVDA", 875.40, 869.20, 865.50, 880.10, 867.30, 52_300_000, 48_000_000, 2_160_000_000_000, 62.8, 13.53, 0.03, 1.68, 974.00, 395.42, "USD"),
            ("AMD", 162.30, 159.80, 158.40, 163.90, 158.90, 71_400_000, 65_000_000, 263_000_000_000, 185.3, 0.84, 0.0, 1.72, 227.30, 96.38, "USD"),
            ("INTC", 38.20, 37.50, 37.10, 38.80, 37.30, 48_200_000, 45_000_000, 162_000_000_000, 42.1, 0.85, 1.46, 0.95, 51.28, 25.55, "USD"),
            ("NFLX", 685.40, 679.20, 675.80, 688.50, 678.40, 8_900_000, 8_200_000, 296_000_000_000, 39.8, 17.21, 0.0, 1.22, 700.99, 344.73, "USD"),
            ("JPM", 198.50, 196.30, 195.10, 199.80, 195.50, 15_600_000, 14_200_000, 579_000_000_000, 12.1, 16.24, 2.10, 1.15, 205.88, 139.26, "USD"),
            ("BAC", 38.90, 38.20, 37.80, 39.30, 38.00, 42_100_000, 39_000_000, 307_000_000_000, 13.5, 2.88, 2.50, 1.43, 44.44, 24.75, "USD"),
            ("GS", 452.30, 448.00, 445.20, 455.10, 447.50, 4_200_000, 3_900_000, 148_000_000_000, 13.8, 32.78, 2.40, 1.28, 478.65, 293.22, "USD"),
            ("V", 278.40, 275.20, 273.80, 279.80, 274.50, 9_800_000, 9_100_000, 580_000_000_000, 30.5, 9.12, 0.76, 0.97, 290.96, 215.25, "USD"),
            ("MA", 487.60, 483.40, 480.90, 489.30, 482.50, 4_100_000, 3_800_000, 461_000_000_000, 34.2, 14.23, 0.55, 1.06, 508.76, 360.52, "USD"),
            ("JNJ", 155.40, 153.80, 152.90, 156.20, 153.20, 8_900_000, 8_300_000, 373_000_000_000, 17.2, 9.01, 3.05, 0.56, 175.97, 143.13, "USD"),
            ("PFE", 28.50, 28.00, 27.80, 28.90, 27.70, 32_400_000, 30_000_000, 161_000_000_000, 11.4, 2.50, 5.89, 0.60, 38.62, 25.20, "USD"),
            ("UNH", 512.80, 508.40, 505.90, 515.30, 507.20, 4_500_000, 4_100_000, 476_000_000_000, 23.1, 22.20, 1.42, 0.53, 570.97, 445.69, "USD"),
            ("XOM", 112.40, 110.90, 110.20, 113.10, 110.60, 24_300_000, 22_500_000, 476_000_000_000, 14.2, 7.92, 3.20, 0.85, 123.75, 93.56, "USD"),
            ("CVX", 158.20, 156.40, 155.80, 159.30, 155.90, 12_100_000, 11_200_000, 294_000_000_000, 13.8, 11.46, 4.02, 1.04, 182.40, 139.60, "USD"),
            ("SPY", 528.90, 525.40, 523.80, 530.20, 524.80, 98_000_000, 91_000_000, 0, 24.5, 0.0, 1.28, 1.0, 543.09, 410.42, "USD"),
            ("QQQ", 451.20, 448.30, 446.80, 452.60, 447.50, 62_000_000, 57_000_000, 0, 29.8, 0.0, 0.52, 1.06, 467.69, 326.19, "USD"),
            ("DIA", 389.40, 387.20, 386.10, 390.80, 386.50, 12_000_000, 10_500_000, 0, 21.4, 0.0, 1.68, 0.98, 400.31, 309.92, "USD"),
            ("BTC-USD", 68450.00, 67200.00, 66800.00, 69100.00, 66500.00, 28_900_000_000, 25_000_000_000, 1_346_000_000_000, 0, 0, 0, 0.68, 73750.00, 26000.00, "USD"),
            ("ETH-USD", 3520.00, 3480.00, 3450.00, 3560.00, 3440.00, 18_500_000_000, 16_000_000_000, 423_000_000_000, 0, 0, 0, 0.82, 4090.00, 1520.00, "USD"),
            ("BNB-USD", 485.00, 478.00, 475.00, 490.00, 472.00, 1_250_000_000, 980_000_000, 75_000_000_000, 0, 0, 0, 0.75, 635.00, 210.00, "USD"),
            ("WMT", 68.40, 67.80, 67.50, 68.90, 67.30, 18_200_000, 16_800_000, 550_000_000_000, 29.8, 2.29, 1.21, 0.52, 73.50, 48.24, "USD"),
            ("KO", 61.20, 60.80, 60.50, 61.60, 60.40, 15_400_000, 14_200_000, 264_000_000_000, 23.4, 2.62, 3.20, 0.56, 64.99, 54.13, "USD"),
            ("MCD", 295.40, 292.80, 291.50, 296.80, 292.20, 6_800_000, 6_200_000, 214_000_000_000, 24.8, 11.92, 2.28, 0.72, 317.90, 245.62, "USD"),
            ("DIS", 112.80, 111.20, 110.80, 113.50, 110.90, 14_200_000, 13_100_000, 205_000_000_000, 42.5, 2.65, 0.0, 1.38, 123.74, 78.73, "USD"),
        ]
        
        for i, data in enumerate(market_data):
            (sym, price, open_p, prev_c, high, low, vol, avg_vol, mkt_cap,
             pe, eps, div_yield, beta, w52h, w52l, currency) = data
            
            change = price - prev_c
            change_pct = (change / prev_c) * 100 if prev_c != 0 else 0
            
            self.insert("market_data", {
                "data_id": i + 1,
                "symbol": sym,
                "price": round(price, 2),
                "open_price": round(open_p, 2),
                "prev_close": round(prev_c, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": vol,
                "avg_volume": avg_vol,
                "market_cap": mkt_cap,
                "pe_ratio": pe,
                "eps": eps,
                "dividend_yield": div_yield,
                "beta": beta,
                "week_52_high": w52h,
                "week_52_low": w52l,
                "currency": currency,
                "timestamp": datetime.now().isoformat(),
                "is_market_hours": True,
            })

    def _populate_portfolios(self) -> None:
        """Pobla portafolios de ejemplo"""
        portfolios = [
            {
                "portfolio_id": "port-001",
                "name": "Portafolio Principal",
                "description": "Mi portafolio de inversión principal",
                "currency": "USD",
                "initial_capital": 100000.0,
                "cash_balance": 32450.80,
                "is_active": True,
                "created_at": (datetime.now() - timedelta(days=365)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Estrategia de crecimiento a largo plazo",
                "benchmark": "SPY",
                "strategy": "Growth"
            },
            {
                "portfolio_id": "port-002",
                "name": "Portafolio Dividendos",
                "description": "Enfocado en acciones que pagan dividendos",
                "currency": "USD",
                "initial_capital": 50000.0,
                "cash_balance": 8920.50,
                "is_active": True,
                "created_at": (datetime.now() - timedelta(days=180)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Generar ingreso pasivo con dividendos",
                "benchmark": "DIA",
                "strategy": "Income"
            },
            {
                "portfolio_id": "port-003",
                "name": "Portafolio Especulativo",
                "description": "Para trades de alto riesgo",
                "currency": "USD",
                "initial_capital": 20000.0,
                "cash_balance": 5200.00,
                "is_active": True,
                "created_at": (datetime.now() - timedelta(days=90)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": "Alto riesgo / alta recompensa",
                "benchmark": "QQQ",
                "strategy": "Speculative"
            },
        ]
        
        for port in portfolios:
            self.insert("portfolios", port)
        
        # Posiciones del portafolio principal
        positions = [
            {
                "position_id": "pos-001",
                "portfolio_id": "port-001",
                "symbol": "AAPL",
                "quantity": 50.0,
                "avg_cost": 165.30,
                "current_price": 189.30,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=300)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Posición core en Apple",
            },
            {
                "position_id": "pos-002",
                "portfolio_id": "port-001",
                "symbol": "MSFT",
                "quantity": 30.0,
                "avg_cost": 385.50,
                "current_price": 415.20,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=250)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Microsoft - apuesta en cloud",
            },
            {
                "position_id": "pos-003",
                "portfolio_id": "port-001",
                "symbol": "NVDA",
                "quantity": 20.0,
                "avg_cost": 650.00,
                "current_price": 875.40,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=180)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "NVIDIA - juego en IA",
            },
            {
                "position_id": "pos-004",
                "portfolio_id": "port-001",
                "symbol": "BTC-USD",
                "quantity": 0.5,
                "avg_cost": 52000.00,
                "current_price": 68450.00,
                "asset_type": "CRYPTO",
                "opened_at": (datetime.now() - timedelta(days=120)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Bitcoin - cobertura inflacionaria",
            },
            {
                "position_id": "pos-005",
                "portfolio_id": "port-001",
                "symbol": "SPY",
                "quantity": 40.0,
                "avg_cost": 490.00,
                "current_price": 528.90,
                "asset_type": "ETF",
                "opened_at": (datetime.now() - timedelta(days=365)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "ETF S&P 500 - base del portafolio",
            },
            # Portafolio dividendos
            {
                "position_id": "pos-006",
                "portfolio_id": "port-002",
                "symbol": "JNJ",
                "quantity": 100.0,
                "avg_cost": 148.50,
                "current_price": 155.40,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=150)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Johnson & Johnson - dividendo estable",
            },
            {
                "position_id": "pos-007",
                "portfolio_id": "port-002",
                "symbol": "KO",
                "quantity": 200.0,
                "avg_cost": 58.90,
                "current_price": 61.20,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=120)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Coca-Cola - dividendo aristocrat",
            },
            {
                "position_id": "pos-008",
                "portfolio_id": "port-002",
                "symbol": "CVX",
                "quantity": 80.0,
                "avg_cost": 148.30,
                "current_price": 158.20,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=90)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Chevron - alto dividendo en energía",
            },
            # Portafolio especulativo
            {
                "position_id": "pos-009",
                "portfolio_id": "port-003",
                "symbol": "TSLA",
                "quantity": 25.0,
                "avg_cost": 215.00,
                "current_price": 242.80,
                "asset_type": "STOCK",
                "opened_at": (datetime.now() - timedelta(days=60)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Tesla - apuesta especulativa",
            },
            {
                "position_id": "pos-010",
                "portfolio_id": "port-003",
                "symbol": "ETH-USD",
                "quantity": 2.0,
                "avg_cost": 2980.00,
                "current_price": 3520.00,
                "asset_type": "CRYPTO",
                "opened_at": (datetime.now() - timedelta(days=45)).isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_short": False,
                "notes": "Ethereum - apuesta DeFi",
            },
        ]
        
        for pos in positions:
            self.insert("positions", pos)
        
        # Transacciones históricas
        transactions = [
            {
                "transaction_id": f"txn-{i:04d}",
                "portfolio_id": "port-001",
                "symbol": sym,
                "side": side,
                "order_type": "MARKET",
                "quantity": qty,
                "price": price,
                "total_value": round(qty * price, 2),
                "commission": round(qty * price * 0.001, 2),
                "executed_at": (datetime.now() - timedelta(days=days)).isoformat(),
                "status": "FILLED",
                "notes": notes,
                "realized_pnl": pnl,
            }
            for i, (sym, side, qty, price, days, notes, pnl) in enumerate([
                ("AAPL", "BUY", 50, 165.30, 300, "Compra inicial AAPL", 0),
                ("MSFT", "BUY", 30, 385.50, 250, "Compra inicial MSFT", 0),
                ("GOOGL", "BUY", 20, 148.20, 200, "Compra GOOGL", 0),
                ("GOOGL", "SELL", 20, 165.80, 150, "Venta GOOGL con ganancia", 348.0),
                ("NVDA", "BUY", 20, 650.00, 180, "Compra NVDA inicio AI boom", 0),
                ("TSLA", "BUY", 15, 195.40, 120, "Compra TSLA", 0),
                ("TSLA", "SELL", 15, 225.80, 80, "Venta TSLA con ganancia", 456.0),
                ("BTC-USD", "BUY", 0.5, 52000, 120, "Compra BTC", 0),
                ("SPY", "BUY", 40, 490.00, 365, "Compra SPY base", 0),
                ("AMZN", "BUY", 25, 178.30, 160, "Compra AMZN", 0),
                ("AMZN", "SELL", 25, 190.50, 90, "Venta AMZN", 305.0),
                ("META", "BUY", 10, 495.20, 100, "Compra META", 0),
                ("META", "SELL", 10, 515.40, 50, "Venta META con ganancia", 202.0),
            ])
        ]
        
        for txn in transactions:
            self.insert("transactions", txn)

    def _populate_watchlists(self) -> None:
        """Pobla las listas de seguimiento"""
        watchlists = [
            {
                "watchlist_id": "wl-001",
                "name": "Tecnología",
                "description": "Acciones tecnológicas principales",
                "color": "#1f538d",
                "icon": "💻",
                "is_default": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "watchlist_id": "wl-002",
                "name": "Criptomonedas",
                "description": "Principales criptomonedas",
                "color": "#f7931a",
                "icon": "₿",
                "is_default": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "watchlist_id": "wl-003",
                "name": "Dividendos",
                "description": "Acciones con alto dividendo",
                "color": "#2ed573",
                "icon": "💰",
                "is_default": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "watchlist_id": "wl-004",
                "name": "ETFs",
                "description": "Fondos indexados",
                "color": "#ff4757",
                "icon": "📊",
                "is_default": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        ]
        
        for wl in watchlists:
            self.insert("watchlists", wl)
        
        # Símbolos por watchlist
        wl_symbols = [
            # Tecnología
            ("wl-001", "AAPL"), ("wl-001", "MSFT"), ("wl-001", "GOOGL"),
            ("wl-001", "NVDA"), ("wl-001", "AMD"), ("wl-001", "INTC"),
            ("wl-001", "META"), ("wl-001", "NFLX"), ("wl-001", "AMZN"),
            # Cripto
            ("wl-002", "BTC-USD"), ("wl-002", "ETH-USD"), ("wl-002", "BNB-USD"),
            # Dividendos
            ("wl-003", "JNJ"), ("wl-003", "KO"), ("wl-003", "CVX"),
            ("wl-003", "XOM"), ("wl-003", "PFE"), ("wl-003", "JPM"),
            # ETFs
            ("wl-004", "SPY"), ("wl-004", "QQQ"), ("wl-004", "DIA"),
        ]
        
        for i, (wl_id, symbol) in enumerate(wl_symbols):
            self.insert("watchlist_symbols", {
                "ws_id": i + 1,
                "watchlist_id": wl_id,
                "symbol": symbol,
                "added_at": datetime.now().isoformat(),
                "sort_order": i,
            })

    def _populate_price_alerts(self) -> None:
        """Pobla alertas de precio de ejemplo"""
        alerts = [
            {
                "alert_id": "alr-001",
                "symbol": "AAPL",
                "alert_type": "PRICE_ABOVE",
                "threshold": 200.00,
                "message": "AAPL superó los $200",
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "repeat": False,
                "priority": "HIGH",
                "portfolio_id": "port-001",
            },
            {
                "alert_id": "alr-002",
                "symbol": "BTC-USD",
                "alert_type": "PRICE_ABOVE",
                "threshold": 70000.00,
                "message": "Bitcoin superó los $70,000",
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "repeat": True,
                "priority": "CRITICAL",
            },
            {
                "alert_id": "alr-003",
                "symbol": "TSLA",
                "alert_type": "PRICE_BELOW",
                "threshold": 220.00,
                "message": "TSLA cayó por debajo de $220",
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "repeat": False,
                "priority": "MEDIUM",
            },
            {
                "alert_id": "alr-004",
                "symbol": "SPY",
                "alert_type": "PERCENT_CHANGE",
                "threshold": 2.0,
                "message": "SPY movimiento > 2% en el día",
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "repeat": True,
                "priority": "MEDIUM",
            },
            {
                "alert_id": "alr-005",
                "symbol": "NVDA",
                "alert_type": "PRICE_ABOVE",
                "threshold": 900.00,
                "message": "NVDA sobre $900 - evaluar toma de ganancias",
                "is_active": True,
                "is_triggered": False,
                "created_at": datetime.now().isoformat(),
                "repeat": False,
                "priority": "HIGH",
            },
        ]
        
        for alert in alerts:
            self.insert("price_alerts", alert)

    def _populate_news(self) -> None:
        """Pobla noticias de mercado simuladas"""
        news_items = [
            {
                "news_id": f"news-{i:04d}",
                "title": title,
                "summary": summary,
                "url": f"https://financenews.com/article-{i}",
                "source": source,
                "published_at": (datetime.now() - timedelta(hours=h)).isoformat(),
                "sentiment": sentiment,
                "impact": impact,
                "is_read": False,
                "related_symbols": json.dumps(symbols),
            }
            for i, (title, summary, source, h, sentiment, impact, symbols) in enumerate([
                ("Apple reporta ganancias récord en Q4", 
                 "Apple superó las expectativas con ingresos de $120B en el trimestre.",
                 "Reuters", 2, "POSITIVE", "HIGH", ["AAPL"]),
                ("Fed mantiene tasas sin cambios",
                 "La Reserva Federal mantuvo las tasas de interés en 5.25-5.5%.",
                 "Bloomberg", 4, "NEUTRAL", "HIGH", ["SPY", "QQQ", "DIA"]),
                ("NVIDIA lanza nuevas GPUs para IA",
                 "NVIDIA presentó la arquitectura Blackwell para centros de datos.",
                 "CNBC", 6, "POSITIVE", "HIGH", ["NVDA", "AMD"]),
                ("Bitcoin alcanza máximo histórico",
                 "BTC superó los $73,000 impulsado por los ETF spot.",
                 "CoinDesk", 8, "POSITIVE", "HIGH", ["BTC-USD", "ETH-USD"]),
                ("Tesla reduce precios en Europa",
                 "Tesla bajó precios en modelos S y X en mercados europeos.",
                 "Reuters", 10, "NEGATIVE", "MEDIUM", ["TSLA"]),
                ("Microsoft Azure crece 30% anual",
                 "Azure, la nube de Microsoft, reportó crecimiento de 30% interanual.",
                 "Bloomberg", 12, "POSITIVE", "HIGH", ["MSFT"]),
                ("Goldman Sachs sube precio objetivo de NVDA a $1,100",
                 "Los analistas de Goldman elevaron su precio objetivo para NVIDIA.",
                 "MarketWatch", 14, "POSITIVE", "MEDIUM", ["NVDA"]),
                ("Meta anuncia nuevas inversiones en IA",
                 "Meta planea invertir $40B en infraestructura de IA este año.",
                 "CNBC", 16, "POSITIVE", "HIGH", ["META"]),
                ("PFE retrasa lanzamiento de nuevo medicamento",
                 "Pfizer anunció retrasos en el proceso de aprobación FDA.",
                 "Reuters", 18, "NEGATIVE", "MEDIUM", ["PFE"]),
                ("Datos de empleo superan expectativas",
                 "Creación de empleo en EE.UU. fue de 275K vs 185K esperados.",
                 "Bloomberg", 20, "POSITIVE", "HIGH", ["SPY", "QQQ"]),
                ("Amazon anuncia expansión en logística",
                 "Amazon invertirá $15B en nueva infraestructura logística.",
                 "WSJ", 22, "POSITIVE", "MEDIUM", ["AMZN"]),
                ("Intel pierde cuota de mercado en servidores",
                 "AMD y ARM ganan terreno frente a Intel en datacenter.",
                 "Reuters", 24, "NEGATIVE", "MEDIUM", ["INTC", "AMD"]),
                ("J&J gana litigio por talco",
                 "Johnson & Johnson ganó demanda clave relacionada con polvos de talco.",
                 "Bloomberg", 26, "POSITIVE", "HIGH", ["JNJ"]),
                ("Ethereum actualización exitosa",
                 "La actualización Dencun de Ethereum redujo costos de transacción.",
                 "CoinDesk", 28, "POSITIVE", "HIGH", ["ETH-USD"]),
                ("Chevron aumenta dividendo trimestral",
                 "CVX anunció incremento de 8% en su dividendo trimestral.",
                 "MarketWatch", 30, "POSITIVE", "MEDIUM", ["CVX", "XOM"]),
            ])
        ]
        
        for news in news_items:
            self.insert("market_news", news)

    def _populate_economic_calendar(self) -> None:
        """Pobla el calendario económico"""
        events = [
            {
                "event_id": i + 1,
                "event_name": name,
                "country": country,
                "event_date": (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d %H:%M:00"),
                "impact": impact,
                "previous": prev,
                "forecast": fore,
                "actual": actual,
                "currency": curr,
                "description": desc,
            }
            for i, (name, country, offset, impact, prev, fore, actual, curr, desc) in enumerate([
                ("Non-Farm Payrolls", "US", 3, "HIGH", "215K", "225K", "", "USD", "Creación de empleo no agrícola"),
                ("CPI (Inflación)", "US", 5, "HIGH", "3.2%", "3.1%", "", "USD", "Índice de precios al consumidor"),
                ("FOMC Meeting", "US", 7, "HIGH", "5.25-5.5%", "5.25-5.5%", "", "USD", "Decisión de tasas Fed"),
                ("GDP Q4 (Final)", "US", 10, "HIGH", "3.2%", "3.3%", "", "USD", "PIB trimestral final"),
                ("Retail Sales", "US", 12, "MEDIUM", "0.3%", "0.4%", "", "USD", "Ventas minoristas"),
                ("Initial Jobless Claims", "US", 14, "MEDIUM", "218K", "215K", "", "USD", "Solicitudes desempleo"),
                ("PMI Manufacturing", "US", 16, "MEDIUM", "52.1", "52.5", "", "USD", "Índice gerentes de compra"),
                ("Consumer Confidence", "US", 18, "MEDIUM", "104.7", "105.0", "", "USD", "Confianza del consumidor"),
                ("Trade Balance", "US", 20, "LOW", "-67.4B", "-65.0B", "", "USD", "Balanza comercial"),
                ("Housing Starts", "US", 22, "MEDIUM", "1.42M", "1.45M", "", "USD", "Inicio de construcciones"),
                ("ECB Rate Decision", "EU", 8, "HIGH", "4.0%", "3.75%", "", "EUR", "Decisión tasas BCE"),
                ("UK CPI", "UK", 6, "HIGH", "3.4%", "3.2%", "", "GBP", "Inflación Reino Unido"),
                ("Japan GDP", "JP", 15, "HIGH", "0.1%", "0.4%", "", "JPY", "PIB Japón"),
                ("China PMI", "CN", 4, "HIGH", "49.8", "50.1", "", "CNY", "PMI China"),
                ("Earnings: AAPL", "US", 2, "HIGH", "$2.18", "$2.05", "", "USD", "Reporte ganancias Apple"),
                ("Earnings: MSFT", "US", 3, "HIGH", "$2.93", "$2.82", "", "USD", "Reporte ganancias Microsoft"),
                ("Earnings: GOOGL", "US", 4, "HIGH", "$1.64", "$1.53", "", "USD", "Reporte ganancias Alphabet"),
                ("Earnings: NVDA", "US", 9, "HIGH", "$5.16", "$4.98", "", "USD", "Reporte ganancias NVIDIA"),
                ("Crude Oil Inventories", "US", 1, "MEDIUM", "-2.1M", "-1.5M", "", "USD", "Inventarios petróleo crudo"),
                ("PPI (Precios Productor)", "US", 11, "MEDIUM", "0.2%", "0.3%", "", "USD", "Índice precios productor"),
            ])
        ]
        
        for event in events:
            self.insert("economic_calendar", event)

    def _populate_sector_performance(self) -> None:
        """Pobla el rendimiento por sectores"""
        sector_data = [
            ("Technology", 1.45, 3.20, 8.50, 22.40, 11_500_000_000_000),
            ("Healthcare", -0.32, 0.85, 2.10, 5.80, 3_200_000_000_000),
            ("Financials", 0.78, 1.95, 5.30, 12.60, 4_100_000_000_000),
            ("Consumer Discretionary", 0.52, 1.20, 3.80, 9.20, 2_800_000_000_000),
            ("Communication Services", 1.12, 2.40, 6.80, 18.30, 3_500_000_000_000),
            ("Industrials", 0.25, 0.90, 2.50, 7.40, 2_200_000_000_000),
            ("Consumer Staples", -0.18, 0.40, 1.20, 3.80, 1_800_000_000_000),
            ("Energy", 0.65, 2.10, 7.20, 15.60, 2_400_000_000_000),
            ("Utilities", -0.45, -0.80, -1.50, -3.20, 950_000_000_000),
            ("Real Estate", -0.28, -0.60, -2.10, -5.40, 1_100_000_000_000),
            ("Materials", 0.38, 1.05, 3.40, 8.90, 890_000_000_000),
        ]
        
        for i, (sector, daily, weekly, monthly, ytd, mkt_cap) in enumerate(sector_data):
            self.insert("sector_performance", {
                "perf_id": i + 1,
                "sector": sector,
                "daily_change": daily,
                "weekly_change": weekly,
                "monthly_change": monthly,
                "ytd_change": ytd,
                "market_cap": mkt_cap,
                "timestamp": datetime.now().isoformat(),
            })

    def _populate_correlations(self) -> None:
        """Pobla correlaciones entre activos"""
        correlations = [
            ("AAPL", "MSFT", 0.82),
            ("AAPL", "GOOGL", 0.75),
            ("AAPL", "NVDA", 0.68),
            ("MSFT", "GOOGL", 0.79),
            ("MSFT", "NVDA", 0.71),
            ("GOOGL", "META", 0.73),
            ("AAPL", "SPY", 0.88),
            ("MSFT", "SPY", 0.85),
            ("SPY", "QQQ", 0.95),
            ("BTC-USD", "ETH-USD", 0.92),
            ("BTC-USD", "SPY", 0.32),
            ("TSLA", "SPY", 0.65),
            ("TSLA", "BTC-USD", 0.48),
            ("XOM", "CVX", 0.94),
            ("JPM", "BAC", 0.88),
            ("JNJ", "PFE", 0.62),
            ("KO", "WMT", 0.55),
            ("AAPL", "KO", 0.22),
            ("BTC-USD", "XOM", -0.12),
            ("INTC", "AMD", 0.75),
        ]
        
        for i, (sym_a, sym_b, corr) in enumerate(correlations):
            self.insert("correlations", {
                "corr_id": i + 1,
                "symbol_a": sym_a,
                "symbol_b": sym_b,
                "correlation": corr,
                "period": "1y",
                "calculated_at": datetime.now().isoformat(),
            })

    def _populate_dividend_history(self) -> None:
        """Pobla historial de dividendos"""
        dividends = [
            # symbol, ex_date, payment, record, amount, frequency, type
            ("AAPL", "2024-02-09", "2024-02-15", "2024-02-12", 0.24, "QUARTERLY", "REGULAR"),
            ("AAPL", "2023-11-10", "2023-11-16", "2023-11-13", 0.24, "QUARTERLY", "REGULAR"),
            ("MSFT", "2024-02-14", "2024-03-14", "2024-02-15", 0.75, "QUARTERLY", "REGULAR"),
            ("MSFT", "2023-11-15", "2023-12-14", "2023-11-16", 0.75, "QUARTERLY", "REGULAR"),
            ("JNJ", "2024-02-27", "2024-03-05", "2024-02-28", 1.19, "QUARTERLY", "REGULAR"),
            ("KO", "2024-03-14", "2024-04-01", "2024-03-15", 0.485, "QUARTERLY", "REGULAR"),
            ("CVX", "2024-03-15", "2024-03-28", "2024-03-18", 1.63, "QUARTERLY", "REGULAR"),
            ("JPM", "2024-01-05", "2024-01-31", "2024-01-08", 1.05, "QUARTERLY", "REGULAR"),
            ("PFE", "2024-01-25", "2024-03-01", "2024-01-26", 0.42, "QUARTERLY", "REGULAR"),
            ("V", "2024-02-22", "2024-03-01", "2024-02-23", 0.52, "QUARTERLY", "REGULAR"),
            ("XOM", "2024-02-13", "2024-03-11", "2024-02-14", 0.95, "QUARTERLY", "REGULAR"),
            ("MCD", "2024-03-01", "2024-03-15", "2024-03-04", 1.67, "QUARTERLY", "REGULAR"),
            ("DIS", "2020-12-10", "2021-01-21", "2020-12-14", 0.88, "SEMIANNUAL", "REGULAR"),
            ("WMT", "2024-03-08", "2024-04-01", "2024-03-11", 0.2075, "QUARTERLY", "REGULAR"),
        ]
        
        for i, (sym, ex, pay, rec, amt, freq, typ) in enumerate(dividends):
            self.insert("dividend_history", {
                "div_id": i + 1,
                "symbol": sym,
                "ex_date": ex,
                "payment_date": pay,
                "record_date": rec,
                "amount": amt,
                "frequency": freq,
                "type": typ,
            })

    def _populate_earnings_calendar(self) -> None:
        """Pobla calendario de ganancias"""
        earnings = [
            # sym, report_date, report_time, eps_est, eps_act, rev_est, rev_act, surprise, period
            ("AAPL", "2024-02-01", "AMC", 2.10, 2.18, 117.9e9, 119.6e9, 3.81, "Q1 FY2024"),
            ("MSFT", "2024-01-30", "AMC", 2.78, 2.93, 60.8e9, 62.0e9, 5.40, "Q2 FY2024"),
            ("GOOGL", "2024-01-30", "AMC", 1.59, 1.64, 86.0e9, 86.3e9, 3.14, "Q4 2023"),
            ("META", "2024-02-01", "AMC", 4.96, 5.33, 39.2e9, 40.1e9, 7.46, "Q4 2023"),
            ("NVDA", "2024-02-21", "AMC", 4.59, 5.16, 20.4e9, 22.1e9, 12.42, "Q4 FY2024"),
            ("AMZN", "2024-02-01", "AMC", 0.80, 1.00, 166.2e9, 170.0e9, 25.00, "Q4 2023"),
            ("TSLA", "2024-01-24", "AMC", 0.73, 0.71, 25.7e9, 25.2e9, -2.74, "Q4 2023"),
            ("NFLX", "2024-01-23", "AMC", 2.22, 2.11, 8.71e9, 9.83e9, -4.95, "Q4 2023"),
            ("JPM", "2024-01-12", "BMO", 3.61, 3.97, 39.6e9, 41.0e9, 9.97, "Q4 2023"),
            ("BAC", "2024-01-12", "BMO", 0.68, 0.70, 23.5e9, 23.7e9, 2.94, "Q4 2023"),
        ]
        
        for i, (sym, rd, rt, eps_e, eps_a, rev_e, rev_a, surp, period) in enumerate(earnings):
            self.insert("earnings_calendar", {
                "earning_id": i + 1,
                "symbol": sym,
                "report_date": rd,
                "report_time": rt,
                "eps_estimate": eps_e,
                "eps_actual": eps_a,
                "revenue_estimate": rev_e,
                "revenue_actual": rev_a,
                "surprise_pct": surp,
                "period": period,
            })

    def _populate_technical_indicators(self) -> None:
        """Pobla indicadores técnicos calculados"""
        indicators_data = [
            # Para AAPL
            ("AAPL", "SMA_20", 185.40, "BULLISH", 20),
            ("AAPL", "SMA_50", 178.20, "BULLISH", 50),
            ("AAPL", "SMA_200", 168.80, "BULLISH", 200),
            ("AAPL", "EMA_12", 187.30, "BULLISH", 12),
            ("AAPL", "EMA_26", 183.50, "BULLISH", 26),
            ("AAPL", "RSI", 62.5, "NEUTRAL", 14),
            ("AAPL", "MACD", 1.85, "BULLISH", None),
            # Para MSFT
            ("MSFT", "SMA_20", 408.50, "BULLISH", 20),
            ("MSFT", "SMA_50", 395.20, "BULLISH", 50),
            ("MSFT", "RSI", 68.3, "OVERBOUGHT", 14),
            ("MSFT", "MACD", 4.20, "BULLISH", None),
            # Para NVDA
            ("NVDA", "SMA_20", 858.30, "BULLISH", 20),
            ("NVDA", "SMA_50", 780.50, "BULLISH", 50),
            ("NVDA", "RSI", 71.8, "OVERBOUGHT", 14),
            ("NVDA", "MACD", 25.40, "BULLISH", None),
            # Para TSLA
            ("TSLA", "SMA_20", 235.80, "BULLISH", 20),
            ("TSLA", "SMA_50", 225.40, "NEUTRAL", 50),
            ("TSLA", "RSI", 55.2, "NEUTRAL", 14),
            ("TSLA", "MACD", -2.10, "BEARISH", None),
            # Para BTC
            ("BTC-USD", "SMA_20", 65200.00, "BULLISH", 20),
            ("BTC-USD", "SMA_50", 58400.00, "BULLISH", 50),
            ("BTC-USD", "RSI", 65.8, "NEUTRAL", 14),
            ("BTC-USD", "MACD", 850.00, "BULLISH", None),
        ]
        
        for i, (sym, ind, val, signal, period) in enumerate(indicators_data):
            self.insert("technical_indicators", {
                "indicator_id": i + 1,
                "symbol": sym,
                "indicator_name": ind,
                "value": val,
                "signal": signal,
                "period": period,
                "timestamp": datetime.now().isoformat(),
            })

    def _populate_price_history(self) -> None:
        """
        Pobla historial de precios con datos sintéticos realistas.
        Genera 30 días de datos OHLCV para los principales tickers.
        """
        base_prices = {
            "AAPL": 180.0, "MSFT": 395.0, "GOOGL": 165.0,
            "NVDA": 800.0, "TSLA": 220.0, "BTC-USD": 62000.0,
            "SPY": 510.0, "META": 500.0,
        }
        
        hist_id = 1
        for symbol, base_price in base_prices.items():
            price = base_price
            for days_back in range(30, 0, -1):
                # Simular movimiento de precio realista (random walk)
                daily_return = random.gauss(0.0005, 0.015)
                price = price * (1 + daily_return)
                
                # Generar OHLCV realista
                intraday_range = abs(random.gauss(0, 0.008))
                open_p = price * (1 + random.uniform(-0.005, 0.005))
                high_p = max(price, open_p) * (1 + intraday_range)
                low_p = min(price, open_p) * (1 - intraday_range)
                close_p = price
                volume = int(random.gauss(50_000_000, 15_000_000))
                if volume < 0:
                    volume = 10_000_000
                
                timestamp = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                
                self.insert("price_history", {
                    "history_id": hist_id,
                    "symbol": symbol,
                    "open_price": round(open_p, 2),
                    "high_price": round(high_p, 2),
                    "low_price": round(low_p, 2),
                    "close_price": round(close_p, 2),
                    "adj_close": round(close_p, 2),
                    "volume": abs(volume),
                    "interval": "1d",
                    "timestamp": timestamp,
                    "source": "simulated",
                    "is_adjusted": True,
                })
                hist_id += 1


# ==============================================================================
# SECCIÓN 7: GESTOR DE BASE DE DATOS SQLite (REAL)
# ==============================================================================

class DatabaseManager:
    """
    Gestiona la persistencia de datos en SQLite.
    Complementa la base de datos simulada con almacenamiento persistente real.
    """
    
    def __init__(self, db_name: str = DB_NAME):
        """
        Inicializa el gestor de base de datos SQLite.
        
        Args:
            db_name: Nombre del archivo de base de datos
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._setup_connection()
        self._setup_schema()
        
        # Base de datos simulada en memoria
        self.simdb = SimulatedDatabase()
        
        logger.info(f"DatabaseManager inicializado: {db_name}")

    def _setup_connection(self) -> None:
        """Establece conexión con SQLite"""
        try:
            self.conn = sqlite3.connect(
                self.db_name,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            # Optimizaciones de rendimiento
            self.cursor.execute("PRAGMA journal_mode=WAL")
            self.cursor.execute("PRAGMA synchronous=NORMAL")
            self.cursor.execute("PRAGMA cache_size=-64000")  # 64MB
            self.cursor.execute("PRAGMA temp_store=MEMORY")
            
            logger.info(f"Conexión SQLite establecida: {self.db_name}")
        except Exception as e:
            logger.error(f"Error conectando a SQLite: {e}")
            raise

    def _setup_schema(self) -> None:
        """Crea las tablas SQLite necesarias"""
        schema_queries = [
            # Historial de cotizaciones (registro persistente)
            """
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                precio REAL NOT NULL,
                cambio REAL NOT NULL,
                fecha TEXT NOT NULL,
                volumen INTEGER DEFAULT 0,
                alto REAL DEFAULT 0,
                bajo REAL DEFAULT 0,
                moneda TEXT DEFAULT 'USD',
                fuente TEXT DEFAULT 'yfinance'
            )
            """,
            
            # Índice en ticker y fecha
            "CREATE INDEX IF NOT EXISTS idx_historial_ticker ON historial(ticker)",
            "CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial(fecha)",
            
            # Portafolios persistentes
            """
            CREATE TABLE IF NOT EXISTS portafolios_local (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                capital_inicial REAL,
                saldo_efectivo REAL,
                fecha_creacion TEXT,
                fecha_actualizacion TEXT,
                activo INTEGER DEFAULT 1,
                descripcion TEXT
            )
            """,
            
            # Posiciones locales
            """
            CREATE TABLE IF NOT EXISTS posiciones_local (
                id TEXT PRIMARY KEY,
                portafolio_id TEXT,
                simbolo TEXT NOT NULL,
                cantidad REAL DEFAULT 0,
                costo_promedio REAL DEFAULT 0,
                precio_actual REAL DEFAULT 0,
                tipo_activo TEXT DEFAULT 'STOCK',
                fecha_apertura TEXT,
                notas TEXT,
                FOREIGN KEY(portafolio_id) REFERENCES portafolios_local(id)
            )
            """,
            
            # Alertas de precio locales
            """
            CREATE TABLE IF NOT EXISTS alertas_precio (
                id TEXT PRIMARY KEY,
                simbolo TEXT NOT NULL,
                tipo_alerta TEXT NOT NULL,
                umbral REAL NOT NULL,
                mensaje TEXT,
                activa INTEGER DEFAULT 1,
                disparada INTEGER DEFAULT 0,
                fecha_creacion TEXT,
                fecha_disparo TEXT,
                repetir INTEGER DEFAULT 0
            )
            """,
            
            # Configuración del usuario
            """
            CREATE TABLE IF NOT EXISTS config_usuario (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                tipo TEXT DEFAULT 'string',
                fecha_actualizacion TEXT
            )
            """,
            
            # Tickers vigilados
            """
            CREATE TABLE IF NOT EXISTS tickers_watch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simbolo TEXT UNIQUE NOT NULL,
                nombre TEXT,
                tipo_activo TEXT DEFAULT 'STOCK',
                activo INTEGER DEFAULT 1,
                fecha_agregado TEXT,
                notas TEXT
            )
            """,
            
            # Log del sistema
            """
            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nivel TEXT NOT NULL,
                modulo TEXT,
                mensaje TEXT NOT NULL,
                fecha TEXT NOT NULL
            )
            """,
            
            # Cache de datos de mercado
            """
            CREATE TABLE IF NOT EXISTS market_cache (
                simbolo TEXT PRIMARY KEY,
                datos_json TEXT NOT NULL,
                ultima_actualizacion TEXT NOT NULL,
                expira_en TEXT
            )
            """,
        ]
        
        try:
            for query in schema_queries:
                self.cursor.execute(query)
            self.conn.commit()
            logger.info("Esquema SQLite creado/verificado correctamente")
        except Exception as e:
            logger.error(f"Error creando esquema SQLite: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # OPERACIONES SQLITE
    # ─────────────────────────────────────────────────────────────────────────

    def guardar_registro(self, ticker: str, precio: float, cambio: float,
                        volumen: int = 0, alto: float = 0, bajo: float = 0,
                        moneda: str = "USD") -> bool:
        """
        Guarda un registro de cotización en el historial SQLite.
        
        Args:
            ticker: Símbolo del activo
            precio: Precio actual
            cambio: Cambio porcentual
            volumen: Volumen negociado
            alto: Precio máximo del día
            bajo: Precio mínimo del día
            moneda: Moneda del precio
        
        Returns:
            True si se guardó correctamente
        """
        try:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """
                INSERT INTO historial (ticker, precio, cambio, fecha, volumen, alto, bajo, moneda)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ticker, precio, cambio, fecha, volumen, alto, bajo, moneda)
            )
            self.conn.commit()
            
            # También guardar en base de datos simulada
            self.simdb.insert("data_snapshots", {
                "symbol": ticker,
                "price": precio,
                "change_pct": cambio,
                "volume": volumen,
                "timestamp": fecha,
                "market_status": "OPEN",
            })
            
            return True
        except Exception as e:
            logger.error(f"Error guardando registro {ticker}: {e}")
            return False

    def obtener_historial(self, ticker: str, dias: int = 7, limit: int = 100) -> List[Dict]:
        """
        Obtiene el historial de cotizaciones de un ticker.
        
        Args:
            ticker: Símbolo del activo
            dias: Número de días hacia atrás
            limit: Máximo de registros
        
        Returns:
            Lista de registros del historial
        """
        try:
            fecha_desde = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            self.cursor.execute(
                """
                SELECT ticker, precio, cambio, fecha, volumen, alto, bajo, moneda
                FROM historial
                WHERE ticker = ? AND fecha >= ?
                ORDER BY fecha DESC
                LIMIT ?
                """,
                (ticker, fecha_desde, limit)
            )
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error obteniendo historial {ticker}: {e}")
            return []

    def obtener_todos_los_tickers(self) -> List[str]:
        """Retorna lista de todos los tickers en el historial"""
        try:
            self.cursor.execute("SELECT DISTINCT ticker FROM historial ORDER BY ticker")
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo tickers: {e}")
            return []

    def guardar_config(self, clave: str, valor: Any, tipo: str = "string") -> bool:
        """
        Guarda una configuración en la base de datos.
        
        Args:
            clave: Clave de configuración
            valor: Valor (se serializa a string/JSON)
            tipo: Tipo de dato
        
        Returns:
            True si se guardó correctamente
        """
        try:
            if tipo in ("dict", "list"):
                valor_str = json.dumps(valor)
            else:
                valor_str = str(valor)
            
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO config_usuario (clave, valor, tipo, fecha_actualizacion)
                VALUES (?, ?, ?, ?)
                """,
                (clave, valor_str, tipo, datetime.now().isoformat())
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error guardando config {clave}: {e}")
            return False

    def obtener_config(self, clave: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            clave: Clave de configuración
            default: Valor por defecto si no existe
        
        Returns:
            Valor de configuración
        """
        try:
            self.cursor.execute(
                "SELECT valor, tipo FROM config_usuario WHERE clave = ?",
                (clave,)
            )
            row = self.cursor.fetchone()
            if row:
                valor, tipo = row
                if tipo == "int":
                    return int(valor)
                elif tipo == "float":
                    return float(valor)
                elif tipo == "bool":
                    return valor.lower() == "true"
                elif tipo in ("dict", "list"):
                    return json.loads(valor)
                return valor
            return default
        except Exception as e:
            logger.error(f"Error obteniendo config {clave}: {e}")
            return default

    def guardar_cache_mercado(self, simbolo: str, datos: Dict, ttl_segundos: int = 60) -> bool:
        """
        Guarda datos de mercado en cache.
        
        Args:
            simbolo: Símbolo del activo
            datos: Datos a cachear
            ttl_segundos: Tiempo de vida del cache
        
        Returns:
            True si se guardó correctamente
        """
        try:
            ahora = datetime.now()
            expira = ahora + timedelta(seconds=ttl_segundos)
            
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO market_cache (simbolo, datos_json, ultima_actualizacion, expira_en)
                VALUES (?, ?, ?, ?)
                """,
                (simbolo, json.dumps(datos, default=str), ahora.isoformat(), expira.isoformat())
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error guardando cache {simbolo}: {e}")
            return False

    def obtener_cache_mercado(self, simbolo: str) -> Optional[Dict]:
        """
        Obtiene datos de mercado del cache si están vigentes.
        
        Args:
            simbolo: Símbolo del activo
        
        Returns:
            Datos del cache o None si expiró
        """
        try:
            self.cursor.execute(
                """
                SELECT datos_json, expira_en FROM market_cache
                WHERE simbolo = ? AND expira_en > ?
                """,
                (simbolo, datetime.now().isoformat())
            )
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Error obteniendo cache {simbolo}: {e}")
            return None

    def limpiar_historial_antiguo(self, dias: int = DB_MAX_HISTORY_DAYS) -> int:
        """
        Elimina registros de historial más antiguos que `dias` días.
        
        Args:
            dias: Días de retención del historial
        
        Returns:
            Número de registros eliminados
        """
        try:
            fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            self.cursor.execute(
                "DELETE FROM historial WHERE fecha < ?",
                (fecha_limite,)
            )
            count = self.cursor.rowcount
            self.conn.commit()
            if count > 0:
                logger.info(f"Limpieza historial: {count} registros eliminados")
            return count
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
            return 0

    def get_db_stats(self) -> Dict:
        """Retorna estadísticas de la base de datos SQLite"""
        try:
            stats = {}
            
            tables = ["historial", "portafolios_local", "posiciones_local",
                      "alertas_precio", "config_usuario", "tickers_watch", 
                      "system_log", "market_cache"]
            
            for table in tables:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = self.cursor.fetchone()[0]
                except Exception:
                    stats[table] = 0
            
            # Tamaño del archivo de base de datos
            if os.path.exists(self.db_name):
                stats["file_size_bytes"] = os.path.getsize(self.db_name)
                stats["file_size_kb"] = stats["file_size_bytes"] / 1024
            
            # Estadísticas de la DB simulada
            stats["simdb"] = self.simdb.get_database_stats()
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo stats DB: {e}")
            return {}

    def exportar_csv(self, file_path: str, ticker: str = None) -> bool:
        """
        Exporta el historial a CSV.
        
        Args:
            file_path: Ruta del archivo CSV de salida
            ticker: Ticker específico o None para todos
        
        Returns:
            True si se exportó correctamente
        """
        try:
            if ticker:
                self.cursor.execute(
                    "SELECT ticker, precio, cambio, fecha, volumen, alto, bajo FROM historial WHERE ticker = ? ORDER BY fecha",
                    (ticker,)
                )
            else:
                self.cursor.execute(
                    "SELECT ticker, precio, cambio, fecha, volumen, alto, bajo FROM historial ORDER BY fecha"
                )
            
            rows = self.cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Ticker", "Precio", "Cambio%", "Fecha", "Volumen", "Alto", "Bajo"])
                for row in rows:
                    writer.writerow(list(row))
            
            logger.info(f"Exportado CSV: {file_path} ({len(rows)} registros)")
            return True
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")
            return False

    def close(self) -> None:
        """Cierra la conexión a la base de datos"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Conexión SQLite cerrada")
            except Exception as e:
                logger.error(f"Error cerrando conexión: {e}")

    def __del__(self):
        """Destructor: asegura cierre de conexión"""
        self.close()


# ==============================================================================
# SECCIÓN 8: MOTOR DE DATOS FINANCIEROS
# ==============================================================================

class MarketEngine:
    """
    Motor de obtención de datos financieros en tiempo real.
    Utiliza yfinance como fuente principal con fallback a datos simulados.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Inicializa el motor de mercado.
        
        Args:
            db_manager: Gestor de base de datos para cache
        """
        self.db = db_manager
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_duration = 30  # segundos
        self._fetch_errors: Dict[str, int] = defaultdict(int)
        self._max_errors = 5
        logger.info("MarketEngine inicializado")

    def fetch_data(self, ticker: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Obtiene datos de mercado para un ticker.
        
        Estrategia:
        1. Verifica cache en memoria
        2. Verifica cache en SQLite
        3. Consulta yfinance
        4. Fallback a datos simulados
        
        Args:
            ticker: Símbolo del activo
            use_cache: Si usar el cache
        
        Returns:
            Diccionario con datos del ticker o None si falla
        """
        # 1. Cache en memoria
        if use_cache and self._is_cached(ticker):
            return self._cache[ticker]
        
        # 2. Cache en SQLite
        if use_cache and self.db:
            cached = self.db.obtener_cache_mercado(ticker)
            if cached:
                self._cache[ticker] = cached
                self._cache_timestamps[ticker] = time.time()
                return cached
        
        # 3. Intentar yfinance
        data = self._fetch_from_yfinance(ticker)
        
        # 4. Fallback a datos simulados
        if data is None:
            data = self._fetch_from_simdb(ticker)
        
        if data:
            # Actualizar caches
            self._cache[ticker] = data
            self._cache_timestamps[ticker] = time.time()
            if self.db:
                self.db.guardar_cache_mercado(ticker, data)
        
        return data

    def _fetch_from_yfinance(self, ticker: str) -> Optional[Dict]:
        """
        Obtiene datos reales de yfinance.
        
        Args:
            ticker: Símbolo del activo
        
        Returns:
            Diccionario con datos o None si falla
        """
        # Verificar si hay demasiados errores consecutivos
        if self._fetch_errors[ticker] >= self._max_errors:
            logger.warning(f"Demasiados errores para {ticker}, usando fallback")
            return None
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="1m")
            
            if hist.empty:
                self._fetch_errors[ticker] += 1
                logger.warning(f"Sin datos para {ticker}")
                return None
            
            info = {}
            try:
                info = stock.info
            except Exception:
                pass
            
            current_price = float(hist['Close'].iloc[-1])
            open_price = float(hist['Open'].iloc[0])
            
            if open_price == 0:
                open_price = current_price
            
            pct_change = ((current_price - open_price) / open_price) * 100
            
            data = {
                "symbol": ticker,
                "price": round(current_price, 2),
                "open_price": round(open_price, 2),
                "change": round(current_price - open_price, 2),
                "change_pct": round(pct_change, 2),
                "high": round(float(hist['High'].max()), 2),
                "low": round(float(hist['Low'].min()), 2),
                "volume": int(info.get('volume', hist['Volume'].sum())),
                "avg_volume": int(info.get('averageVolume', 0)),
                "market_cap": float(info.get('marketCap', 0)),
                "pe_ratio": float(info.get('trailingPE', 0) or 0),
                "eps": float(info.get('trailingEps', 0) or 0),
                "dividend_yield": float(info.get('dividendYield', 0) or 0) * 100,
                "beta": float(info.get('beta', 0) or 0),
                "week_52_high": float(info.get('fiftyTwoWeekHigh', 0) or 0),
                "week_52_low": float(info.get('fiftyTwoWeekLow', 0) or 0),
                "currency": info.get('currency', 'USD'),
                "company_name": info.get('longName', ticker),
                "sector": info.get('sector', ''),
                "exchange": info.get('exchange', ''),
                "timestamp": datetime.now().isoformat(),
                "source": "yfinance",
            }
            
            # Reset errores en éxito
            self._fetch_errors[ticker] = 0
            return data
            
        except Exception as e:
            self._fetch_errors[ticker] += 1
            logger.error(f"Error yfinance para {ticker}: {e}")
            return None

    def _fetch_from_simdb(self, ticker: str) -> Optional[Dict]:
        """
        Obtiene datos de la base de datos simulada como fallback.
        
        Args:
            ticker: Símbolo del activo
        
        Returns:
            Diccionario con datos simulados
        """
        if not self.db:
            return self._generate_random_data(ticker)
        
        try:
            # Buscar en market_data simulada
            records = self.db.simdb.select("market_data", {"symbol": ticker})
            if records:
                rec = records[0]
                # Añadir variación aleatoria pequeña
                noise = random.uniform(-0.005, 0.005)
                price = rec.get("price", 100.0) * (1 + noise)
                
                return {
                    "symbol": ticker,
                    "price": round(price, 2),
                    "open_price": rec.get("open_price", price),
                    "change": round(price - rec.get("prev_close", price), 2),
                    "change_pct": rec.get("change_pct", 0) + noise * 100,
                    "high": rec.get("high", price * 1.01),
                    "low": rec.get("low", price * 0.99),
                    "volume": rec.get("volume", 1000000),
                    "avg_volume": rec.get("avg_volume", 1000000),
                    "market_cap": rec.get("market_cap", 0),
                    "pe_ratio": rec.get("pe_ratio", 0),
                    "eps": rec.get("eps", 0),
                    "dividend_yield": rec.get("dividend_yield", 0),
                    "beta": rec.get("beta", 1.0),
                    "week_52_high": rec.get("week_52_high", price * 1.2),
                    "week_52_low": rec.get("week_52_low", price * 0.8),
                    "currency": rec.get("currency", "USD"),
                    "company_name": ticker,
                    "sector": "",
                    "exchange": "",
                    "timestamp": datetime.now().isoformat(),
                    "source": "simulated",
                }
            
            return self._generate_random_data(ticker)
            
        except Exception as e:
            logger.error(f"Error obteniendo datos simulados para {ticker}: {e}")
            return self._generate_random_data(ticker)

    def _generate_random_data(self, ticker: str) -> Dict:
        """
        Genera datos aleatorios para un ticker desconocido.
        
        Args:
            ticker: Símbolo del activo
        
        Returns:
            Diccionario con datos generados aleatoriamente
        """
        # Precio base dependiendo del tipo de activo
        if "USD" in ticker or "BTC" in ticker or "ETH" in ticker:
            base_price = random.uniform(100, 70000)
        else:
            base_price = random.uniform(10, 500)
        
        change_pct = random.uniform(-5, 5)
        prev_close = base_price / (1 + change_pct / 100)
        
        return {
            "symbol": ticker,
            "price": round(base_price, 2),
            "open_price": round(prev_close * 1.002, 2),
            "change": round(base_price - prev_close, 2),
            "change_pct": round(change_pct, 2),
            "high": round(base_price * 1.015, 2),
            "low": round(base_price * 0.985, 2),
            "volume": random.randint(1_000_000, 100_000_000),
            "avg_volume": random.randint(1_000_000, 50_000_000),
            "market_cap": round(base_price * random.randint(1_000_000, 10_000_000_000), 0),
            "pe_ratio": round(random.uniform(10, 50), 1),
            "eps": round(random.uniform(0.5, 20), 2),
            "dividend_yield": round(random.uniform(0, 4), 2),
            "beta": round(random.uniform(0.5, 2.0), 2),
            "week_52_high": round(base_price * 1.3, 2),
            "week_52_low": round(base_price * 0.7, 2),
            "currency": "USD",
            "company_name": ticker,
            "sector": random.choice(MARKET_SECTORS),
            "exchange": random.choice(["NYSE", "NASDAQ", "AMEX"]),
            "timestamp": datetime.now().isoformat(),
            "source": "generated",
        }

    def _is_cached(self, ticker: str) -> bool:
        """
        Verifica si un ticker tiene datos en cache válidos.
        
        Args:
            ticker: Símbolo del activo
        
        Returns:
            True si el cache es válido
        """
        if ticker not in self._cache:
            return False
        if ticker not in self._cache_timestamps:
            return False
        age = time.time() - self._cache_timestamps[ticker]
        return age < self._cache_duration

    def fetch_multiple(self, tickers: List[str], parallel: bool = True) -> Dict[str, Dict]:
        """
        Obtiene datos para múltiples tickers.
        
        Args:
            tickers: Lista de símbolos
            parallel: Si descargar en paralelo (no implementado en esta versión básica)
        
        Returns:
            Diccionario {ticker: data}
        """
        results = {}
        for ticker in tickers:
            data = self.fetch_data(ticker)
            if data:
                results[ticker] = data
        return results

    def fetch_historical(self, ticker: str, period: str = "1mo",
                         interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos de un ticker.
        
        Args:
            ticker: Símbolo del activo
            period: Periodo de datos ("1d", "5d", "1mo", "3mo", "1y", etc.)
            interval: Intervalo de datos ("1m", "5m", "1h", "1d", etc.)
        
        Returns:
            DataFrame con datos históricos o None
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if not hist.empty:
                hist.index = hist.index.tz_localize(None)
                logger.info(f"Historial obtenido para {ticker}: {len(hist)} registros")
                return hist
            
            # Fallback a datos simulados
            return self._generate_simulated_historical(ticker, period)
            
        except Exception as e:
            logger.warning(f"Error obteniendo historial yfinance para {ticker}: {e}")
            return self._generate_simulated_historical(ticker, period)

    def _generate_simulated_historical(self, ticker: str, period: str) -> pd.DataFrame:
        """
        Genera datos históricos simulados como fallback.
        
        Args:
            ticker: Símbolo del activo
            period: Periodo de datos
        
        Returns:
            DataFrame con datos simulados
        """
        period_days = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
        }
        days = period_days.get(period, 30)
        
        # Precio base del ticker
        if self.db:
            records = self.db.simdb.select("price_history", {"symbol": ticker}, 
                                           order_by="-timestamp", limit=1)
            if records:
                base_price = records[0].get("close_price", 100.0)
            else:
                base_price = 100.0
        else:
            base_price = 100.0
        
        # Generar datos
        dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
        prices = []
        price = base_price * random.uniform(0.7, 0.9)
        
        for _ in dates:
            price *= (1 + random.gauss(0.0005, 0.015))
            prices.append(max(price, 0.01))
        
        data = {
            'Open': [p * random.uniform(0.995, 1.005) for p in prices],
            'High': [p * random.uniform(1.005, 1.020) for p in prices],
            'Low': [p * random.uniform(0.980, 0.995) for p in prices],
            'Close': prices,
            'Volume': [random.randint(1_000_000, 100_000_000) for _ in prices],
        }
        
        df = pd.DataFrame(data, index=dates)
        return df

    def get_market_summary(self) -> Dict:
        """
        Retorna un resumen del estado general del mercado.
        
        Returns:
            Diccionario con métricas del mercado
        """
        if not self.db:
            return {}
        
        try:
            all_data = self.db.simdb.select("market_data")
            
            if not all_data:
                return {}
            
            prices = [d.get("price", 0) for d in all_data]
            changes = [d.get("change_pct", 0) for d in all_data]
            volumes = [d.get("volume", 0) for d in all_data]
            
            advancing = sum(1 for c in changes if c > 0)
            declining = sum(1 for c in changes if c < 0)
            unchanged = sum(1 for c in changes if c == 0)
            
            return {
                "total_symbols": len(all_data),
                "advancing": advancing,
                "declining": declining,
                "unchanged": unchanged,
                "advance_decline_ratio": advancing / max(declining, 1),
                "avg_change_pct": statistics.mean(changes) if changes else 0,
                "total_volume": sum(volumes),
                "market_sentiment": "BULLISH" if advancing > declining else "BEARISH" if declining > advancing else "NEUTRAL",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculando market summary: {e}")
            return {}


# ==============================================================================
# SECCIÓN 9: CALCULADORA DE INDICADORES TÉCNICOS
# ==============================================================================

class TechnicalAnalysis:
    """
    Clase para calcular indicadores técnicos sobre series de precios.
    Implementa los indicadores más utilizados en análisis técnico.
    """

    @staticmethod
    def sma(prices: List[float], period: int) -> List[Optional[float]]:
        """
        Calcula la Media Móvil Simple (SMA).
        
        Args:
            prices: Lista de precios de cierre
            period: Período de la media
        
        Returns:
            Lista con valores SMA (None para períodos sin datos suficientes)
        """
        result = [None] * len(prices)
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            result[i] = sum(window) / period
        return result

    @staticmethod
    def ema(prices: List[float], period: int) -> List[Optional[float]]:
        """
        Calcula la Media Móvil Exponencial (EMA).
        
        Args:
            prices: Lista de precios de cierre
            period: Período de la EMA
        
        Returns:
            Lista con valores EMA
        """
        if len(prices) < period:
            return [None] * len(prices)
        
        result = [None] * len(prices)
        multiplier = 2 / (period + 1)
        
        # Inicializar con SMA
        result[period - 1] = sum(prices[:period]) / period
        
        for i in range(period, len(prices)):
            result[i] = (prices[i] * multiplier) + (result[i - 1] * (1 - multiplier))
        
        return result

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
        """
        Calcula el Índice de Fuerza Relativa (RSI).
        
        Args:
            prices: Lista de precios de cierre
            period: Período del RSI (default 14)
        
        Returns:
            Lista con valores RSI (0-100)
        """
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        result = [None] * len(prices)
        
        # Calcular cambios
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [max(d, 0) for d in deltas]
        losses = [abs(min(d, 0)) for d in deltas]
        
        # Primera media
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(prices)):
            if avg_loss == 0:
                result[i] = 100
            else:
                rs = avg_gain / avg_loss
                result[i] = round(100 - (100 / (1 + rs)), 2)
            
            # Actualizar medias
            gain = gains[i - 1] if i - 1 < len(gains) else 0
            loss = losses[i - 1] if i - 1 < len(losses) else 0
            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period
        
        return result

    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Tuple[List, List, List]:
        """
        Calcula el MACD (Moving Average Convergence/Divergence).
        
        Args:
            prices: Lista de precios de cierre
            fast: Período EMA rápida (default 12)
            slow: Período EMA lenta (default 26)
            signal: Período línea de señal (default 9)
        
        Returns:
            Tupla (macd_line, signal_line, histogram)
        """
        ema_fast = TechnicalAnalysis.ema(prices, fast)
        ema_slow = TechnicalAnalysis.ema(prices, slow)
        
        macd_line = []
        for i in range(len(prices)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line.append(round(ema_fast[i] - ema_slow[i], 4))
            else:
                macd_line.append(None)
        
        # Signal line (EMA del MACD)
        valid_macd = [v for v in macd_line if v is not None]
        signal_ema = TechnicalAnalysis.ema(valid_macd, signal)
        
        signal_line = [None] * len(prices)
        j = 0
        for i in range(len(prices)):
            if macd_line[i] is not None:
                signal_line[i] = signal_ema[j]
                j += 1
        
        # Histograma
        histogram = []
        for i in range(len(prices)):
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram.append(round(macd_line[i] - signal_line[i], 4))
            else:
                histogram.append(None)
        
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, 
                        std_dev: float = 2.0) -> Tuple[List, List, List]:
        """
        Calcula las Bandas de Bollinger.
        
        Args:
            prices: Lista de precios de cierre
            period: Período de la media móvil (default 20)
            std_dev: Multiplicador de desviación estándar (default 2)
        
        Returns:
            Tupla (upper_band, middle_band, lower_band)
        """
        middle = TechnicalAnalysis.sma(prices, period)
        upper = [None] * len(prices)
        lower = [None] * len(prices)
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            std = statistics.stdev(window)
            if middle[i] is not None:
                upper[i] = round(middle[i] + (std_dev * std), 2)
                lower[i] = round(middle[i] - (std_dev * std), 2)
        
        return upper, middle, lower

    @staticmethod
    def stochastic(highs: List[float], lows: List[float], closes: List[float],
                   k_period: int = 14, d_period: int = 3) -> Tuple[List, List]:
        """
        Calcula el Oscilador Estocástico.
        
        Args:
            highs: Lista de precios máximos
            lows: Lista de precios mínimos
            closes: Lista de precios de cierre
            k_period: Período para %K (default 14)
            d_period: Período para %D (default 3)
        
        Returns:
            Tupla (%K, %D)
        """
        n = len(closes)
        k_values = [None] * n
        
        for i in range(k_period - 1, n):
            high_max = max(highs[i - k_period + 1:i + 1])
            low_min = min(lows[i - k_period + 1:i + 1])
            
            if high_max == low_min:
                k_values[i] = 50.0
            else:
                k_values[i] = round(((closes[i] - low_min) / (high_max - low_min)) * 100, 2)
        
        # %D es SMA de %K
        valid_k = [v for v in k_values if v is not None]
        d_sma = TechnicalAnalysis.sma(valid_k, d_period)
        
        d_values = [None] * n
        j = 0
        for i in range(n):
            if k_values[i] is not None:
                d_values[i] = d_sma[j]
                j += 1
        
        return k_values, d_values

    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float],
            period: int = 14) -> List[Optional[float]]:
        """
        Calcula el Average True Range (ATR).
        
        Args:
            highs: Lista de precios máximos
            lows: Lista de precios mínimos
            closes: Lista de precios de cierre
            period: Período del ATR (default 14)
        
        Returns:
            Lista con valores ATR
        """
        n = len(closes)
        if n < 2:
            return [None] * n
        
        true_ranges = [None]
        for i in range(1, n):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i - 1])
            lc = abs(lows[i] - closes[i - 1])
            true_ranges.append(max(hl, hc, lc))
        
        return TechnicalAnalysis.sma([tr for tr in true_ranges if tr is not None], period)

    @staticmethod
    def obv(closes: List[float], volumes: List[float]) -> List[float]:
        """
        Calcula el On-Balance Volume (OBV).
        
        Args:
            closes: Lista de precios de cierre
            volumes: Lista de volúmenes
        
        Returns:
            Lista con valores OBV
        """
        obv_values = [0.0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i - 1]:
                obv_values.append(obv_values[-1] + volumes[i])
            elif closes[i] < closes[i - 1]:
                obv_values.append(obv_values[-1] - volumes[i])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values

    @staticmethod
    def get_signal(indicator: str, value: float, extra: Dict = None) -> str:
        """
        Determina la señal de trading basada en un indicador.
        
        Args:
            indicator: Nombre del indicador
            value: Valor actual del indicador
            extra: Parámetros adicionales (ej: precio actual para SMA)
        
        Returns:
            String con la señal: "BUY", "SELL", "HOLD", "OVERBOUGHT", "OVERSOLD"
        """
        if value is None:
            return "NEUTRAL"
        
        if indicator == "RSI":
            if value >= 70:
                return "OVERBOUGHT"
            elif value <= 30:
                return "OVERSOLD"
            elif value >= 60:
                return "BULLISH"
            elif value <= 40:
                return "BEARISH"
            return "NEUTRAL"
        
        elif indicator.startswith("SMA") or indicator.startswith("EMA"):
            if extra and "price" in extra:
                price = extra["price"]
                if price > value * 1.02:
                    return "BULLISH"
                elif price < value * 0.98:
                    return "BEARISH"
                return "NEUTRAL"
        
        elif indicator == "MACD":
            if value > 0:
                return "BULLISH"
            elif value < 0:
                return "BEARISH"
            return "NEUTRAL"
        
        elif indicator == "STOCHASTIC":
            if value >= 80:
                return "OVERBOUGHT"
            elif value <= 20:
                return "OVERSOLD"
            return "NEUTRAL"
        
        return "NEUTRAL"


# ==============================================================================
# SECCIÓN 10: MOTOR DE ALERTAS
# ==============================================================================

class AlertEngine:
    """
    Motor de gestión y evaluación de alertas de precio.
    Verifica continuamente las condiciones de las alertas activas.
    """

    def __init__(self, db: DatabaseManager):
        """
        Inicializa el motor de alertas.
        
        Args:
            db: Gestor de base de datos
        """
        self.db = db
        self._callbacks: List[callable] = []
        self._triggered_alerts: List[Dict] = []
        logger.info("AlertEngine inicializado")

    def register_callback(self, callback: callable) -> None:
        """
        Registra un callback que se llama cuando una alerta se dispara.
        
        Args:
            callback: Función a llamar con (alert_data, price)
        """
        self._callbacks.append(callback)

    def check_alerts(self, market_data: Dict[str, Dict]) -> List[Dict]:
        """
        Verifica todas las alertas activas contra los datos de mercado actuales.
        
        Args:
            market_data: Diccionario {symbol: data} con datos actuales
        
        Returns:
            Lista de alertas disparadas
        """
        triggered = []
        
        try:
            # Obtener alertas activas de la DB simulada
            active_alerts = self.db.simdb.select(
                "price_alerts",
                {"is_active": True, "is_triggered": False}
            )
            
            for alert in active_alerts:
                symbol = alert.get("symbol")
                if symbol not in market_data:
                    continue
                
                data = market_data[symbol]
                current_price = data.get("price", 0)
                current_pct = data.get("change_pct", 0)
                
                alert_type = alert.get("alert_type")
                threshold = alert.get("threshold", 0)
                
                should_trigger = False
                
                if alert_type == "PRICE_ABOVE" and current_price >= threshold:
                    should_trigger = True
                elif alert_type == "PRICE_BELOW" and current_price <= threshold:
                    should_trigger = True
                elif alert_type == "PERCENT_CHANGE" and abs(current_pct) >= threshold:
                    should_trigger = True
                
                if should_trigger:
                    # Marcar como disparada en la DB
                    pk = alert.get("alert_id")
                    if pk:
                        self.db.simdb.update("price_alerts", str(pk), {
                            "is_triggered": True,
                            "triggered_at": datetime.now().isoformat(),
                            "is_active": alert.get("repeat", False),
                        })
                    
                    alert_info = {
                        **alert,
                        "current_price": current_price,
                        "triggered_at": datetime.now().isoformat(),
                    }
                    
                    triggered.append(alert_info)
                    self._triggered_alerts.append(alert_info)
                    
                    # Ejecutar callbacks
                    for callback in self._callbacks:
                        try:
                            callback(alert_info, current_price)
                        except Exception as e:
                            logger.error(f"Error en callback de alerta: {e}")
            
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
        
        return triggered

    def add_alert(self, symbol: str, alert_type: str, threshold: float,
                  message: str = "", priority: str = "MEDIUM",
                  repeat: bool = False) -> str:
        """
        Añade una nueva alerta de precio.
        
        Args:
            symbol: Símbolo del activo
            alert_type: Tipo de alerta (PRICE_ABOVE, PRICE_BELOW, PERCENT_CHANGE)
            threshold: Umbral de la alerta
            message: Mensaje personalizado
            priority: Prioridad (LOW, MEDIUM, HIGH, CRITICAL)
            repeat: Si repetir cuando se dispare
        
        Returns:
            ID de la alerta creada
        """
        alert = {
            "symbol": symbol,
            "alert_type": alert_type,
            "threshold": threshold,
            "message": message or f"Alerta {alert_type} para {symbol} @ {threshold}",
            "is_active": True,
            "is_triggered": False,
            "created_at": datetime.now().isoformat(),
            "repeat": repeat,
            "priority": priority,
        }
        
        alert_id = self.db.simdb.insert("price_alerts", alert)
        
        # También guardar en SQLite
        try:
            self.db.cursor.execute(
                """
                INSERT INTO alertas_precio (id, simbolo, tipo_alerta, umbral, mensaje, activa, repetir, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (str(alert_id), symbol, alert_type, threshold, 
                 alert["message"], int(repeat), datetime.now().isoformat())
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error guardando alerta en SQLite: {e}")
        
        logger.info(f"Alerta creada: {symbol} {alert_type} @ {threshold}")
        return str(alert_id)

    def get_active_alerts(self) -> List[Dict]:
        """Retorna todas las alertas activas"""
        return self.db.simdb.select("price_alerts", {"is_active": True})

    def get_triggered_history(self) -> List[Dict]:
        """Retorna el historial de alertas disparadas"""
        return self._triggered_alerts.copy()

    def disable_alert(self, alert_id: str) -> bool:
        """
        Desactiva una alerta.
        
        Args:
            alert_id: ID de la alerta a desactivar
        
        Returns:
            True si se desactivó correctamente
        """
        return self.db.simdb.update("price_alerts", alert_id, {"is_active": False})

    def delete_alert(self, alert_id: str) -> bool:
        """
        Elimina una alerta.
        
        Args:
            alert_id: ID de la alerta a eliminar
        
        Returns:
            True si se eliminó correctamente
        """
        return self.db.simdb.delete("price_alerts", alert_id)


# ==============================================================================
# SECCIÓN 11: GESTOR DE PORTAFOLIO
# ==============================================================================

class PortfolioManager:
    """
    Gestiona operaciones de portafolio: compra/venta, cálculo de PnL,
    análisis de rendimiento y gestión de posiciones.
    """

    def __init__(self, db: DatabaseManager):
        """
        Inicializa el gestor de portafolio.
        
        Args:
            db: Gestor de base de datos
        """
        self.db = db
        self._active_portfolio_id: Optional[str] = "port-001"
        logger.info("PortfolioManager inicializado")

    @property
    def active_portfolio(self) -> Optional[Dict]:
        """Retorna el portafolio activo actual"""
        if not self._active_portfolio_id:
            return None
        return self.db.simdb.select_one("portfolios", 
                                        {"portfolio_id": self._active_portfolio_id})

    def set_active_portfolio(self, portfolio_id: str) -> bool:
        """
        Establece el portafolio activo.
        
        Args:
            portfolio_id: ID del portafolio a activar
        
        Returns:
            True si el portafolio existe y se activó
        """
        portfolio = self.db.simdb.select_one("portfolios", {"portfolio_id": portfolio_id})
        if portfolio:
            self._active_portfolio_id = portfolio_id
            return True
        return False

    def get_all_portfolios(self) -> List[Dict]:
        """Retorna todos los portafolios"""
        return self.db.simdb.select("portfolios", {"is_active": True})

    def create_portfolio(self, name: str, initial_capital: float = 100000.0,
                         currency: str = "USD", description: str = "") -> str:
        """
        Crea un nuevo portafolio.
        
        Args:
            name: Nombre del portafolio
            initial_capital: Capital inicial
            currency: Moneda del portafolio
            description: Descripción del portafolio
        
        Returns:
            ID del portafolio creado
        """
        portfolio_id = f"port-{uuid.uuid4().hex[:8]}"
        
        self.db.simdb.insert("portfolios", {
            "portfolio_id": portfolio_id,
            "name": name,
            "description": description,
            "currency": currency,
            "initial_capital": initial_capital,
            "cash_balance": initial_capital,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })
        
        # También en SQLite
        try:
            self.db.cursor.execute(
                """
                INSERT INTO portafolios_local (id, nombre, capital_inicial, saldo_efectivo, 
                fecha_creacion, fecha_actualizacion, activo, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (portfolio_id, name, initial_capital, initial_capital,
                 datetime.now().isoformat(), datetime.now().isoformat(), description)
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Error guardando portafolio en SQLite: {e}")
        
        logger.info(f"Portafolio creado: {name} ({portfolio_id})")
        return portfolio_id

    def buy(self, symbol: str, quantity: float, price: float = None,
            order_type: str = "MARKET", notes: str = "",
            portfolio_id: str = None) -> Optional[str]:
        """
        Ejecuta una compra de activos.
        
        Args:
            symbol: Símbolo del activo
            quantity: Cantidad a comprar
            price: Precio de compra (None = precio de mercado)
            order_type: Tipo de orden
            notes: Notas de la transacción
            portfolio_id: ID del portafolio (None = activo)
        
        Returns:
            ID de la transacción o None si falló
        """
        port_id = portfolio_id or self._active_portfolio_id
        if not port_id:
            logger.error("No hay portafolio activo")
            return None
        
        portfolio = self.db.simdb.select_one("portfolios", {"portfolio_id": port_id})
        if not portfolio:
            logger.error(f"Portafolio no encontrado: {port_id}")
            return None
        
        # Obtener precio actual si no se especificó
        if price is None:
            market_data = self.db.simdb.select_one("market_data", {"symbol": symbol})
            if market_data:
                price = market_data.get("price", 0)
            else:
                logger.error(f"No hay datos de precio para {symbol}")
                return None
        
        total_value = round(quantity * price, 2)
        commission = round(total_value * 0.001, 2)  # 0.1% de comisión
        total_cost = total_value + commission
        
        # Verificar fondos suficientes
        if portfolio.get("cash_balance", 0) < total_cost:
            logger.warning(f"Fondos insuficientes: necesita ${total_cost:.2f}, tiene ${portfolio.get('cash_balance', 0):.2f}")
            return None
        
        txn_id = f"txn-{uuid.uuid4().hex[:8]}"
        
        # Registrar transacción
        self.db.simdb.insert("transactions", {
            "transaction_id": txn_id,
            "portfolio_id": port_id,
            "symbol": symbol,
            "side": "BUY",
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "total_value": total_value,
            "commission": commission,
            "executed_at": datetime.now().isoformat(),
            "status": "FILLED",
            "notes": notes,
            "realized_pnl": 0,
        })
        
        # Actualizar o crear posición
        existing_position = self.db.simdb.select_one("positions", {
            "portfolio_id": port_id,
            "symbol": symbol,
        })
        
        if existing_position:
            # Calcular nuevo costo promedio
            old_qty = existing_position.get("quantity", 0)
            old_cost = existing_position.get("avg_cost", 0)
            new_qty = old_qty + quantity
            new_avg_cost = ((old_qty * old_cost) + total_value) / new_qty if new_qty > 0 else 0
            
            pos_id = existing_position.get("position_id")
            self.db.simdb.update("positions", str(pos_id), {
                "quantity": new_qty,
                "avg_cost": round(new_avg_cost, 4),
                "current_price": price,
                "updated_at": datetime.now().isoformat(),
            })
        else:
            # Nueva posición
            self.db.simdb.insert("positions", {
                "portfolio_id": port_id,
                "symbol": symbol,
                "quantity": quantity,
                "avg_cost": price,
                "current_price": price,
                "asset_type": "STOCK",
                "opened_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "notes": notes,
            })
        
        # Actualizar saldo del portafolio
        new_balance = portfolio.get("cash_balance", 0) - total_cost
        self.db.simdb.update("portfolios", port_id, {
            "cash_balance": round(new_balance, 2),
            "updated_at": datetime.now().isoformat(),
        })
        
        logger.info(f"COMPRA ejecutada: {quantity} {symbol} @ ${price} = ${total_value}")
        return txn_id

    def sell(self, symbol: str, quantity: float, price: float = None,
             order_type: str = "MARKET", notes: str = "",
             portfolio_id: str = None) -> Optional[str]:
        """
        Ejecuta una venta de activos.
        
        Args:
            symbol: Símbolo del activo
            quantity: Cantidad a vender
            price: Precio de venta (None = precio de mercado)
            order_type: Tipo de orden
            notes: Notas de la transacción
            portfolio_id: ID del portafolio (None = activo)
        
        Returns:
            ID de la transacción o None si falló
        """
        port_id = portfolio_id or self._active_portfolio_id
        if not port_id:
            return None
        
        # Verificar posición existente
        position = self.db.simdb.select_one("positions", {
            "portfolio_id": port_id,
            "symbol": symbol,
        })
        
        if not position:
            logger.error(f"No hay posición en {symbol}")
            return None
        
        if position.get("quantity", 0) < quantity:
            logger.error(f"Cantidad insuficiente: tiene {position.get('quantity')}, intenta vender {quantity}")
            return None
        
        # Obtener precio actual
        if price is None:
            market_data = self.db.simdb.select_one("market_data", {"symbol": symbol})
            if market_data:
                price = market_data.get("price", 0)
            else:
                return None
        
        total_value = round(quantity * price, 2)
        commission = round(total_value * 0.001, 2)
        net_proceeds = total_value - commission
        
        # Calcular PnL realizado
        avg_cost = position.get("avg_cost", 0)
        realized_pnl = round((price - avg_cost) * quantity - commission, 2)
        
        txn_id = f"txn-{uuid.uuid4().hex[:8]}"
        
        # Registrar transacción
        self.db.simdb.insert("transactions", {
            "transaction_id": txn_id,
            "portfolio_id": port_id,
            "symbol": symbol,
            "side": "SELL",
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "total_value": total_value,
            "commission": commission,
            "executed_at": datetime.now().isoformat(),
            "status": "FILLED",
            "notes": notes,
            "realized_pnl": realized_pnl,
        })
        
        # Actualizar posición
        new_qty = position.get("quantity", 0) - quantity
        pos_id = position.get("position_id")
        
        if new_qty <= 0:
            self.db.simdb.delete("positions", str(pos_id))
        else:
            self.db.simdb.update("positions", str(pos_id), {
                "quantity": new_qty,
                "current_price": price,
                "updated_at": datetime.now().isoformat(),
            })
        
        # Actualizar saldo
        portfolio = self.db.simdb.select_one("portfolios", {"portfolio_id": port_id})
        if portfolio:
            new_balance = portfolio.get("cash_balance", 0) + net_proceeds
            self.db.simdb.update("portfolios", port_id, {
                "cash_balance": round(new_balance, 2),
                "updated_at": datetime.now().isoformat(),
            })
        
        logger.info(f"VENTA ejecutada: {quantity} {symbol} @ ${price} = ${total_value} (PnL: ${realized_pnl})")
        return txn_id

    def update_positions_prices(self, market_data: Dict[str, Dict]) -> int:
        """
        Actualiza los precios actuales de todas las posiciones.
        
        Args:
            market_data: Datos de mercado actuales
        
        Returns:
            Número de posiciones actualizadas
        """
        updated = 0
        positions = self.db.simdb.select("positions")
        
        for pos in positions:
            symbol = pos.get("symbol")
            if symbol in market_data:
                price = market_data[symbol].get("price", 0)
                pos_id = pos.get("position_id")
                if pos_id and price > 0:
                    self.db.simdb.update("positions", str(pos_id), {
                        "current_price": price,
                        "updated_at": datetime.now().isoformat(),
                    })
                    updated += 1
        
        return updated

    def get_portfolio_positions(self, portfolio_id: str = None) -> List[Dict]:
        """
        Obtiene todas las posiciones de un portafolio con PnL calculado.
        
        Args:
            portfolio_id: ID del portafolio (None = activo)
        
        Returns:
            Lista de posiciones con métricas de rendimiento
        """
        port_id = portfolio_id or self._active_portfolio_id
        if not port_id:
            return []
        
        positions = self.db.simdb.select("positions", {"portfolio_id": port_id})
        
        enriched = []
        for pos in positions:
            qty = pos.get("quantity", 0)
            avg_cost = pos.get("avg_cost", 0)
            current_price = pos.get("current_price", 0)
            
            cost_basis = qty * avg_cost
            current_value = qty * current_price
            unrealized_pnl = current_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            enriched.append({
                **pos,
                "cost_basis": round(cost_basis, 2),
                "current_value": round(current_value, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
            })
        
        return enriched

    def get_portfolio_summary(self, portfolio_id: str = None) -> Dict:
        """
        Retorna un resumen completo del portafolio.
        
        Args:
            portfolio_id: ID del portafolio (None = activo)
        
        Returns:
            Diccionario con métricas del portafolio
        """
        port_id = portfolio_id or self._active_portfolio_id
        if not port_id:
            return {}
        
        return self.db.simdb.sp_get_portfolio_summary(port_id)

    def get_transaction_history(self, portfolio_id: str = None,
                                 symbol: str = None, limit: int = 50) -> List[Dict]:
        """
        Obtiene el historial de transacciones.
        
        Args:
            portfolio_id: ID del portafolio (None = activo)
            symbol: Filtrar por símbolo específico
            limit: Número máximo de transacciones
        
        Returns:
            Lista de transacciones ordenadas por fecha
        """
        port_id = portfolio_id or self._active_portfolio_id
        filters = {}
        if port_id:
            filters["portfolio_id"] = port_id
        if symbol:
            filters["symbol"] = symbol
        
        return self.db.simdb.select("transactions", filters=filters,
                                    order_by="-executed_at", limit=limit)

    def calculate_performance_metrics(self, portfolio_id: str = None) -> Dict:
        """
        Calcula métricas detalladas de rendimiento del portafolio.
        
        Args:
            portfolio_id: ID del portafolio
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        port_id = portfolio_id or self._active_portfolio_id
        if not port_id:
            return {}
        
        summary = self.db.simdb.sp_get_portfolio_summary(port_id)
        pnl_data = self.db.simdb.sp_calculate_portfolio_pnl(port_id)
        
        initial_capital = summary.get("initial_capital", 100000)
        total_value = summary.get("total_value", initial_capital)
        
        total_return = ((total_value - initial_capital) / initial_capital) * 100
        
        # Calcular volatilidad con datos históricos simulados
        returns = [random.gauss(0.0005, 0.015) for _ in range(252)]
        volatility = statistics.stdev(returns) * math.sqrt(252) * 100
        
        # Sharpe Ratio (asumiendo tasa libre de riesgo = 5%)
        risk_free_rate = 0.05
        sharpe = (total_return / 100 - risk_free_rate) / (volatility / 100) if volatility > 0 else 0
        
        # Max Drawdown simulado
        peak = initial_capital
        max_dd = 0
        current_val = initial_capital
        for r in returns:
            current_val *= (1 + r)
            if current_val > peak:
                peak = current_val
            dd = (peak - current_val) / peak
            if dd > max_dd:
                max_dd = dd
        
        return {
            "portfolio_id": port_id,
            "total_return": round(total_return, 2),
            "total_return_abs": round(total_value - initial_capital, 2),
            "volatility_annual": round(volatility, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown": round(max_dd * 100, 2),
            "var_95": round(statistics.quantile(returns, 0.05) * 100, 2),
            "realized_pnl": pnl_data.get("realized_pnl", 0),
            "unrealized_pnl": pnl_data.get("unrealized_pnl", 0),
            "total_commissions": pnl_data.get("total_commissions", 0),
            "num_transactions": summary.get("num_transactions", 0),
            "num_positions": summary.get("num_positions", 0),
        }


# ==============================================================================
# SECCIÓN 12: INTERFAZ GRÁFICA - COMPONENTES BASE
# ==============================================================================

class NotificationManager:
    """
    Gestor de notificaciones del sistema.
    Maneja alertas, mensajes y notificaciones al usuario.
    """

    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._history: List[Dict] = []
        self._max_history: int = 100
        self._callbacks: List[callable] = []

    def notify(self, message: str, notification_type: str = "INFO",
               title: str = None, duration: int = 5000) -> None:
        """
        Envía una notificación.
        
        Args:
            message: Mensaje de la notificación
            notification_type: Tipo (INFO, SUCCESS, WARNING, ERROR, ALERT)
            title: Título de la notificación
            duration: Duración en milisegundos
        """
        notification = {
            "id": str(uuid.uuid4()),
            "message": message,
            "type": notification_type,
            "title": title or notification_type,
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "read": False,
        }
        
        self._queue.put(notification)
        self._history.append(notification)
        
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        for callback in self._callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Error en callback de notificación: {e}")
        
        logger.info(f"Notificación [{notification_type}]: {message}")

    def register_callback(self, callback: callable) -> None:
        """Registra callback para notificaciones"""
        self._callbacks.append(callback)

    def get_pending(self) -> List[Dict]:
        """Obtiene notificaciones pendientes"""
        pending = []
        while not self._queue.empty():
            try:
                pending.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return pending

    def get_history(self, limit: int = 20) -> List[Dict]:
        """Obtiene historial de notificaciones"""
        return self._history[-limit:][::-1]

    def unread_count(self) -> int:
        """Retorna número de notificaciones no leídas"""
        return sum(1 for n in self._history if not n.get("read"))


class BaseWidget(ctk.CTkFrame):
    """
    Widget base para todos los componentes de la UI.
    Provee funcionalidades comunes: actualización, estado, estilo.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._is_loading = False
        self._last_update: Optional[datetime] = None
        self._update_callbacks: List[callable] = []

    def set_loading(self, loading: bool) -> None:
        """Establece el estado de carga del widget"""
        self._is_loading = loading
        self._on_loading_changed(loading)

    def _on_loading_changed(self, loading: bool) -> None:
        """Callback cuando cambia el estado de carga"""
        pass

    def register_update_callback(self, callback: callable) -> None:
        """Registra callback de actualización"""
        self._update_callbacks.append(callback)

    def trigger_update(self) -> None:
        """Dispara callbacks de actualización"""
        self._last_update = datetime.now()
        for callback in self._update_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error en update callback: {e}")


class MetricCard(BaseWidget):
    """
    Tarjeta de métrica individual para el dashboard.
    Muestra un valor, título y tendencia.
    """

    def __init__(self, parent, title: str, value: str = "--",
                 subtitle: str = "", color: str = "white",
                 icon: str = "📊", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(corner_radius=12)
        
        # Header con icono y título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 2))
        
        ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=18)).pack(side="left")
        ctk.CTkLabel(
            header, text=title.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=5)
        
        # Valor principal
        self._value_label = ctk.CTkLabel(
            self, text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color
        )
        self._value_label.pack(padx=12, pady=2, anchor="w")
        
        # Subtítulo
        self._subtitle_label = ctk.CTkLabel(
            self, text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self._subtitle_label.pack(padx=12, pady=(0, 10), anchor="w")

    def update_value(self, value: str, color: str = None, subtitle: str = None) -> None:
        """Actualiza el valor mostrado en la tarjeta"""
        self._value_label.configure(text=value)
        if color:
            self._value_label.configure(text_color=color)
        if subtitle is not None:
            self._subtitle_label.configure(text=subtitle)


class StatusBar(ctk.CTkFrame):
    """
    Barra de estado inferior de la aplicación.
    Muestra información del sistema, última actualización y estado del mercado.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=30, corner_radius=0, **kwargs)
        
        self._items: Dict[str, ctk.CTkLabel] = {}
        
        # Estado del mercado
        self._market_status = self._add_item("market", "🟢 Mercado: ABIERTO", "left")
        
        # Última actualización
        self._last_update = self._add_item("update", "⏱ Última act.: --", "left")
        
        # Conteo de tickers
        self._ticker_count = self._add_item("tickers", "📈 Tickers: 0", "left")
        
        # Separator
        ctk.CTkLabel(self, text="|", text_color=COLORS["text_muted"]).pack(side="left", padx=5)
        
        # Hora del sistema
        self._clock = self._add_item("clock", "🕐 --:--:--", "right")
        
        # Versión
        ctk.CTkLabel(
            self, text=f"{APP_NAME} v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        ).pack(side="right", padx=10)
        
        # Iniciar reloj
        self._update_clock()

    def _add_item(self, key: str, text: str, side: str) -> ctk.CTkLabel:
        """Añade un elemento a la barra de estado"""
        label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        label.pack(side=side, padx=8)
        self._items[key] = label
        return label

    def update_item(self, key: str, text: str, color: str = None) -> None:
        """Actualiza un elemento de la barra de estado"""
        if key in self._items:
            self._items[key].configure(text=text)
            if color:
                self._items[key].configure(text_color=color)

    def set_market_status(self, status: str, color: str = None) -> None:
        """Actualiza el estado del mercado"""
        icons = {
            "OPEN": "🟢", "CLOSED": "🔴",
            "PRE_MARKET": "🟡", "AFTER_HOURS": "🟠", "HOLIDAY": "⚫"
        }
        icon = icons.get(status, "⚪")
        self.update_item("market", f"{icon} Mercado: {status}", color)

    def set_last_update(self, dt: datetime = None) -> None:
        """Actualiza el timestamp de última actualización"""
        if dt is None:
            dt = datetime.now()
        self.update_item("update", f"⏱ Última act.: {dt.strftime('%H:%M:%S')}")

    def set_ticker_count(self, count: int) -> None:
        """Actualiza el conteo de tickers"""
        self.update_item("tickers", f"📈 Tickers: {count}")

    def _update_clock(self) -> None:
        """Actualiza el reloj en tiempo real"""
        now = datetime.now().strftime("%H:%M:%S")
        self.update_item("clock", f"🕐 {now}")
        self.after(1000, self._update_clock)


# ==============================================================================
# SECCIÓN 13: INTERFAZ GRÁFICA - PANEL DE COTIZACIONES
# ==============================================================================

class QuotesPanel(BaseWidget):
    """
    Panel principal de cotizaciones en tiempo real.
    Muestra la tabla de cotizaciones con actualizaciones automáticas.
    """

    def __init__(self, parent, db: DatabaseManager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db
        self._market_cache: Dict[str, Dict] = {}
        self._sort_column: str = "symbol"
        self._sort_reverse: bool = False
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura la interfaz del panel de cotizaciones"""
        # Header con controles
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            header, text="📊 Monitor de Cotizaciones",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Botones de acción
        self._btn_refresh = ctk.CTkButton(
            header, text="🔄 Actualizar",
            width=100, height=30,
            command=self._on_refresh_click
        )
        self._btn_refresh.pack(side="right", padx=5)
        
        ctk.CTkButton(
            header, text="📥 Exportar",
            width=100, height=30,
            fg_color=COLORS["accent_blue"],
            command=self._on_export_click
        ).pack(side="right", padx=5)
        
        # Barra de filtro
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(filter_frame, text="🔍 Filtrar:").pack(side="left")
        self._filter_entry = ctk.CTkEntry(
            filter_frame, width=200, placeholder_text="Buscar ticker..."
        )
        self._filter_entry.pack(side="left", padx=5)
        self._filter_entry.bind("<KeyRelease>", self._on_filter_change)
        
        # Selector de tipo de activo
        self._asset_filter = ctk.CTkComboBox(
            filter_frame, values=["Todos"] + list(ASSET_TYPES.values()),
            width=150, command=self._on_asset_filter_change
        )
        self._asset_filter.pack(side="left", padx=5)
        self._asset_filter.set("Todos")
        
        # Tabla de cotizaciones
        self._setup_table()

    def _setup_table(self) -> None:
        """Configura el TreeView de cotizaciones"""
        # Frame contenedor con scrollbar
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True)
        
        # Estilo del TreeView
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Quotes.Treeview",
            background="#1e1e2e",
            foreground="#e8e8e8",
            fieldbackground="#1e1e2e",
            rowheight=35,
            font=("Consolas", 10),
        )
        style.configure(
            "Quotes.Treeview.Heading",
            background="#2a2a4a",
            foreground="#a0a0c0",
            font=("Consolas", 10, "bold"),
        )
        style.map("Quotes.Treeview",
                  background=[("selected", "#1f538d")],
                  foreground=[("selected", "white")])
        
        # Definir columnas
        columns = [
            ("symbol", "TICKER", 80, "center"),
            ("price", "PRECIO", 100, "right"),
            ("change_pct", "CAMBIO %", 90, "right"),
            ("high", "MÁX", 90, "right"),
            ("low", "MÍN", 90, "right"),
            ("volume", "VOLUMEN", 110, "right"),
            ("market_cap", "CAPITALIZ.", 120, "right"),
            ("pe_ratio", "P/E", 70, "right"),
            ("beta", "BETA", 70, "right"),
            ("currency", "MONEDA", 70, "center"),
        ]
        
        col_ids = [c[0] for c in columns]
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=col_ids,
            show="headings",
            style="Quotes.Treeview",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Configurar columnas y cabeceras
        for col_id, col_text, col_width, col_anchor in columns:
            self.tree.heading(
                col_id, text=col_text,
                command=lambda c=col_id: self._sort_by_column(c)
            )
            self.tree.column(col_id, width=col_width, anchor=col_anchor, minwidth=50)
        
        # Tags para colores
        self.tree.tag_configure("up", foreground="#00c896")
        self.tree.tag_configure("down", foreground="#ff4757")
        self.tree.tag_configure("neutral", foreground="#a0a0a0")
        self.tree.tag_configure("crypto", foreground="#ffd700")
        self.tree.tag_configure("etf", foreground="#1e90ff")
        
        # Eventos
        self.tree.bind("<Double-1>", self._on_row_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="ns