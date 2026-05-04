@echo off
REM ============================================================================
REM MARKET PRO TERMINAL v3.0 - Script de Instalación para Windows
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║       MARKET PRO TERMINAL v3.0 - Instalador para Windows          ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
echo ✓ Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python no encontrado. Por favor, instala Python 3.9 o superior
    echo.
    echo Descárgalo desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   → Python %PYTHON_VERSION% encontrado
echo.

REM Actualizar pip
echo ✓ Actualizando pip...
python -m pip install --upgrade pip --quiet
echo   → pip actualizado
echo.

REM Instalar librerías
echo ✓ Instalando librerías necesarias...
echo   → Instalando customtkinter...
pip install customtkinter --quiet

echo   → Instalando yfinance...
pip install yfinance --quiet

echo   → Instalando pandas...
pip install pandas --quiet

echo   → Instalando matplotlib...
pip install matplotlib --quiet

echo.
echo ✓ Librerías instaladas correctamente
echo.

REM Verificar instalación
echo ✓ Verificando instalación...
python << 'EOF'
try:
    import customtkinter
    import yfinance
    import pandas
    import matplotlib
    print("  ✅ Todas las librerías están disponibles")
except ImportError as e:
    print(f"  ❌ Error: {e}")
    exit(1)
EOF

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║              ✅ Instalación completada exitosamente               ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo Para iniciar la aplicación, ejecuta:
echo   python market_pro.py
echo.
echo Más información en: INSTRUCCIONES.md
echo.
pause
