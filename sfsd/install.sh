#!/bin/bash
# ============================================================================
# MARKET PRO TERMINAL v3.0 - Script de Instalación Automática
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       MARKET PRO TERMINAL v3.0 - Instalador Automático           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "✓ Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 no encontrado. Por favor, instala Python 3.9 o superior"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  → Python $PYTHON_VERSION encontrado"
echo ""

# Actualizar pip
echo "✓ Actualizando pip..."
python3 -m pip install --upgrade pip --quiet
echo "  → pip actualizado"
echo ""

# Instalar librerías
echo "✓ Instalando librerías necesarias..."
echo "  → Instalando customtkinter..."
pip install customtkinter --quiet

echo "  → Instalando yfinance..."
pip install yfinance --quiet

echo "  → Instalando pandas..."
pip install pandas --quiet

echo "  → Instalando matplotlib..."
pip install matplotlib --quiet

echo ""
echo "✓ Librerías instaladas correctamente"
echo ""

# Verificar instalación
echo "✓ Verificando instalación..."
python3 << 'EOF'
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

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Instalación completada exitosamente               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Para iniciar la aplicación, ejecuta:"
echo "  python3 market_pro.py"
echo ""
echo "Más información en: INSTRUCCIONES.md"
echo ""
