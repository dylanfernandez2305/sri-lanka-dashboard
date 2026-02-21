#!/bin/bash

echo ""
echo "🌴 Sri Lanka Explorer Dashboard"
echo "================================"

# Vérifie si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé. Installe Python sur https://python.org"
    exit 1
fi

# Vérifie si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 non trouvé."
    exit 1
fi

# Vérifie si streamlit est déjà installé
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Installation des dépendances (première fois uniquement)..."
    pip3 install streamlit plotly pandas folium streamlit-folium -q
    echo "✅ Dépendances installées !"
else
    echo "✅ Dépendances déjà installées"
fi

echo ""
echo "🚀 Lancement du dashboard..."
echo "👉 Ouvre http://localhost:8501 dans ton navigateur"
echo "   (Ctrl+C pour arrêter)"
echo ""

streamlit run sri_lanka_dashboard.py --server.headless false
