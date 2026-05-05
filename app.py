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

def calcular_soportes_tecnicos(precios_serie, umbral_distancia):
    lista_soportes = []
    # Usamos una ventana de 30 días para detectar mínimos locales
    for i in range(30, len(precios_serie) - 30):
        ventana = precios_serie[i-30 : i+31]
        precio_centro = precios_serie[i]
        if precio_centro == min(ventana):
            # Evitar soportes demasiado pegados entre sí
            if not any(abs(precio_centro - s) < umbral_distancia for s in lista_soportes):
                lista_soportes.append(precio_centro)
    return sorted(lista_soportes)

def dibujar_grafico(datos_df, titulo, color_principal, umbral_soporte):
    precios = datos_df['Precio']
    precio_actual = precios.iloc[-1]
    indices = range(len(precios))
    
    fig, eje = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#111827')
    eje.set_facecolor('#1e1e2e')
    
    # 1. Gráfico de área (Montañas)
    eje.fill_between(indices, precios, color=color_principal, alpha=0.1)
    eje.plot(indices, precios, color=color_principal, linewidth=1.5)

    # 2. Línea de Precio Actual (Verde)
    eje.axhline(y=precio_actual, color='#22c55e', linestyle='-', linewidth=2, zorder=5)
    eje.text(len(precios)//2, precio_actual, f" {round(precio_actual, 1)}€ ", 
             color='white', va='bottom', ha='center', fontweight='bold', 
             bbox=dict(facecolor='#22c55e', edgecolor='none', boxstyle='round,pad=0.3'))

    # 3. Niveles de Soporte (Amarillo)
    niveles = calcular_soportes_tecnicos(precios, umbral_soporte)
    for nivel in niveles:
        if nivel < precio_actual: # Solo mostrar soportes por debajo del precio
            eje.axhline(y=nivel, color='#facc15', linestyle='--', alpha=0.4, linewidth=1)
            eje.text(len(precios), nivel, f" {int(nivel)}", 
                     color='#facc15', va='center', fontsize=8, fontweight='bold')

    eje.set_title(titulo, color='white', fontsize=14, fontweight='bold', pad=20)
    eje.axis('off') # Limpieza total para que se vea bien en el móvil
    return fig

# --- Interfaz Principal ---
st.title("📊 Radar de Criptomonedas")

# Botón de actualización
if st.button('🔄 ACTUALIZAR PRECIOS AHORA'):
    col1, col2 = st.columns(2)
    
    # Bloque Bitcoin
    datos_btc = obtener_datos_cripto("bitcoin")
    if datos_btc is not None:
        precio_actual_btc = datos_btc['Precio'].iloc[-1]
        col1.metric("BITCOIN (BTC)", f"{round(precio_actual_btc, 2)} €")
        fig_btc = dibujar_grafico(datos_btc, "BITCOIN", "#38bdf8", 3500)
        col1.pyplot(fig_btc)
        
    # Bloque Ethereum
    datos_eth = obtener_datos_cripto("ethereum")
    if datos_eth is not None:
        precio_actual_eth = datos_eth['Precio'].iloc[-1]
        col2.metric("ETHEREUM (ETH)", f"{round(precio_actual_eth, 2)} €")
        fig_eth = dibujar_grafico(datos_eth, "ETHEREUM", "#a78bfa", 350)
        col2.pyplot(fig_eth)
else:
    st.info("Pulsa el botón superior para cargar los datos en vivo.")
