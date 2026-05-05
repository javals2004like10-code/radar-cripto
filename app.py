import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de la Página ---
st.set_page_config(page_title="Radar Dual BTC/ETH", layout="wide")

# Estética oscura y ajuste para móviles
st.markdown("""
    <style>
    .main { background-color: #111827; }
    .stMetric { background-color: #1e1e2e; padding: 15px; border-radius: 10px; color: white; border: 1px solid #374151; }
    /* Forzar que las columnas se apilen en pantallas pequeñas */
    [data-testid="column"] { min-width: 300px ! width: 100% !important; }
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
    for i in range(20, len(precios_serie) - 20):
        ventana = precios_serie[i-20 : i+21]
        precio_centro = precios_serie[i]
        if precio_centro == min(ventana) or precio_centro == max(ventana):
            if not any(abs(precio_centro - n) < umbral_distancia for n in lista_niveles):
                lista_niveles.append(precio_centro)
    return sorted(lista_niveles)

def dibujar_grafico(datos_df, titulo, color_principal, umbral_nivel):
    precios = datos_df['Precio']
    precio_actual = precios.iloc[-1]
    indices = range(len(precios))
    
    # Aumentamos el alto (8) para que se vea más grande
    fig, eje = plt.subplots(figsize=(10, 8)) 
    fig.patch.set_facecolor('#111827')
    eje.set_facecolor('#1e1e2e')
    
    eje.fill_between(indices, precios, color=color_principal, alpha=0.1)
    eje.plot(indices, precios, color=color_principal, linewidth=2)

    eje.axhline(y=precio_actual, color='#22c55e', linestyle='-', linewidth=2.5, zorder=5)
    eje.text(len(precios)//2, precio_actual, f" {round(precio_actual, 1)}€ ", 
             color='white', va='center', ha='center', fontweight='bold', 
             bbox=dict(facecolor='#22c55e', edgecolor='none', boxstyle='round,pad=0.5'))

    niveles = calcular_niveles_tecnicos(precios, umbral_nivel)
    for nivel in niveles:
        eje.axhline(y=nivel, color='#facc15', linestyle='--', alpha=0.5, linewidth=1)
        eje.text(len(precios), nivel, f" {int(nivel)}", 
                 color='#facc15', va='center', fontsize=10, fontweight='bold')

    eje.set_title(titulo, color='white', fontsize=18, fontweight='bold', pad=30)
    eje.tick_params(colors='gray', labelsize=10)
    eje.spines['top'].set_visible(False)
    eje.spines['right'].set_visible(False)
    eje.grid(True, axis='y', color='#374151', alpha=0.3)
    
    return fig

# --- Interfaz Principal ---
st.title("📊 Radar Pro BTC/ETH")

if st.button('🔄 ACTUALIZAR MERCADO'):
    # En móvil, Streamlit pondrá automáticamente una columna debajo de otra
    col1, col2 = st.columns(2)
    
    datos_btc = obtener_datos_cripto("bitcoin")
    if datos_btc is not None:
        with col1:
            st.metric("BITCOIN (BTC)", f"{round(datos_btc['Precio'].iloc[-1], 2)} €")
            fig_btc = dibujar_grafico(datos_btc, "BITCOIN (BTC)", "#38bdf8", 4000)
            st.pyplot(fig_btc, use_container_width=True) # Adaptar al ancho disponible
        
    datos_eth = obtener_datos_cripto("ethereum")
    if datos_eth is not None:
        with col2:
            st.metric("ETHEREUM (ETH)", f"{round(datos_eth['Precio'].iloc[-1], 2)} €")
            fig_eth = dibujar_grafico(datos_eth, "ETHEREUM (ETH)", "#a78bfa", 300)
            st.pyplot(fig_eth, use_container_width=True) # Adaptar al ancho disponible
else:
    st.info("Haz clic para cargar el radar.")
