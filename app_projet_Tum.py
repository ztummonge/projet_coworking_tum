import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st

st.title("Coworkings à Paris")

@st.cache_data
def load_data():
    df = pd.read_excel("coworkings_paris.xlsx")
    return df

df = load_data()

st.write(df.columns)  # Ajoute cette ligne pour afficher les colonnes disponibles

# Centre de la carte sur Paris
map_center = [48.8566, 2.3522]  # Coordonnées de Paris
coworking_map = folium.Map(location=map_center, zoom_start=12)

# Ajout des marqueurs pour chaque coworking
for index, row in df.iterrows():
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Nom du Coworking']}<br>{row['Adresse']}",
                tooltip=row['Nom du Coworking']
            ).add_to(coworking_map)

# Affichage de la carte dans l'application Streamlit
folium_static(coworking_map)

# Affichage du DataFrame des informations des coworkings
st.dataframe(df)
