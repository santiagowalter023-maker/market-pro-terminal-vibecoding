# 🚀 MARKET PRO TERMINAL v3.0 - GUÍA DE INSTALACIÓN

## 📋 Librerías Requeridas

El código requiere las siguientes librerías de Python:

```
customtkinter      (Interfaz gráfica moderna)
yfinance          (Datos financieros en tiempo real)
pandas            (Manipulación de datos)
matplotlib        (Gráficos)
```

Además utiliza librerías estándar de Python:
- tkinter (interfaz gráfica base)
- sqlite3 (base de datos)
- threading (operaciones asincrónicas)
- datetime, logging, csv, json, etc.

## 🔧 Instalación de Librerías

### Opción 1: Instalación Manual (Linux/Mac)
```bash
pip install customtkinter yfinance pandas matplotlib
```

### Opción 2: Instalación en Windows (con privilegios)
```bash
pip install --user customtkinter yfinance pandas matplotlib
```

### Opción 3: Instalación con apt (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-tk python3-pip
pip3 install customtkinter yfinance pandas matplotlib
```

### Opción 4: Instalación con Homebrew (macOS)
```bash
brew install python-tk
pip install customtkinter yfinance pandas matplotlib
```

## ✅ Verificar la Instalación

Para comprobar que todo está instalado correctamente:

```bash
python3 -c "import customtkinter; import yfinance; import pandas; import matplotlib; print('✅ Todas las librerías están instaladas!')"
```

## 🎯 Ejecutar la Aplicación

Una vez instaladas las librerías:

```bash
python3 market_pro.py
```

O simplemente:
```bash
python market_pro.py
```

## 📊 Características Principales

✨ **Monitor de Cotizaciones en Tiempo Real**
- Actualización automática de precios
- Soporte para múltiples tickers
- Gráficos interactivos

💾 **Base de Datos SQLite**
- Almacenamiento de datos históricos
- Gestión de portafolios
- Análisis técnico

📈 **Indicadores Técnicos**
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- MACD, RSI, Bollinger Bands
- Y muchos más...

🌍 **Soporte Multidivisas**
- USD, EUR, GBP, JPY, ARS, etc.
- Conversión automática de monedas

## 🐛 Solución de Problemas

### Error: "No module named 'customtkinter'"
```bash
pip install --upgrade customtkinter
```

### Error: "No module named 'tkinter'"
**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

**Windows:** Instalar Python desde python.org con la opción "tcl/tk and IDLE"

### Error de conexión a yfinance
- Verifica tu conexión a Internet
- Los datos pueden no estar disponibles en ciertos horarios
- Intenta con otros tickers

### La ventana no aparece
- Asegúrate de tener un servidor X11 (Linux con interfaz gráfica)
- En WSL2, necesitas XServer (VcXsrv o similar)

## 📦 Requisitos del Sistema

- **Python:** 3.9 o superior
- **RAM:** Mínimo 512 MB (recomendado 2 GB+)
- **Almacenamiento:** 100 MB libre
- **Conexión:** Internet (para descargar datos financieros)

## 🔐 Archivo de Base de Datos

La aplicación crea automáticamente `market_data.db` en el mismo directorio.
Este archivo almacena:
- Datos históricos de cotizaciones
- Información de portafolios
- Órdenes y transacciones

## 📝 Notas Importantes

1. Los datos se descargan de Yahoo Finance (yfinance)
2. La aplicación requiere conexión a Internet
3. Algunos datos pueden tener retraso de 15 minutos
4. Las criptomonedas (BTC-USD, ETH-USD) están soportadas
5. Los tickers deben existir en Yahoo Finance

## 🎨 Personalización

Puedes editar las constantes en el código:

```python
# Colores del tema
COLORS = { ... }

# Tickers predeterminados
DEFAULT_TICKERS = ["AAPL", "MSFT", ...]

# Intervalo de actualización
DEFAULT_REFRESH_INTERVAL = 30  # segundos
```

## 📞 Soporte

Si tienes problemas:
1. Verifica que todas las librerías estén instaladas
2. Comprueba tu versión de Python (debe ser 3.9+)
3. Intenta ejecutar el código nuevamente
4. Revisa los logs en `market_pro.log`

---

**Versión:** 3.0.0  
**Autor:** Market Pro Team  
**Licencia:** Professional
