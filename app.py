import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de la Página ---
st.set_page_config(page_title="Radar Dual BTC/ETH", layout="wide")

# Estética oscura personalizada
st.markdown("""
    <style>
    .main { background-color: #111827; }
    .stMetric { background-color: #1e1e2e; padding: 15px; border-radius: 10px; color: white; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

MONEDA_LOCAL = "eur"

def obtener_datos_cripto(id_cripto):
    url_servidor = f"https://api.coingecko.com/api/v3/coins/{id_cripto}/market_chart"
    parametros_api = {'vs_currency': MONEDA_LOCAL, 'days': '365', 'interval': 'daily'}
    try:
        respuesta = requests.get(url_servidor, params=parametros_api)
        datos_json = respuesta.json()
        lista_precios = datos_json['prices']
        tabla_datos = pd.DataFrame(lista_precios, columns=['Fecha', 'Precio'])
        return tabla_datos
    except Exception as e:
        st.error(f"Error al obtener datos de {id_cripto}: {e}")
        return None

def calcular_niveles_tecnicos(precios_serie, umbral_distancia):
    lista_niveles = []
    # Ventana de 20 días para detectar más puntos clave como en tu VS Code
    for i in range(20, len(precios_serie) - 20):
        ventana = precios_serie[i-20 : i+21]
        precio_centro = precios_serie[i]
        # Detectamos tanto mínimos como máximos locales
        if precio_centro == min(ventana) or precio_centro == max(ventana):
            if not any(abs(precio_centro - n) < umbral_distancia for n in lista_niveles):
                lista_niveles.append(precio_centro)
    return sorted(lista_niveles)

def dibujar_grafico(datos_df, titulo, color_principal, umbral_nivel):
    precios = datos_df['Precio']
    precio_actual = precios.iloc[-1]
    indices = range(len(precios))
    
    fig, eje = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#111827')
    eje.set_facecolor('#1e1e2e')
    
    # 1. Gráfico de área
    eje.fill_between(indices, precios, color=color_principal, alpha=0.1)
    eje.plot(indices, precios, color=color_principal, linewidth=1.5)

    # 2. Línea de Precio Actual (Verde brillante)
    eje.axhline(y=precio_actual, color='#22c55e', linestyle='-', linewidth=2, zorder=5)
    eje.text(len(precios)//2, precio_actual, f" {round(precio_actual, 1)}€ ", 
             color='white', va='center', ha='center', fontweight='bold', 
             bbox=dict(facecolor='#22c55e', edgecolor='none', boxstyle='round,pad=0.3'))

    # 3. Niveles Técnicos (Amarillo para soportes y resistencias)
    niveles = calcular_niveles_tecnicos(precios, umbral_nivel)
    for nivel in niveles:
        # Dibujamos TODOS los niveles, no solo los de abajo
        eje.axhline(y=nivel, color='#facc15', linestyle='--', alpha=0.5, linewidth=0.8)
        eje.text(len(precios), nivel, f" {int(nivel)}", 
                 color='#facc15', va='center', fontsize=9, fontweight='bold')

    eje.set_title(titulo, color='white', fontsize=16, fontweight='bold', pad=25)
    
    # Ajustes de rejilla y ejes para que se vea profesional
    eje.tick_params(colors='gray', labelsize=8)
    eje.spines['top'].set_visible(False)
    eje.spines['right'].set_visible(False)
    eje.spines['left'].set_color('#374151')
    eje.spines['bottom'].set_color('#374151')
    eje.grid(True, axis='y', color='#374151', alpha=0.2)
    
    return fig

# --- Interfaz Principal ---
st.title("📊 Radar Pro BTC/ETH")

if st.button('🔄 ACTUALIZAR MERCADO'):
    col1, col2 = st.columns(2)
    
    # Bloque Bitcoin
    datos_btc = obtener_datos_cripto("bitcoin")
    if datos_btc is not None:
        precio_actual_btc = datos_btc['Precio'].iloc[-1]
        col1.metric("BITCOIN (BTC)", f"{round(precio_actual_btc, 2)} €")
        # Umbral ajustado para que salgan niveles parecidos a tu VS Code
        fig_btc = dibujar_grafico(datos_btc, "BITCOIN (BTC)", "#38bdf8", 4000)
        col1.pyplot(fig_btc)
        
    # Bloque Ethereum
    datos_eth = obtener_datos_cripto("ethereum")
    if datos_eth is not None:
        precio_actual_eth = datos_eth['Precio'].iloc[-1]
        col2.metric("ETHEREUM (ETH)", f"{round(precio_actual_eth, 2)} €")
        fig_eth = dibujar_grafico(datos_eth, "ETHEREUM (ETH)", "#a78bfa", 300)
        col2.pyplot(fig_eth)
else:
    st.info("Haz clic en el botón para cargar el radar con todos los niveles técnicos.")
