import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st

# Lire les données du fichier Excel
df = pd.read_excel("listeCoworking.xlsx")

# Titre de l'application
st.title("Carte des Espaces de Coworking à Paris")

# Créer une carte Folium centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Ajouter des marqueurs pour chaque espace de coworking
for idx, row in df.iterrows():
    if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<strong>{row['Nom']}</strong><br>{row['Adresse']}<br>{row['Téléphone']}<br><a href='{row['URL']}'>{row['URL']}</a>",
            tooltip=row['Nom']
        ).add_to(m)

# Afficher la carte dans Streamlit
folium_static(m)
